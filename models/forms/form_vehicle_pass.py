from odoo import fields, models


class VehiclePassForm(models.Model):
    _name = "forms.vehicle_pass"
    _description = "Vehicle Pass Form"
    _inherit = ["form.base"]

    requestor_id = fields.Many2one(
        "res.partner", string="Name of Requestor", required=True
    )
    application_type = fields.Selection(
        [("new", "New"), ("renewal", "Renewal")],
        string="Type of Application",
    )
    vehicle_ownership = fields.Selection(
        [("owned", "Owned"), ("company", "Company")], string="Ownership of Vehicle"
    )
    lto_cr_attachment_ids = fields.Many2many(
        "ir.attachment",
        "sticker_lto_cr_rel",
        "application_id",
        "attachment_id",
        string="LTO OR / Certificate of Registration",
    )
    plate_no_attachment_ids = fields.Many2many(
        "ir.attachment",
        "sticker_plate_no_rel",
        "application_id",
        "attachment_id",
        string="Plate Number",
    )
    driver_license_attachment_ids = fields.Many2many(
        "ir.attachment",
        "sticker_driver_license_rel",
        "application_id",
        "attachment_id",
        string="Driver’s License",
    )
    deed_of_sale_attachment_ids = fields.Many2many(
        "ir.attachment",
        "sticker_deed_sale_rel",
        "application_id",
        "attachment_id",
        string="Duly Notarized Deed of Sale",
    )
    homeowner_endorsement_attachment_ids = fields.Many2many(
        "ir.attachment",
        "sticker_homeowner_endorse_rel",
        "application_id",
        "attachment_id",
        string="Homeowner Endorsement",
    )
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
