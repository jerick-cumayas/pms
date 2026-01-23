from odoo import fields, models


class IncidentDetails(models.Model):
    _name = "incident.details"
    _description = "Incident Details"


class CCTVRequestForm(models.Model):
    _name = "forms.cctv"
    _description = "CCTV Request Form"
    _inherit = ["form.base"]

    requestor_id = fields.Many2one(
        "res.partner", string="Name of Requestor", required=True
    )
    incident_datetime = fields.Date(string="Incident Date")
    location = fields.Char(string="Location")
    camera_number = fields.Char(string="Camera number")
    purpose = fields.Text(string="Purpose of Request")
    description = fields.Text(string="Description of Incident")

    review_date = fields.Date(string="Review Date")
    footage_provided = fields.Date(string="Footage Provided")
    remarks = fields.Text(string="Comments/Remarks")
