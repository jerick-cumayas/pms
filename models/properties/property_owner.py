from odoo import fields, models


class PropertyOwner(models.Model):
    _name = "property.current.owner"
    _description = "Current Property Ownership"
    _rec_name = "main_owner_id"

    unit_id = fields.One2one(
        "property.unit",
        required=True,
        ondelete="cascade",
    )

    main_owner_id = fields.Many2one(
        "res.partner",
        required=True,
        domain=[("is_company", "=", False)],
        string="Main Owner",
    )

    member_ids = fields.Many2many(
        "res.partner",
        domain=[("is_company", "=", False)],
        string="Co-Owners / Family Members",
    )

    start_date = fields.Date(required=True)
