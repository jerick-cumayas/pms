from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    property_unit_id = fields.Many2one(
        "property.unit", string="Property Unit", help="Unit being sold"
    )


class PropertyUnit(models.Model):
    _name = "property.unit"

    name = fields.Char(required=True)
    building_id = fields.Many2one(
        "property.building", required=True, ondelete="restrict"
    )

    ownership_ids = fields.One2many("property.ownership", "unit_id")
    lease_ids = fields.One2many("property.lease", "unit_id")

    current_owner_ids = fields.Many2many(
        "res.partner", compute="_compute_current_owners"
    )
    current_tenant_id = fields.Many2one(
        "res.partner", compute="_compute_current_tenant"
    )

    state = fields.Selection(
        [
            ("available", "Available"),
            ("quotation", "Quotation"),
            ("pending_invoice", "Invoice Sent"),
            ("pending_payment", "Pending Payment"),
            ("sold", "Sold"),
            ("rented", "Rented"),
        ],
        string="Status",
        store=True,
        default="available",
    )

    price = fields.Float(
        string="Default Price", help="Suggested sale price for the unit"
    )

    @api.depends(
        "ownership_ids.start_date",
        "ownership_ids.end_date",
        "lease_ids.start_date",
        "lease_ids.end_date",
    )
    def _compute_state(self):
        today = fields.Date.today()
        SaleOrder = self.env["sale.order"]

        for unit in self:
            # Check active lease first
            active_lease = unit.lease_ids.filtered(
                lambda l: l.start_date <= today <= l.end_date
            )
            if active_lease:
                unit.state = "rented"
                continue

            # Check sale order lines
            sale_order = SaleOrder.search(
                [("property_unit_id", "=", unit.id), ("state", "!=", "cancel")]
            )
            if sale_order:
                sale = sale_order[0]
                if sale.state == "draft":
                    unit.state = "quotation"
                elif sale.state == "sale":  # confirmed
                    invoices = sale.invoice_ids.filtered(
                        lambda inv: inv.state == "posted"
                    )
                    if not invoices:
                        unit.state = "pending_invoice"
                    elif any(inv.payment_state != "paid" for inv in invoices):
                        unit.state = "pending_payment"
                    else:
                        unit.state = "sold"
                continue

            # Check ownership history
            active_owner = unit.ownership_ids.filtered(
                lambda o: o.start_date <= today
                and (not o.end_date or o.end_date >= today)
            )
            if active_owner:
                unit.state = "sold"
            else:
                unit.state = "available"

    def _compute_current_owners(self):
        today = fields.Date.today()
        for unit in self:
            unit.current_owner_ids = unit.ownership_ids.filtered(
                lambda o: o.start_date <= today
                and (not o.end_date or o.end_date >= today)
            ).mapped("owner_id")

    def _get_unit_purchase_product(self):
        """Helper to get or create the generic 'Unit Purchase' product"""
        Product = self.env["product.product"]
        product = Product.search([("name", "=", "Unit Purchase")], limit=1)
        if not product:
            product = Product.create(
                {
                    "name": "Unit Purchase",
                    "type": "service",  # not stockable
                    "sale_ok": True,
                    "purchase_ok": False,
                    "list_price": 0.0,
                }
            )
        return product

    def _compute_current_tenant(self):
        today = fields.Date.today()
        for unit in self:
            lease = unit.lease_ids.filtered(
                lambda l: l.start_date <= today and l.end_date >= today
            )[:1]
            unit.current_tenant_id = lease.tenant_id

    def action_create_sale_quotation(self):
        self.ensure_one()

        if self.state != "available":
            raise UserError("This unit is not available for quotation.")

        return {
            "type": "ir.actions.act_window",
            "name": "Create Sale Quotation",
            "res_model": "property.unit.sale.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_unit_id": self.id,
                "default_price": self.price,
            },
        }

    def action_open_ownership_wizard(self):
        """Open a wizard to assign an owner"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Assign Owner",
            "res_model": "property.ownership.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_unit_id": self.id,
                "default_start_date": fields.Date.today(),
            },
        }

    def action_open_tenant_wizard(self):
        """Open a wizard to assign a tenant"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Assign Tenant",
            "res_model": "property.tenant.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_unit_id": self.id,
                "default_start_date": fields.Date.today(),
            },
        }


class PropertyUnitSaleWizard(models.TransientModel):
    _name = "property.unit.sale.wizard"
    _description = "Create Sale Quotation for Property Unit"

    unit_id = fields.Many2one("property.unit", required=True, readonly=True)
    partner_id = fields.Many2one(
        "res.partner",
        required=True,
        string="Customer",
        domain=[("is_company", "=", False)],
    )
    price = fields.Float(string="Sale Price")

    def action_confirm(self):
        self.ensure_one()

        unit = self.unit_id
        product = unit._get_unit_purchase_product()

        sale_order = self.env["sale.order"].create(
            {"partner_id": self.partner_id.id, "property_unit_id": self.unit_id.id}
        )

        self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": product.id,
                "product_uom_qty": 1,
                "price_unit": self.price or unit.price,
                "name": f"Purchase of {unit.name}",
            }
        )

        unit.state = "quotation"

        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "view_mode": "form",
            "res_id": sale_order.id,
            "target": "current",
        }


class PropertyOwnershipWizard(models.TransientModel):
    _name = "property.ownership.wizard"
    _description = "Assign Property Ownership"

    unit_id = fields.Many2one("property.unit", required=True, string="Unit")
    owner_id = fields.Many2one(
        "res.partner",
        required=True,
        string="Owner",
        domain=[("is_company", "=", False)],
    )
    start_date = fields.Date(default=fields.Date.today)
    end_date = fields.Date()

    def action_assign_owner(self):
        self.ensure_one()
        unit = self.unit_id

        # End any current ownership
        current_owner = unit.ownership_ids.filtered(lambda o: not o.end_date)
        if current_owner:
            current_owner.end_date = self.start_date - timedelta(days=1)

        # Create new ownership record
        self.env["property.ownership"].create(
            {
                "unit_id": unit.id,
                "owner_id": self.owner_id.id,
                "start_date": self.start_date,
                "end_date": self.end_date,
            }
        )

        # Update the unit state
        unit.state = "sold"


class PropertyTenantWizard(models.TransientModel):
    _name = "property.tenant.wizard"
    _description = "Assign Property Tenant"

    unit_id = fields.Many2one("property.unit", required=True, string="Unit")
    tenant_id = fields.Many2one(
        "res.partner",
        required=True,
        string="Tenant",
        domain=[("is_company", "=", False)],
    )
    start_date = fields.Date(default=fields.Date.today)
    end_date = fields.Date()

    def action_assign_tenant(self):
        self.ensure_one()
        unit = self.unit_id

        # End current lease if overlapping
        current_lease = unit.lease_ids.filtered(
            lambda l: not l.end_date or l.end_date >= self.start_date
        )
        if current_lease:
            current_lease.end_date = self.start_date - timedelta(days=1)

        # Create new lease record
        self.env["property.lease"].create(
            {
                "unit_id": unit.id,
                "tenant_id": self.tenant_id.id,
                "start_date": self.start_date,
                "end_date": self.end_date,
            }
        )

        # Update unit state
        unit.state = "rented"


class DateRangeMixin(models.AbstractModel):
    _name = "date.range.mixin"
    _description = "Mixin to validate start/end dates"

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        today = fields.Date.today()
        for record in self:
            if record.start_date > today:
                raise ValidationError(
                    f"{self._description} start date cannot be in the future."
                )
            if record.end_date and record.start_date > record.end_date:
                raise ValidationError(
                    f"{self._description} start date must be before end date."
                )


class PropertyOwnership(models.Model, DateRangeMixin):
    _name = "property.ownership"

    unit_id = fields.Many2one("property.unit", required=True)
    owner_id = fields.Many2one(
        "res.partner",
        required=True,
        string="Owner",
        domain=[("is_company", "=", False)],  # only individuals
    )

    start_date = fields.Date(required=True)
    end_date = fields.Date()


class PropertyLease(models.Model, DateRangeMixin):
    _name = "property.lease"

    unit_id = fields.Many2one("property.unit", required=True)
    tenant_id = fields.Many2one(
        "res.partner",
        required=True,
        string="Tenant",
        domain=[("is_company", "=", False)],  # only individuals
    )

    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
