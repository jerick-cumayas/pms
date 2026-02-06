from odoo import api, fields, models


class ConcernSlipForm(models.Model):
    _name = "forms.concern_slip"
    _description = "Concern Slip Form"
    _inherit = ["form.base"]
    _order = "create_date desc"

    requester_id = fields.Many2one(
        "res.partner",
        string="Requester",
        required=True,
    )
    subject = fields.Char(
        string="Subject",
        required=True,
    )
    description = fields.Text(
        string="Concern Details",
        required=True,
    )
    concern_type = fields.Selection(
        [
            ("complaint", "Complaint"),
            ("request", "Request"),
            ("suggestion", "Suggestion"),
            ("incident", "Incident"),
        ],
        string="Concern Type",
        required=True,
    )
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "concern_slip_attachment_rel",
        "concern_id",
        "attachment_id",
        string="Attachments",
    )
    reviewer_ids = fields.One2many(
        "form.reviewer",
        "form_id",
        string="Reviewers",
        compute="_compute_reviewers",
        store=True,
    )
