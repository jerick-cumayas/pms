from odoo import api, fields, models


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

    property_ownership_ids = fields.One2many(
        "property.ownership", "main_partner_id", string="Ownership Records"
    )
    property_tenancy_ids = fields.One2many(
        "property.tenancy", "main_partner_id", string="Tenancy Records"
    )

    current_owned_unit_ids = fields.One2many(
        "property.unit",
        compute="_compute_current_units",
        string="Units Owned",
        readonly=True,  # Important
    )
    current_tenant_unit_ids = fields.One2many(
        "property.unit",
        compute="_compute_current_units",
        string="Units Rented",
        readonly=True,  # Important
    )

    @api.depends("property_ownership_ids.state", "property_tenancy_ids.state")
    def _compute_current_units(self):
        for partner in self:
            # search units where this partner is the current owner
            owner_units = self.env["property.unit"].search(
                [("ownership_partner_id", "=", partner.id)]
            )
            # search units where this partner is the current tenant
            tenant_units = self.env["property.unit"].search(
                [("tenancy_partner_id", "=", partner.id)]
            )
            partner.current_owned_unit_ids = owner_units
            partner.current_tenant_unit_ids = tenant_units

    # Optional: compute full_name
    @api.depends("first_name", "middle_name", "last_name")
    def _compute_full_name(self):
        for rec in self:
            rec.full_name = " ".join(
                filter(None, [rec.first_name, rec.middle_name, rec.last_name])
            )
