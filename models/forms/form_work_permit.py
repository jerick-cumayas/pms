from odoo import api, fields, models


# -------------------------------------------------
# Work Permit
# -------------------------------------------------
class WorkPermit(models.Model):
    _name = "form.work_permit"
    _description = "Work Permit"

    contractor = fields.Char("Contractor")
    contractor_no = fields.Char("Contractor Contact #")
    estimated_completion = fields.Date("Estimated Completion Date")

    # Work Type & Scope
    work_type_ids = fields.Many2many("form.work_types", string="Work Type")
    work_scope_ids = fields.Many2many("form.work_scopes", string="Work Scope")
    work_details = fields.Text("Specify Details")

    # Generic Checklist Lines
    checklist_line_ids = fields.One2many(
        "form.work_permit.checklist.line", "permit_id", string="Checklist"
    )

    # Authorized Personnel
    personnel_ids = fields.One2many(
        "form.work_permit_personnels", "permit_id", string="Authorized Personnel"
    )


# -------------------------------------------------
# Work Type & Scope
# -------------------------------------------------
class WorkType(models.Model):
    _name = "form.work_types"
    _description = "Work Type Option"

    name = fields.Char("Type Name", required=True)


class WorkScope(models.Model):
    _name = "form.work_scopes"
    _description = "Work Scope Option"

    name = fields.Char("Scope Name", required=True)


# -------------------------------------------------
# Master Checklist Items
# -------------------------------------------------
class WorkPermitChecklistItem(models.Model):
    _name = "form.work_permit.checklist.item"
    _description = "Checklist Item"

    name = fields.Char("Item", required=True)
    checklist_type = fields.Selection(
        [
            ("hot_work", "Hot Work"),
            ("confined_hazard", "Confined Space Hazard"),
            ("confined_precaution", "Confined Space Precaution"),
            ("confined_safety", "Confined Space Safety Equipment"),
            ("height_prevention", "Work at Height Prevention"),
            ("height_procedure", "Work at Height Procedure"),
        ],
        required=True,
    )


# -------------------------------------------------
# Checklist Lines (per Permit)
# -------------------------------------------------
class WorkPermitChecklistLine(models.Model):
    _name = "form.work_permit.checklist.line"
    _description = "Checklist Line"

    permit_id = fields.Many2one(
        "form.work_permit",
        string="Work Permit",
        required=True,
        ondelete="cascade",
    )
    item_id = fields.Many2one(
        "form.work_permit.checklist.item",
        string="Checklist Item",
        required=True,
    )

    done = fields.Boolean("Done")
    remarks = fields.Text("Remarks")

    checklist_type = fields.Selection(
        related="item_id.checklist_type",
        store=True,
        readonly=True,
    )


# -------------------------------------------------
# Authorized Personnel
# -------------------------------------------------
class WorkPermitPersonnel(models.Model):
    _name = "form.work_permit_personnels"
    _description = "Work Permit Authorized Personnel"

    permit_id = fields.Many2one(
        "form.work_permit",
        string="Work Permit",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char("Name", required=True)
    email = fields.Char("Email", required=True)
