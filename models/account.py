from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _compute_payment_state(self):
        super()._compute_payment_state()
        for move in self:
            if move.move_type == "out_invoice" and move.payment_state == "paid":
                move._handle_unit_sale()

    def _handle_unit_sale(self):
        for line in self.invoice_line_ids:
            sale_line = line.sale_line_ids[:1]  # take the first linked sale order line
            if sale_line:
                sale_order = sale_line.order_id
                if (
                    hasattr(sale_order, "property_unit_id")
                    and sale_order.property_unit_id
                ):
                    unit = sale_order.property_unit_id

                    # Only create ownership if not already sold
                    if unit.state != "sold":
                        self.env["property.ownership"].create(
                            {
                                "unit_id": unit.id,
                                "owner_id": self.partner_id.id,
                                "start_date": fields.Date.today(),
                            }
                        )
                        unit.state = "sold"
