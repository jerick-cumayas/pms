from odoo import api, fields, models


class IncidentDetails(models.Model):
    _name = "incident.details"
    _description = "Incident Details"


class CCTVRequestForm(models.Model):
    _name = "forms.cctv"
    _description = "CCTV Request Form"
    _rec_name = "purpose"
    _inherit = ["form.base"]

    requestor_id = fields.Many2one(
        "res.partner", string="Name of Requestor", required=True
    )
    incident_datetime = fields.Date(string="Incident Date")
    location = fields.Char(string="Location")
    camera_number = fields.Char(string="Camera number")
    purpose = fields.Text(string="Purpose of Request")
    description = fields.Text(string="Description of Incident")

    footage_provided = fields.Date(string="Footage Provided")
    remarks = fields.Text(string="Comments/Remarks")

    reviewer_ids = fields.One2many(
        "form.reviewer",
        "form_id",
        string="Reviewers",
        compute="_compute_reviewers",
        store=True,
    )

    def _compute_reviewers(self):
        for rec in self:
            rec.reviewer_ids = self.env["form.reviewer"].search(
                [
                    ("form_model", "=", rec._name),
                    ("form_id", "=", rec.id),
                ]
            )
