from odoo import api, fields, models

from .form_constants import STATE_COMPLETED, STATE_INVOICE, STATE_QUOTATION


class FormQuotationAbstract(models.AbstractModel):
    _name = "form.quotation.abstract"
    _description = "Form Quotation Mixin"

    quotation_id = fields.Many2one(
        "sale.order",
        string="Quotation",
        readonly=True,
        copy=False,
    )

    invoice_ids = fields.Many2many(
        related="quotation_id.invoice_ids",
        string="Invoices",
        readonly=True,
    )

    invoice_created = fields.Boolean(
        compute="_compute_invoice_created",
        store=True,
    )

    invoice_paid = fields.Boolean(
        compute="_compute_invoice_status",
        store=True,
    )

    can_quotation = fields.Boolean(
        compute="_compute_quotation_permissions",
        store=False,
    )

    can_invoice = fields.Boolean(
        compute="_compute_quotation_permissions",
        store=False,
    )

    # ------------------------------
    # PERMISSIONS
    # ------------------------------
    @api.depends("state", "reviewer_ids.state", "quotation_id")
    def _compute_quotation_permissions(self):
        for rec in self:
            transitions = rec.STATE_TRANSITIONS.get(rec.state, [])

            self.write(
                {
                    "can_quotation": (
                        STATE_QUOTATION in transitions and not rec.review_incomplete
                    ),
                    "can_invoice": (
                        rec.state == STATE_QUOTATION
                        and STATE_INVOICE in transitions
                        and bool(rec.quotation_id)
                    ),
                }
            )

    @api.depends("invoice_ids.payment_state", "invoice_ids.state")
    def _compute_invoice_status(self):
        for rec in self:
            invoices = rec.invoice_ids

            rec.invoice_created = any(inv.state == "posted" for inv in invoices)
            rec.invoice_paid = any(inv.payment_state == "paid" for inv in invoices)

            if rec.invoice_created and rec.state == STATE_QUOTATION:
                self.write({"state": STATE_INVOICE})
                # rec.state = STATE_INVOICE

            if rec.invoice_paid and rec.state == STATE_INVOICE:
                self.write({"state": STATE_COMPLETED})
                # rec.state = STATE_COMPLETED

    # ------------------------------
    # EXTENSION HOOKS
    # ------------------------------
    def _get_quotation_product(self):
        """Override in child model if needed"""
        return self._get_or_create_product(
            name="Generic Service",
            type="service",
        )

    def _prepare_quotation_vals(self, product):
        """Override if form needs custom logic"""
        self.ensure_one()

        return {
            "partner_id": self.requestor_id.id,
            "company_id": self.env.company.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "product_uom_qty": 1,
                    },
                )
            ],
        }

    def _prepare_quotation_line_vals(self, product, quantity=1):
        self.ensure_one()

        return {
            "product_id": product.id,
            "product_uom_qty": quantity,
        }

    def _get_or_create_product(self, name, list_price=1.0, type="service"):
        """
        Get or create a product by name.

        :param name: Product name
        :param list_price: Default sale price
        :param type: product type (service, consumable, etc.)
        """
        Product = self.env["product.product"]

        product = Product.search(
            [
                ("name", "=", name),
            ],
            limit=1,
        )

        if not product:
            product = Product.create(
                {
                    "name": name,
                    "type": type,
                    "list_price": list_price,
                }
            )

        return product

    # ------------------------------
    # ACTIONS
    # ------------------------------
    def action_quotation(self):
        self.ensure_one()
        self.action_set_state(STATE_QUOTATION)

    def action_invoice(self):
        self.ensure_one()
        self.action_set_state(STATE_INVOICE)

    def action_send_quotation(self):
        self.ensure_one()

        product = self._get_quotation_product()

        quotation_vals = self._prepare_quotation_vals(product)
        quotation = self.env["sale.order"].create(quotation_vals)

        self.write({"quotation_id": quotation.id})

        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "res_id": quotation.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_open_quotation(self):
        self.ensure_one()

        if not self.quotation_id:
            return False

        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "res_id": self.quotation_id.id,
            "view_mode": "form",
            "target": "current",
        }
