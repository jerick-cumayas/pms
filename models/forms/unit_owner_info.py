from odoo import models, fields, api

class VehicleInfoForm(models.Model):
    _name = 'form.vehicle_info'
    _description = 'Vehicle Info'
    _rec_name = 'plate_no'

    brand = fields.Char(
        string = 'Brand'
    )
    type = fields.Char(
        string = 'Type'
    )
    plate_no = fields.Char(
        string = 'Plate No.'
    )
    colour = fields.Char(
        string = 'Colour'
    )


class PersonBase(models.AbstractModel):
    _name = 'form.person.base'
    _description = 'Common Person Fields'

    first_name = fields.Char(
        string='First Name',
        required=True
    )
    middle_name = fields.Char(
        string='Middle Name',
        required=True
    )
    last_name = fields.Char(
        string='Last Name',
        required=True
    )
    full_name = fields.Char(
        string='Full Name',
        compute='_compute_full_name',
        store=True,
        readonly=True
    )
    age = fields.Integer(
        string="Age",
        required=True
    )
    gender = fields.Selection(
        [("male", "Male"), ("female", "Female")],
        string="Gender"
    )
    civil_status = fields.Selection(
        [("single", "Single"), ("married", "Married")],
        string="Civil Status"
    )
    birthday = fields.Date(
        string='Birthday'
    )
    nationality = fields.Char(
        string='Nationality'
    )
    home_mailing_address = fields.Text(
        string='Home Mailing Address'
    )
    home_mailing_address_tel_no = fields.Char(
        string='Tel No. (Residence)'
    )
    abroad_address = fields.Text(
        string='Address Abroad (If any)'
    )
    abroad_address_tel_no = fields.Char(
        string='Tel No. (Abroad if any)'
    )
    office_address = fields.Text(
        string='Office Address'
    )
    office_address_tel_no = fields.Char(
        string='Tel No. (Office)'
    )
    email = fields.Char(
        string='Email Address'
    )
    mobile_number = fields.Char(
        string='Mobile Number'
    )
    office_business = fields.Char(
        string='Office/Business Name'
    )
    position = fields.Char(
        string='Position'
    )
    occupation = fields.Char(
        string='Occupation'
    )
    religion = fields.Char(
        string='Religion'
    )

    @api.depends('first_name', 'middle_name', 'last_name')
    def _compute_full_name(self):
        for rec in self:
            rec.full_name = " ".join(
                filter(None, [rec.first_name, rec.middle_name, rec.last_name])
            )

class SpouseInfoForm(models.Model):
    _name = 'form.spouse_info'
    _description = 'Spouse Info'
    _rec_name = 'full_name'

    _inherit = 'form.person.base'

class UnitOwnerInfoForm(models.Model):
    _name = 'form.unit_owner_info'
    _description = 'Unit Owner Information Form'
    _rec_name = 'full_name'

    _inherit = 'form.person.base'

    unit_id = fields.Many2one(
        comodel_name='building.unit',
        string="Assigned Unit"
    )

    spouse_info_id = fields.Many2one(
        comodel_name='form.spouse_info',
        string='Spouse Info'
    )
    vehicle_info_id = fields.Many2one(
        comodel_name='form.vehicle_info',
        string='Vehicle Info'
    )

    spouse_id = fields.Many2one(
        comodel_name='res.partner',
        string='Spouse'
    )
    vehicle_id = fields.Many2one(
        comodel_name='res.partner',
        string='Vehicle'
    )
    