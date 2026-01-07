from odoo import models, fields, api

class AmenitiesRequestForm(models.Model):
    _name = 'form.amenities'
    _description = 'Amenities Form'

    # REQUIRED for website forms
    website_form_access = True
    
    requestor_id = fields.Many2one(
        'res.partner',
        string="Name of Requestor",
        required=True
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

    def get_requestors(self):
        """
        Returns a recordset of partners eligible to be requestors,
        excluding the current logged-in user.
        """
        current_partner = self.env.user.partner_id
        return self.env['res.partner'].search([('id', '!=', current_partner.id)])
