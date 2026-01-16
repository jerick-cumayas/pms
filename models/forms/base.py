from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FormBase(models.AbstractModel):
    _name = 'form.base'
    _description = 'Base Model'
    
    # Signature fields
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('signed', 'Signed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    approval_date = fields.Datetime(
        string='Approval Date',
        copy=False
    )
    approver_id = fields.Many2one(
        'res.partner',
        string="Name of Approver",
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        copy=False
    )
    sign_request_id = fields.Many2one(
        'sign.request',
        string="Signature Request",
        copy=False
    )

    def _get_signature_type(self):
        signature_type = self.env['sign.item.type'].search([('name', '=', 'Signature')], limit=1)
        if not signature_type:
            raise UserError(_("Signature type is not configured."))
        return signature_type

    # ---------- FUNCTIONS ----------
    def action_open_sign_request(self):
        self.ensure_one()
        if not self.sign_request_id:
            raise UserError("No signature request linked to this form.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Signature Request',
            'res_model': 'sign.request',
            'res_id': self.sign_request_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_submit(self):
        self.write({
            'state': 'submitted'
        })

    def action_approve(self):
        self.write({
            'state': 'approved',
            'approval_date': fields.Datetime.now(),
            'approved_by': self.env.user.id,
        })

    def action_cancel(self):
        self.write({
            'state': 'cancelled'
        })

    def action_draft(self):
        self.write({
            'state': 'draft'
        })

    def action_sign(self):
        self.write({
            'state': 'signed'
        })

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

class UnitOwnerInfoForm(models.AbstractModel):
    _name = 'form.unit_owner_info.base'
    _description = 'Unit Owner Information Form'

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