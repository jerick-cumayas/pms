from odoo import api, fields, models


class PropertyOccupancyHistoryAbstract(models.AbstractModel):
    _name = "property.occupancy.history"
    _description = "Property Occupancy History Abstract (Owner / Tenant)"
    _order = "start_date desc"

    unit_id = fields.Many2one(
        "property.unit",
        required=True,
        string="Unit",
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

    start_date = fields.Date(
        required=True,
        string="Start Date",
    )

    end_date = fields.Date(
        string="End Date",
    )


class PropertyOwnershipHistory(models.Model):
    _name = "property.ownership.history"
    _description = "Property Ownership History"
    _inherit = "property.occupancy.history"


class PropertyTenancyHistory(models.Model):
    _name = "property.tenancy.history"
    _description = "Property Tenancy History"
    _inherit = "property.occupancy.history"
