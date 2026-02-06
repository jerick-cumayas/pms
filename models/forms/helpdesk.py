from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    form_model = fields.Char(string="Related Model")
    form_id = fields.Integer(string="Related Record ID")

    def _get_form_record(self):
        self.ensure_one()
        if self.form_model and self.form_id:
            return self.env[self.form_model].browse(self.form_id)
        return self.env[self.form_model]

    def action_open_form(self):
        self.ensure_one()
        if not self.form_model or not self.form_id:
            return False

        return {
            "name": "Pet Registration",
            "type": "ir.actions.act_window",
            "res_model": self.form_model,
            "res_id": self.form_id,
            "view_mode": "form",
            "target": "current",  # <-- opens in a popup
            "context": {
                "default_requestor_id": self.partner_id.id,  # pre-fill owner
            },
        }

    # related_record = fields.Reference(
    #     selection="_get_related_models",
    #     string="Related Document",
    #     compute="_compute_related_record",
    #     store=False,
    # )

    # def _get_related_models(self):
    #     return [
    #         ("form.purchase", "Purchase Form"),
    #         ("form.leave", "Leave Form"),
    #         ("form.expense", "Expense Form"),
    #     ]

    # def _compute_related_record(self):
    #     for ticket in self:
    #         if ticket.related_model and ticket.related_id:
    #             ticket.related_record = "%s,%s" % (
    #                 ticket.related_model,
    #                 ticket.related_id,
    #             )
    #         else:
    #             ticket.related_record = False
