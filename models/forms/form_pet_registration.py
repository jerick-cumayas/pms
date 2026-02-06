import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PetDetails(models.Model):
    _name = "pet.details"
    _description = "Pet Details"

    # Link to registration form
    registration_id = fields.Many2one(
        "form.pet_registration", string="Pet Registration", ondelete="cascade"
    )

    # Pet Information
    name = fields.Char(string="Pet Name", required=True)
    species = fields.Selection(
        [("dog", "Dog"), ("cat", "Cat"), ("bird", "Bird"), ("other", "Other")],
        string="Species",
        required=True,
    )
    breed = fields.Char(string="Breed")
    age = fields.Integer(string="Age (years)")
    gender = fields.Selection([("male", "Male"), ("female", "Female")], string="Gender")
    details = fields.Text(string="Other details")
    is_vaccinated = fields.Boolean(string="Is Vaccinated?")


class PetRegistrationForm(models.Model):
    _name = "form.pet_registration"
    _description = "Pet Registration Form"
    _inherit = ["form.base"]

    requestor_id = fields.Many2one("res.partner", string="Owner's name", required=True)
    pet_ids = fields.One2many(
        "pet.details",  # related model
        "registration_id",  # field in pet.details linking back
        string="Pet Details",
    )

    reviewer_ids = fields.One2many(
        "form.reviewer",
        "form_id",
        string="Reviewers",
        compute="_compute_reviewers",
        store=True,
    )

    def _get_template(self):
        template_name = f"Pet Registration - {self.id} - {self.create_date}.pdf"
        template = self.env["sign.template"].search(
            [("name", "=", template_name)], limit=1
        )

        if not template:
            # Generate PDF
            pdf_content, _ = self.env["ir.actions.report"]._render_qweb_pdf(
                "pms.action_pet_registration_sign_default", self.ids
            )
            # Attachment
            attachment = self.env["ir.attachment"].create(
                {
                    "name": f"Pet_Registration_{self.id}.pdf",
                    "type": "binary",
                    "datas": base64.b64encode(pdf_content),
                    "mimetype": "application/pdf",
                    "res_model": self._name,
                    "res_id": self.id,
                }
            )
            template = self.env["sign.template"].create(
                {
                    "name": template_name,
                    "attachment_id": attachment.id,
                }
            )
        return template

    def _prepare_signature_roles(self, template):
        roles = []

        # Create role
        # Try to find an existing role for this template
        requestor_role = self.env["sign.item.role"].search(
            [
                ("name", "=", "Requestor"),
            ],
            limit=1,
        )

        # If not found, create it
        if not requestor_role:
            requestor_role = self.env["sign.item.role"].create(
                {
                    "name": "Requestor",
                    "template_id": template.id,
                }
            )

        roles.append(requestor_role)

        approver_role = self.env["sign.item.role"].search(
            [
                ("name", "=", "Approver"),
            ],
            limit=1,
        )

        if not approver_role:
            approver_role = self.env["sign.item.role"].create(
                {
                    "name": "Approver",
                    "template_id": template.id,
                }
            )

        roles.append(approver_role)

        return roles

    def action_sign(self):
        if self.state != "approved":
            raise UserError(_("Only approved requests can be signed."))

        if not self.approver_id:
            raise UserError(_("Approver is not configured."))
        try:
            template = self._get_template()
            signature_type = super()._get_signature_type()
            signature_roles = self._prepare_signature_roles(template)
            request_items = []

            for role in signature_roles:
                # Create item linked to role
                if role.name == "Requestor":
                    self.env["sign.item"].sudo().create(
                        {
                            "name": "Signature",
                            "type_id": signature_type.id,  # from sign_item_type
                            "template_id": template.id,  # from sign_template
                            "responsible_id": role.id,  # from sign_item_role
                            "page": 1,
                            "posX": 0.17,
                            "posY": 0.585,
                            "width": 0.2,
                            "height": 0.05,
                            "alignment": "center",
                            "required": True,
                        }
                    )
                    request_items.append(
                        (
                            0,
                            0,
                            {
                                "partner_id": self.requestor_id.id,
                                "role_id": role.id,
                            },
                        )
                    )
                else:
                    self.env["sign.item"].sudo().create(
                        {
                            "name": "Signature",
                            "type_id": signature_type.id,  # from sign_item_type
                            "template_id": template.id,  # from sign_template
                            "responsible_id": role.id,  # from sign_item_role
                            "page": 1,
                            "posX": 0.63,
                            "posY": 0.585,
                            "width": 0.2,
                            "height": 0.05,
                            "alignment": "center",
                            "required": True,
                        }
                    )
                    request_items.append(
                        (
                            0,
                            0,
                            {
                                "partner_id": self.approver_id.id,
                                "role_id": role.id,
                            },
                        )
                    )

            num_pets = len(self.pet_ids)
            sign_request = self.env["sign.request"].create(
                {
                    "template_id": template.id,
                    "subject": f"Pet Registration - {num_pets} - {self.requestor_id.name}",
                    "reference": f"Pet Registration - {num_pets} - {self.requestor_id.name}",
                    "request_item_ids": request_items,
                }
            )

            self.sign_request_id = sign_request.id

            super().action_sign()

            return {
                "type": "ir.actions.act_window",
                "name": "Signature Request",
                "res_model": "sign.request",
                "res_id": sign_request.id,
                "view_mode": "form",
                "target": "current",
            }

        except Exception as e:
            raise UserError("An error occurred: %s" % str(e))
