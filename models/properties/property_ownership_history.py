from odoo import fields, models


class PropertyOwnershipHistory(models.Model):
    _name = "property.ownership.history"
    _description = "Property Ownership History"
    _order = "start_date desc"

    unit_id = fields.Many2one("property.unit", required=True)
    owner_id = fields.Many2one("res.partner", required=True)

    start_date = fields.Date(required=True)
    end_date = fields.Date()
