from odoo import models, fields

class TenantInfoForm(models.Model):
    _name = 'form.tenant_info'
    _description = 'Tenant Information Form'
    _rec_name = 'full_name'

    _inherit = 'form.unit_owner_info'

    move_in_date = fields.Date(
        string = 'Move In Date'
    )
    move_out_date = fields.Date(
        string = 'Move Out Date'
    )
    house_member_ids = fields.One2many(
        comodel_name='form.tenant_house_member',  # the related model
        inverse_name='tenant_id',                # the Many2one field on TenantHouseMember
        string='House Members'
    )

class TenantHouseMember(models.Model):
    _name = 'form.tenant_house_member'
    _description = 'Tenant House Member'
    _rec_name = 'full_name'

    _inherit = 'form.person.base'

    # Link back to the tenant
    tenant_id = fields.Many2one(
        comodel_name='form.tenant_info', 
        string='Tenant',
        required=True,
        ondelete='cascade'  # optional: delete house members if tenant is deleted
    )
    relationship = fields.Selection([
        ('spouse', 'Spouse'),
        ('child', 'Child'),
        ('parent', 'Parent'),
        ('sibling', 'Sibling'),
        ('other', 'Other')
    ], string='Relationship')

    age = fields.Integer(string='Age')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')