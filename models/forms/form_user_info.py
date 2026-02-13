from odoo import fields, models
from odoo.exceptions import UserError


class UserInfoForm(models.Model):
    _name = "form.user_info"
    _description = "User Information Form"
    _rec_name = "full_name"

    _inherit = ["form.person.base", "form.base", "form.unit_owner_info.base"]

    user_id = fields.Many2one("res.users", string="User", readonly=True)
    partner_id = fields.Many2one("res.partner", string="Contact", readonly=True)
    # user_info_id = fields.Many2one(
    #     comodel_name="form.user_info",
    #     string="User Info Form",
    #     readonly=True,
    # )
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

    def action_open_user(self):
        self.ensure_one()
        if not self.user_id:
            raise UserError("No linked user found.")
        return {
            "type": "ir.actions.act_window",
            "name": "User",
            "res_model": "res.users",
            "view_mode": "form",
            "res_id": self.user_id.id,
            "target": "current",
        }

    def action_open_partner(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError("No linked contact found.")
        return {
            "type": "ir.actions.act_window",
            "name": "Contact",
            "res_model": "res.partner",
            "view_mode": "form",
            "res_id": self.partner_id.id,
            "target": "current",
        }

    def action_create_portal_user(self):
        Users = self.env["res.users"]
        PortalGroup = self.env.ref("base.group_portal")

        for rec in self:
            if rec.user_id:
                raise UserError("User already exists.")

            if not rec.email:
                raise UserError("Email is required to create a user.")

            # 1️⃣ Create Contact dynamically from form.user_info
            partner_vals = {}
            partner_model_fields = self.env["res.partner"].fields_get()

            for field_name, field_info in rec.fields_get().items():
                # Skip fields that shouldn't be copied
                if field_name in [
                    "id",
                    "user_id",
                    "full_name",
                    "create_uid",
                    "create_date",
                    "write_uid",
                    "write_date",
                ]:
                    continue

                # Only copy if res.partner has this field
                if field_name in partner_model_fields:
                    partner_vals[field_name] = getattr(rec, field_name)

            partner_vals["phone"] = rec.mobile_number
            partner_vals["mobile"] = rec.mobile_number
            partner_vals["function"] = rec.position
            partner_vals["street"] = rec.home_mailing_address
            partner_vals["street2"] = rec.office_address

            country_ph = self.env.ref("base.ph")
            partner_vals["country_id"] = country_ph.id
            partner_vals["city"] = "Cebu"

            # Ensure at least a name exists
            if "name" not in partner_vals:
                partner_vals["name"] = rec.full_name

            partner = self.env["res.partner"].create(partner_vals)

            # 2️⃣ Create User linked to Contact
            user = Users.with_context(no_reset_password=True).create(
                {
                    "name": rec.full_name,
                    "login": rec.email,
                    "email": rec.email,
                    "partner_id": partner.id,
                    "groups_id": [(6, 0, [PortalGroup.id])],
                }
            )

            # 3️⃣ Send invitation email
            user.action_reset_password()

            rec.user_id = user.id
            rec.user_info_id = rec.id
            rec.partner_id = partner.id

            return {
                "type": "ir.actions.act_window",
                "name": "Contact",
                "res_model": "res.partner",
                "res_id": partner.id,
                "view_mode": "form",
                "target": "current",
            }
