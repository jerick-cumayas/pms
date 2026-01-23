import base64
from odoo import models, fields, api, _
from odoo.exceptions import UserError

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

class SpouseInfoForm(models.Model):
    _name = 'form.spouse_info'
    _description = 'Spouse Info'
    _rec_name = 'full_name'

    _inherit = 'form.person.base'

class UnitOwnerInfoForm(models.Model):
    _name = 'form.unit_owner_info'
    _description = 'Unit Owner Information Form'
    _rec_name = 'full_name'

    _inherit = ['form.person.base', 'form.base', 'form.unit_owner_info.base']

    owner_id = fields.Many2one("res.partner", string="Owner's name")

    def _get_template(self):
        template_name = f'Unit Owner Information - {self.id} - {self.create_date}.pdf'
        template = self.env['sign.template'].search([
            ('name', '=', template_name)
        ], limit=1)
        
        if not template:
            # Generate PDF
            pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
                'pms.action_unit_owner_info_sign_default',
                [self.id]
            )
            # Attachment
            attachment = self.env['ir.attachment'].create({
                'name': f'Unit_Owner_Information_Form_{self.id}.pdf',
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
                            'partner_id': self.owner_id.id,
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
                'subject': f"Unit Owner Information Form - {self.full_name}",
                'reference': f"Unit Owner Information Form - {self.full_name}",
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
    