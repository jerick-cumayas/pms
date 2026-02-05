from odoo import fields, models

from .form_constants import STATE_COMPLETED, STATE_IN_PROGRESS, STATE_PENDING


class AssignReviewersWizard(models.TransientModel):
    _name = "assign.reviewers.wizard"
    _description = "Wizard to assign reviewers to a form"

    reviewer_id = fields.Many2one("res.users", string="Reviewer", required=True)
    review_for = fields.Char(string="Review For")
    review_date = fields.Datetime(string="Review Date", default=fields.Date.today())
    state = fields.Selection(
        [
            (STATE_PENDING, "Pending"),
            (STATE_IN_PROGRESS, "In Progress"),
            (STATE_COMPLETED, "Completed"),
        ],
        string="Status",
        default=STATE_PENDING,
        required=True,
    )
    remarks = fields.Text(string="Remarks")

    # Fields to know which form to assign this reviewer to
    form_model = fields.Char(required=True)
    form_id = fields.Integer(required=True)

    def action_assign_reviewer(self):
        """Create a reviewer record for the specified form"""
        print(self.form_model)
        print(self.form_id)
        self.env["form.reviewer"].create(
            {
                "reviewer_id": self.reviewer_id.id,
                "review_date": self.review_date,
                "review_for": self.review_for,
                "state": self.state,
                "remarks": self.remarks,
                "form_model": self.form_model,
                "form_id": self.form_id,
            }
        )
