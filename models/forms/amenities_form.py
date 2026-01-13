import base64
from odoo import models, fields, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class AmenitiesRequestForm(models.Model):
    _name = 'form.amenities'
    _description = 'Amenities Form'

    # REQUIRED for website forms
    website_form_access = True
    
    amenity = fields.Selection([
        ('swimming_pool', 'Swimming Pool'),
        ('basketball', 'Basketball'),
        ('clubhouse', 'Clubhouse'),
    ], string='Status', default='swimming_pool', tracking=True)
    amenity_name = fields.Char(
        compute="_compute_amenity_name_label",
        store=False
    )
    def _compute_amenity_name_label(self):
        for rec in self:
            rec.amenity_name = dict(
                rec._fields['amenity'].selection
            ).get(rec.amenity)

    requestor_id = fields.Many2one(
        'res.partner',
        string="Name of Requestor",
        required=True
    )
    approver_id = fields.Many2one(
        'res.partner',
        string="Name of Approver",
    )
    activity_type = fields.Text(
        string="Type of Activity",
        required=True
    )
    sponsor_id = fields.Many2one(
        'res.partner',
        string="If sponsored, unit owner's name",
    )
    relation = fields.Char(
        string="Relation to member/resident",
        required=True
    )
    date_from = fields.Date(
        string="Date From",
        required=True
    )
    date_to = fields.Date(
        string="Date To",
        required=True
    )
    guest_ids = fields.Many2many(
        'res.partner', # model
        'amenities_request_partner_rel',  # relation table
        'request_id',
        'partner_id',
        string="Guest List"
    )

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

    def get_requestors(self):
        """
        Returns a recordset of partners eligible to be requestors,
        excluding the current logged-in user.
        """
        current_partner = self.env.user.partner_id
        return self.env['res.partner'].search([('id', '!=', current_partner.id)])
    
    def action_print_pdf(self):
        self.ensure_one()
        return self.env.ref(
            'pms.action_report_amenities_request'
        ).report_action(self)
    
    # Action buttons - FIXED version without message_post
    def action_submit(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Only draft requests can be submitted.'))
            record.state = 'submitted'
    
    def action_approve(self):
        for record in self:
            if record.state != 'submitted':
                raise UserError(_('Only submitted requests can be approved.'))
            record.state = 'approved'
            record.approval_date = fields.Datetime.now()
            record.approved_by = self.env.user
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
    
    def action_draft(self):
        for record in self:
            record.state = 'draft'

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
    
    def _get_template(self):
        # Try to find an existing template for this record
        template_name = f'Amenities Request.pdf'
        template = self.env['sign.template'].search([
            ('name', '=', template_name),
        ], limit=1)

        # If not found, create it
        if not template:
            # Generate PDF
            pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
                'pms.action_report_amenities_sign_default',
                self.ids
            )

            # Attachment
            attachment = self.env['ir.attachment'].create({
                'name': f'Amenities_Request_{self.id}.pdf',
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
    
    def _get_signature_type(self):
        signature_type = self.env['sign.item.type'].search([('name', '=', 'Signature')], limit=1)
        if not signature_type:
            raise UserError(_("Signature type is not configured."))
        return signature_type
    
    def _prepare_signature_roles(self, template):
        roles = []

        # Create role
        # Try to find an existing role for this template
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
    
    def action_create_sign_template(self):
        self.ensure_one()

        if self.state != 'approved':
            raise UserError(_("Only approved requests can be signed."))
        
        if not self.approver_id:
            raise UserError(_("Approver is not configured."))

        try:
            template = self._get_template()
            signature_type = self._get_signature_type()
            signature_roles = self._prepare_signature_roles(template)
            request_items = []

            for role in signature_roles:
                # Create item linked to role
                if role.name == 'Requestor':
                    self.env['sign.item'].sudo().create({
                        'name': 'Signature',
                        'type_id': signature_type.id,     # from sign_item_type
                        'template_id': template.id,       # from sign_template
                        'responsible_id': role.id,        # from sign_item_role
                        'page': 1,
                        'posX': 0.17,
                        'posY': 0.67,
                        'width': 0.2,
                        'height': 0.05,
                        'alignment': 'center',
                        'required': True,
                    })
                    request_items.append(
                        (0, 0, {
                            'partner_id': self.requestor_id.id,
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
                        'posY': 0.67,
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
                'subject': f"Amenities Request - {self.amenity_name} - {self.requestor_id.name}",
                'reference': f"Amenities Request - {self.amenity_name} - {self.requestor_id.name}",
                'request_item_ids': request_items,
            })

            self.sign_request_id = sign_request.id
            self.state = 'signed'

            return {
                'type': 'ir.actions.act_window',
                'name': 'Signature Request',
                'res_model': 'sign.request',
                'res_id': sign_request.id,
                'view_mode': 'form',
                'target': 'current',
            }

        except Exception as e:
            _logger.exception("Error creating sign template")
            raise UserError("An error occurred: %s" % str(e))