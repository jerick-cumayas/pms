from odoo import fields, models


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    property_unit_id = fields.Many2one(
        "property.unit", string="Property Unit", help="Unit being sold"
    )
