from odoo import models, fields, api

class WebsiteRequest(models.Model):
    _name = 'website.request'
    _description = 'Website Request'

    # REQUIRED for website forms
    website_form_access = True

    name = fields.Char(string="Name", required=True)
    email = fields.Char(string="Email")
    message = fields.Text(string="Message")

