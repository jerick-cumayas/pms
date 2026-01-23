from odoo import fields, models


class GatePassItem(models.Model):
    _name = "forms.gate_pass_item"
    _description = "Gate Pass Item"

    gate_pass_id = fields.Many2one(
        "forms.gate_pass", string="Gate Pass Item", ondelete="cascade", required=True
    )
    quantity = fields.Integer(string="Quantity/Unit")
    description = fields.Text(string="Item Description")
    remarks = fields.Char(string="Remarks")


class GatePassForm(models.Model):
    _name = "forms.gate_pass"
    _description = "Gate Pass Form"

    cn_no = fields.Char(string="CN No.")
    authorized_carrier = fields.Char(string="Authorized Carrier")
    company = fields.Char(string="Company")
    transaction = fields.Selection(
        [
            ("pull_out", "Pull Out"),
            ("delivery", "Delivery"),
        ],
        string="Nature of Transaction",
        default="pull_out",
    )
    purpose = fields.Text(string="Purpose")

    item_ids = fields.One2many(
        "forms.gate_pass_item",
        "gate_pass_id",
        string="Specifications",
    )
