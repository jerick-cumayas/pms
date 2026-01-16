import base64
from odoo import models, fields, _
from odoo.exceptions import UserError

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

class TenantInfoForm(models.Model):
    _name = 'form.tenant_info'
    _description = 'Tenant Information Form'
    _rec_name = 'full_name'

    _inherit = ['form.base', 'form.person.base', 'form.unit_owner_info.base']
    
    tenant_id = fields.Many2one("res.partner", string="Tenant's name")

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

    def _get_template(self):
        template_name = f'Tenant Information - {self.id} - {self.create_date}.pdf'
        template = self.env['sign.template'].search([
            ('name', '=', template_name)
        ], limit=1)
        
        if not template:
            # Generate PDF
            pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
                'pms.action_tenant_info_sign_default',
                [self.id]
            )
            # Attachment
            attachment = self.env['ir.attachment'].create({
                'name': f'Tenant_Info_Form_{self.id}.pdf',
                'type': 'binary',
                'datas': base64.b64encode(pdf_content),
                'mimetype': 'application/pdf',
                'res_model': self._name,
                'res_id': self.id,
            })
            template = self.env['sign.template'].create({
                'name': template_name,
                'attachment_id': attachment.id,
            })
        return template

    def _prepare_signature_roles(self, template):
        roles = []

        requestor_role = self.env['sign.item.role'].search([
            ('name', '=', 'Requestor'),
        ], limit=1)

        # If not found, create it
        if not requestor_role:
            requestor_role = self.env['sign.item.role'].create({
                'name': 'Requestor',
                'template_id': template.id,
            })
        
        roles.append(requestor_role)
        
        approver_role = self.env['sign.item.role'].search([
            ('name', '=', 'Approver'),
        ], limit=1)

        if not approver_role:
            approver_role = self.env['sign.item.role'].create({
                'name': 'Approver',
                'template_id': template.id,
            })
            
        roles.append(approver_role)
        
        return roles
    
    def action_sign(self):
        if self.state != 'approved':
            raise UserError(_("Only approved requests can be signed."))
        
        if not self.approver_id:
            raise UserError(_("Approver is not configured."))
        try:
            template = self._get_template()
            signature_type = super()._get_signature_type()
            signature_roles = self._prepare_signature_roles(template)
            request_items = []

            for role in signature_roles:
                if role.name == 'Requestor':
                    self.env['sign.item'].sudo().create({
                        'name': 'Signature',
                        'type_id': signature_type.id,     # from sign_item_type
                        'template_id': template.id,       # from sign_template
                        'responsible_id': role.id,        # from sign_item_role
                        'page': 1,
                        'posX': 0.17,
                        'posY': 0.76,
                        'width': 0.2,
                        'height': 0.05,
                        'alignment': 'center',
                        'required': True,
                    })
                    request_items.append(
                        (0, 0, {
                            'partner_id': self.tenant_id.id,
                            'role_id': role.id,
                        })
                    )
                else:
                    self.env['sign.item'].sudo().create({
                        'name': 'Signature',
                        'type_id': signature_type.id,     # from sign_item_type
                        'template_id': template.id,       # from sign_template
                        'responsible_id': role.id,        # from sign_item_role
                        'page': 1,
                        'posX': 0.63,
                        'posY': 0.76,
                        'width': 0.2,
                        'height': 0.05,
                        'alignment': 'center',
                        'required': True,
                    })
                    request_items.append(
                        (0, 0, {
                            'partner_id': self.approver_id.id,
                            'role_id': role.id,
                        })
                    )

            sign_request = self.env['sign.request'].create({
                'template_id': template.id,
                'subject': f"Tenant Information Form - {self.full_name}",
                'reference': f"Tenant Information Form - {self.full_name}",
                'request_item_ids': request_items,
            })

            self.sign_request_id = sign_request.id
            
            super().action_sign()

            return {
                'type': 'ir.actions.act_window',
                'name': 'Signature Request',
                'res_model': 'sign.request',
                'res_id': sign_request.id,
                'view_mode': 'form',
                'target': 'current',
            }

        except Exception as e:
            raise UserError("An error occurred: %s" % str(e))
    