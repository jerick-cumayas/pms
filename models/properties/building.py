from odoo import models, fields

class Building(models.Model):
    _name = 'building'
    _description = 'Building'
    
    name = fields.Char(
        string = 'Name'
    )
    unit_ids = fields.One2many(
        'building.unit',
        'building_id',
        string = 'Units'
    )