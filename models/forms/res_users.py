from odoo import models


class HelpdeskTicket(models.Model):
    _inherit = "res.users"

    def action_update_details():
        print("hello world")
