from odoo import models, fields

class Unit(models.Model):
    _name = 'building.unit'
    _description = 'Unit'
    
    building_id = fields.Many2one(
        'building',
        string="Building",
        ondelete='cascade'
    )
    unit_no = fields.Char(
        string="Unit No."
    )