from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    form_id = fields.Many2one(
        "form.base",
        string="Related Form",
        readonly=True,
        help="Link to the originating form submission",
    )
