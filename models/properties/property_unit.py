from datetime import timedelta

from odoo import api, fields, models


class PropertyUnit(models.Model):
    _name = "property.unit"
    _description = "Property Unit"
    _rec_name = "display_name"

    name = fields.Char(required=True)
    building_id = fields.Many2one(
        "property.building", required=True, ondelete="restrict"
    )
    price = fields.Float(string="Default Price")

    ownership_ids = fields.One2many(
        "property.ownership",
        "unit_id",
        string="Ownership History",
    )
    tenancy_ids = fields.One2many(
        "property.tenancy",
        "unit_id",
        string="Tenancy History",
    )
    current_ownership_id = fields.Many2one(
        "property.ownership",
        string="Current Owner",
        compute="_compute_current_ownership",
        store=True,
        readonly=True,
    )
    current_tenancy_id = fields.Many2one(
        "property.tenancy",
        string="Current Tenant",
        compute="_compute_current_tenancy",
        store=True,
        readonly=True,
    )
    ownership_partner_id = fields.Many2one(
        "res.partner",
        string="Owner Partner",
        related="current_ownership_id.main_partner_id",
        readonly=True,
        store=True,  # optional: only if you need to search/group/filter
    )

    tenancy_partner_id = fields.Many2one(
        "res.partner",
        string="Tenant Partner",
        related="current_tenancy_id.main_partner_id",
        readonly=True,
        store=True,  # optional
    )

    # sale_ids = fields.One2many("property.sale", "unit_id", string="Sales / Quotations")

    state = fields.Selection(
        [
            ("available", "Available"),  # No current owner
            ("reserved", "Reserved"),  # Has an active owner
            ("occupied", "Occupied"),  # Has an active owner
            ("owned", "Owned"),  # Has an active owner
            ("unavailable", "Unavailable"),  # Has an active owner
        ],
        string="Status",
        default="available",
        store=True,
    )

    @api.depends("name", "building_id")
    def _compute_display_name(self):
        for unit in self:
            building_name = unit.building_id.name if unit.building_id else "No Building"
            unit_name = unit.name or "No Name"
            unit.display_name = f"{unit_name} - {building_name}"

    @api.depends("ownership_ids.state", "ownership_ids.start_date")
    def _compute_current_ownership(self):
        for unit in self:
            active = unit.ownership_ids.filtered(lambda o: o.state == "active")
            unit.current_ownership_id = active[:1] if active else False

    @api.depends("tenancy_ids.state", "tenancy_ids.start_date")
    def _compute_current_tenancy(self):
        for unit in self:
            active = unit.tenancy_ids.filtered(lambda t: t.state == "active")
            unit.current_tenancy_id = active[:1] if active else False
