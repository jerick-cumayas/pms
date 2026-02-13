from odoo import fields, models


class PMSVehicle(models.Model):
    _name = "pms.vehicle"
    _description = "Vehicle"
    _rec_name = "plate_no"

    plate_no = fields.Char(string="Plate No.", required=True)
    vehicle_type = fields.Char(string="Vehicle Type", required=True)
    color = fields.Selection([], string="Color", required=True)
    owner_id = fields.Many2one("res.partner", string="Owner")

    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("plate_no_unique", "unique(plate_no)", "Plate number must be unique."),
    ]
