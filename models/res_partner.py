from odoo import api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    user_info_id = fields.Many2one("form.user_info", string="User Info Form")

    # Copy the fields from UserInfoForm
    # Example: personal info fields
    first_name = fields.Char(string="First Name")
    middle_name = fields.Char(string="Middle Name")
    last_name = fields.Char(string="Last Name")
    full_name = fields.Char(
        string="Full Name", compute="_compute_full_name", store=True
    )
    age = fields.Integer(string="Age")
    gender = fields.Selection([("male", "Male"), ("female", "Female")], string="Gender")
    civil_status = fields.Selection(
        [("single", "Single"), ("married", "Married")], string="Civil Status"
    )
    birthday = fields.Date(string="Birthday")
    nationality = fields.Char(string="Nationality")
    home_mailing_address = fields.Text(string="Home Mailing Address")
    home_mailing_address_tel_no = fields.Char(string="Tel No. (Residence)")
    abroad_address = fields.Text(string="Address Abroad (If any)")
    abroad_address_tel_no = fields.Char(string="Tel No. (Abroad if any)")
    office_address = fields.Text(string="Office Address")
    office_address_tel_no = fields.Char(string="Tel No. (Office)")
    occupation = fields.Char(string="Occupation")
    religion = fields.Char(string="Religion")
    owned_unit_ids = fields.Many2many(
        "property.unit",
        compute="_compute_owned_units",
        string="Owned Units",
        store=False,
    )
    rented_unit_ids = fields.Many2many(
        "property.unit",
        compute="_compute_rented_units",
        string="Rented Units",
        store=False,
    )

    # Optional: compute full_name
    @api.depends("first_name", "middle_name", "last_name")
    def _compute_full_name(self):
        for rec in self:
            rec.full_name = " ".join(
                filter(None, [rec.first_name, rec.middle_name, rec.last_name])
            )

    def _compute_owned_units(self):
        for partner in self:
            units = self.env["property.unit"].search(
                [("current_owner_ids", "in", partner.id)]
            )
            partner.owned_unit_ids = units

    def _compute_rented_units(self):
        for partner in self:
            units = self.env["property.unit"].search(
                [("current_tenant_id", "=", partner.id)]
            )
            partner.rented_unit_ids = units
