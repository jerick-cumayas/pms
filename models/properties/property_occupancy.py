from odoo import fields, models


class PropertyOccupancyAbstract(models.AbstractModel):
    _name = "property.occupancy"
    _description = "Property Occupancy Abstract (Owner / Tenant)"
    _rec_name = "main_partner_id"

    unit_id = fields.Many2one(
        "property.unit",
        required=True,
        ondelete="cascade",
    )

    main_partner_id = fields.Many2one(
        "res.partner",
        required=True,
        domain=[("is_company", "=", False)],
        string="Main Contact",
    )

    member_ids = fields.Many2many(
        "res.partner",
        domain=[("is_company", "=", False)],
        string="Members",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("pending_transfer", "Pending Transfer"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
    )

    start_date = fields.Date(
        required=True,
        default=fields.Date.today,
    )

    # This name_get will apply to all children
    def name_get(self):
        result = []
        for record in self:
            main_name = record.main_partner_id.name if record.main_partner_id else ""
            unit_name = record.unit_id.name if record.unit_id else ""
            display_name = f"{main_name} - {unit_name}" if main_name else unit_name
            result.append((record.id, display_name))
        return result


class PropertyOwnership(models.Model):
    _name = "property.ownership"
    _description = "Current Property Ownership"
    _inherit = "property.occupancy"


class PropertyTenancy(models.Model):
    _name = "property.tenancy"
    _description = "Current Property Tenant"
    _inherit = "property.occupancy"
