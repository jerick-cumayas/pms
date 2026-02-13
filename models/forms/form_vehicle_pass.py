import base64

from odoo import api, fields, models

from .form_constants import (
    STATE_COMPLETED,
    STATE_INVOICE,
)


class VehiclePassForm(models.Model):
    _name = "forms.vehicle_pass"
    _description = "Vehicle Pass Form"
    _inherit = ["form.base", "form.quotation.abstract"]

    application_no = fields.Char(string="Application No.")
    application_type = fields.Selection(
        [("new", "New"), ("renewal", "Renewal")],
        string="Type of Application",
    )
    vehicle_ownership = fields.Selection(
        [("owned", "Owned"), ("company", "Company")], string="Ownership of Vehicle"
    )
    type = fields.Char(string="Vehicle Type")
    color = fields.Selection(
        [
            ("red", "Red"),
            ("orange", "Orange"),
            ("yellow", "Yellow"),
            ("green", "Green"),
            ("blue", "Blue"),
            ("purple", "Purple"),
            ("black", "Black"),
            ("white", "White"),
            ("gray", "Gray"),
        ],
        string="Color",
    )
    plate_no = fields.Char(string="Plate No")
    reviewer_ids = fields.One2many(
        "form.reviewer",
        "form_id",
        string="Reviewers",
        compute="_compute_reviewers",
        store=True,
    )
    attachment_ids = fields.One2many(
        "ir.attachment",
        "res_id",
        string="Attachments",
        domain=lambda self: [("res_model", "=", self._name)],
    )

    @api.depends("state", "reviewer_ids.state")
    def _compute_can_complete(self):
        for rec in self:
            transitions = rec.STATE_TRANSITIONS.get(rec.state, [])
            rec.can_complete = (
                rec.state == STATE_INVOICE
                and STATE_COMPLETED in transitions
                and bool(rec.reviewer_ids)
                and not rec.review_incomplete
            )

    def action_cancel(self):
        super().action_cancel()

        for rec in self:
            if rec.quotation_id:
                quotation = rec.quotation_id

                # Cancel quotation first
                if quotation.state != "cancel":
                    quotation.action_cancel()

                # Delete it
                quotation.unlink()

                rec.quotation_id = False

    def _compute_reviewers(self):
        for rec in self:
            rec.reviewer_ids = self.env["form.reviewer"].search(
                [
                    ("form_model", "=", rec._name),
                    ("form_id", "=", rec.id),
                ]
            )

    def _get_quotation_product(self):
        return self._get_or_create_product(
            name="Vehicle Sticker Pass Application",  # specific for vehicle form
            list_price=1.0,
            type="service",
        )
