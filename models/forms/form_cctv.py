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

    footage_provided = fields.Date(string="Footage Provided")
    remarks = fields.Text(string="Comments/Remarks")

    # reject_date = fields.Datetime(string="Reject Date")
    # rejected_by = fields.Many2one("res.users", string="Rejected By", copy=False)

    # review_date = fields.Date(string="Review Date")
    # review_by = fields.Many2one("res.users", string="Reviewed By", copy=False)

    # completed_date = fields.Datetime(string="Completed Date")
    # completed_by = fields.Many2one("res.users", string="Completed By", copy=False)

    # def action_reject(self):
    #     self._check_transition(
    #         "rejected",
    #         "Request can only be rejected if it is not Under Review or Completed.",
    #     )
    #     self.write(
    #         {
    #             "state": "rejected",
    #             "reject_date": fields.Datetime.now(),
    #             "rejected_by": self.env.user.id,
    #         }
    #     )

    # def action_under_review(self):
    #     self._check_transition(
    #         "under_review", "Request can only be Under Review if it has been Submitted."
    #     )
    #     self.write(
    #         {
    #             "state": "under_review",
    #             "review_date": fields.Datetime.now(),
    #             "review_by": self.env.user.id,
    #         }
    #     )

    # def action_complete(self):
    #     self._check_transition(
    #         "completed", "Request can only be Completed after Under Review."
    #     )
    #     self.write(
    #         {
    #             "state": "completed",
    #             "completed_date": fields.Datetime.now(),
    #             "completed_by": self.env.user.id,
    #         }
    #     )
