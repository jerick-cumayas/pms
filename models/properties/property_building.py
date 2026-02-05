from odoo import fields, models


class Building(models.Model):
    _name = "property.building"
    _description = "Building"

    name = fields.Char(string="Name", required=True)
    unit_ids = fields.One2many("property.unit", "building_id", string="Units")
