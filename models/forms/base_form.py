import base64
import mimetypes

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .form_constants import (
    STATE_APPROVED,
    STATE_CANCELLED,
    STATE_COMPLETED,
    STATE_DRAFT,
    STATE_INVOICE,
    STATE_QUOTATION,
    STATE_REJECTED,
    STATE_SIGNED,
    STATE_SUBMITTED,
    STATE_UNDER_REVIEW,
)


class FormDocumentType(models.Model):
    _name = "form.document.type"
    _description = "Document Type"
    _order = "sequence, id"

    name = fields.Char(
        string="Document Type",
        required=True,
        translate=True,
    )

    code = fields.Char(
        required=True,
        index=True,
    )

    sequence = fields.Integer(
        default=10,
        help="Controls the display order of document types.",
    )

    applies_to = fields.Selection(
        [
            ("vehicle_details", "Vehicle Details"),
            ("vehicle_pass", "Vehicle Pass"),
        ],
        string="Applies To",
        required=True,
    )

    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "unique_document_type_code",
            "unique(code)",
            "The document type code must be unique.",
        )
    ]


class FormReviewer(models.Model):
    _name = "form.reviewer"
    _description = "Base Form Reviewer"

    form_model = fields.Char(
        string="Form Model", required=True
    )  # model name, e.g., 'form.purchase'
    form_id = fields.Integer(string="Form Record ID", required=True)
    reviewer_id = fields.Many2one("res.users", string="Reviewer", required=True)
    review_for = fields.Char(string="Review For")
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
        ],
        string="Status",
        default="pending",
    )
    review_date = fields.Datetime(default=fields.Datetime.now)
    remarks = fields.Text(string="Remarks")


class FormBase(models.AbstractModel):
    _name = "form.base"
    _description = "Base Model"

    # ---------- STATES ----------
    STATE_TRANSITIONS = {
        STATE_DRAFT: [STATE_SUBMITTED, STATE_CANCELLED],
        STATE_SUBMITTED: [STATE_APPROVED, STATE_UNDER_REVIEW, STATE_REJECTED],
        STATE_APPROVED: [STATE_SIGNED, STATE_REJECTED],
        STATE_UNDER_REVIEW: [STATE_COMPLETED, STATE_QUOTATION, STATE_CANCELLED],
        STATE_QUOTATION: [STATE_INVOICE, STATE_CANCELLED],
        STATE_INVOICE: [STATE_COMPLETED, STATE_CANCELLED],
        STATE_COMPLETED: [STATE_DRAFT],
        STATE_SIGNED: [],
        STATE_REJECTED: [STATE_DRAFT],
        STATE_CANCELLED: [STATE_DRAFT],
    }

    requestor_id = fields.Many2one(
        "res.partner", string="Name of Requestor", required=True
    )

    state = fields.Selection(
        [
            (STATE_DRAFT, "Draft"),
            (STATE_SUBMITTED, "Submitted"),
            (STATE_UNDER_REVIEW, "Under Review"),
            (STATE_QUOTATION, "Quotation"),
            (STATE_INVOICE, "Invoice"),
            (STATE_APPROVED, "Approved"),
            (STATE_SIGNED, "Signed"),
            (STATE_COMPLETED, "Completed"),
            (STATE_REJECTED, "Rejected"),
            (STATE_CANCELLED, "Cancelled"),
        ],
        string="Status",
        default=STATE_DRAFT,
    )

    reviewer_ids = fields.One2many(
        "form.reviewer",
        "form_id",
        string="Reviewers",
        store=False,  # Must be stored so other computed fields can track changes
    )

    helpdesk_ticket_id = fields.Many2one(
        "helpdesk.ticket",
        string="Helpdesk Ticket",
        readonly=True,
        store=True,
    )

    # ---------- COMPUTED PERMISSIONS FOR BUTTONS ----------
    can_submit = fields.Boolean(compute="_compute_allowed_actions", store=False)
    can_under_review = fields.Boolean(compute="_compute_allowed_actions", store=False)
    can_complete = fields.Boolean(compute="_compute_can_complete", store=False)
    can_reject = fields.Boolean(compute="_compute_allowed_actions", store=False)
    can_approve = fields.Boolean(compute="_compute_allowed_actions", store=False)
    can_cancel = fields.Boolean(compute="_compute_allowed_actions", store=False)
    can_draft = fields.Boolean(compute="_compute_allowed_actions", store=False)
    can_sign = fields.Boolean(compute="_compute_allowed_actions", store=False)
    review_incomplete = fields.Boolean(
        compute="_compute_review_incomplete",
        store=False,
    )

    is_locked = fields.Boolean(compute="_compute_is_locked")
    is_assigned = fields.Boolean(compute="_compute_show_assign_reviewer_btn")
    review_section_locked = fields.Boolean(compute="_compute_is_locked")

    @api.depends("state")
    def _compute_is_locked(self):
        for rec in self:
            # The whole form is locked if completed or cancelled
            rec.is_locked = rec.state in [
                STATE_COMPLETED,
                STATE_UNDER_REVIEW,
                STATE_CANCELLED,
                STATE_SIGNED,
                STATE_REJECTED,
            ]

            # Review section is editable only in under_review
            rec.review_section_locked = rec.state not in [
                STATE_SUBMITTED,
                STATE_UNDER_REVIEW,
            ]

    def _compute_allowed_actions(self):
        for rec in self:
            transitions = self.STATE_TRANSITIONS.get(rec.state, [])
            rec.can_submit = STATE_SUBMITTED in transitions
            rec.can_under_review = (
                STATE_UNDER_REVIEW in transitions
            ) and not rec.is_assigned
            rec.can_reject = STATE_REJECTED in transitions
            rec.can_approve = STATE_APPROVED in transitions
            rec.can_cancel = STATE_CANCELLED in transitions
            rec.can_draft = STATE_DRAFT in transitions
            rec.can_sign = STATE_SIGNED in transitions

    def _compute_show_assign_reviewer_btn(self):
        for rec in self:
            rec.is_assigned = not bool(rec.reviewer_ids)

    @api.depends("state", "reviewer_ids.state")
    def _compute_can_complete(self):
        for rec in self:
            rec.can_complete = (
                STATE_COMPLETED in rec.STATE_TRANSITIONS.get(rec.state, [])
                and bool(rec.reviewer_ids)
                and not rec.review_incomplete
            )

    @api.depends("state", "reviewer_ids.state")
    def _compute_review_incomplete(self):
        for rec in self:
            rec.review_incomplete = (
                rec.state == STATE_UNDER_REVIEW
                and bool(rec.reviewer_ids)
                and any(r.state != STATE_COMPLETED for r in rec.reviewer_ids)
            )

    # ---------- HELPER METHODS ----------
    def _check_transition(self, target_state, text=None):
        self.ensure_one()
        allowed = self.STATE_TRANSITIONS.get(self.state, [])
        if target_state not in allowed:
            raise UserError(
                text or f"You cannot move from '{self.state}' to '{target_state}'."
            )

    def _get_signature_type(self):
        signature_type = self.env["sign.item.type"].search(
            [("name", "=", "Signature")], limit=1
        )
        if not signature_type:
            raise UserError(_("Signature type is not configured."))
        return signature_type

    # ---------- GENERIC STATE TRANSITION ----------
    def action_set_state(self, target_state, **extra_vals):
        """
        Generic function to change the state of the form.
        Optional extra_vals can include dates, user fields, etc.
        """
        self.ensure_one()
        self._check_transition(target_state)
        vals = {"state": target_state}
        vals.update(extra_vals)
        self.write(vals)

    def action_open_helpdesk_ticket(self):
        self.ensure_one()

        if not self.helpdesk_ticket_id:
            return False

        if not self.helpdesk_ticket_id.exists():
            return False

        return {
            "name": "Helpdesk Ticket",
            "type": "ir.actions.act_window",
            "res_model": "helpdesk.ticket",
            "res_id": self.helpdesk_ticket_id.id,
            "view_mode": "form",
            "target": "current",
        }

    # ---------- SPECIFIC STATE ACTIONS ----------
    def action_submit(self):
        self.action_set_state(STATE_SUBMITTED)

    def action_approve(self):
        self.action_set_state(STATE_APPROVED)

    def action_cancel(self):
        self.action_set_state(STATE_CANCELLED)

    def action_draft(self):
        self.action_set_state(STATE_DRAFT)

    def action_sign(self):
        self.action_set_state(STATE_SIGNED)

    def action_under_review(self):
        self.action_set_state(
            STATE_UNDER_REVIEW,
        )

    def action_complete(self):
        self.action_set_state(
            STATE_COMPLETED,
        )

    def action_reject(self):
        self.action_set_state(
            STATE_REJECTED,
        )

    # ---------- OPEN SIGN REQUEST ----------
    def action_open_sign_request(self):
        self.ensure_one()
        if not self.sign_request_id:
            raise UserError("No signature request linked to this form.")
        return {
            "type": "ir.actions.act_window",
            "name": "Signature Request",
            "res_model": "sign.request",
            "res_id": self.sign_request_id.id,
            "view_mode": "form",
            "target": "current",
        }


class PersonBase(models.AbstractModel):
    _name = "form.person.base"
    _description = "Common Person Fields"

    first_name = fields.Char(string="First Name", required=True)
    middle_name = fields.Char(string="Middle Name", required=True)
    last_name = fields.Char(string="Last Name", required=True)
    full_name = fields.Char(
        string="Full Name", compute="_compute_full_name", store=True, readonly=True
    )
    age = fields.Integer(string="Age", required=True)
    gender = fields.Selection([("male", "Male"), ("female", "Female")], string="Gender")
    civil_status = fields.Selection(
        [("single", "Single"), ("married", "Married")], string="Civil Status"
    )
    birthday = fields.Date(string="Birthday")
    nationality = fields.Char(string="Nationality")
    home_mailing_address = fields.Text(string="Home Mailing Address")
    home_mailing_address_tel_no = fields.Char(string="Tel No. (Residence)")
    abroad_address = fields.Text(string="Address Abroad (If any)")
    abroad_address_tel_no = fields.Char(string="Tel No. (Abroad if any)")
    office_address = fields.Text(string="Office Address")
    office_address_tel_no = fields.Char(string="Tel No. (Office)")
    email = fields.Char(string="Email Address")
    mobile_number = fields.Char(string="Mobile Number")
    office_business = fields.Char(string="Office/Business Name")
    position = fields.Char(string="Position")
    occupation = fields.Char(string="Occupation")
    religion = fields.Char(string="Religion")

    @api.depends("first_name", "middle_name", "last_name")
    def _compute_full_name(self):
        for rec in self:
            rec.full_name = " ".join(
                filter(None, [rec.first_name, rec.middle_name, rec.last_name])
            )


class UnitOwnerInfoForm(models.AbstractModel):
    _name = "form.unit_owner_info.base"
    _description = "Unit Owner Information Form"

    unit_id = fields.Many2one(comodel_name="property.unit", string="Assigned Unit")

    spouse_info_id = fields.Many2one(
        comodel_name="form.spouse_info", string="Spouse Info"
    )
    vehicle_info_id = fields.Many2one(
        comodel_name="form.vehicle_info", string="Vehicle Info"
    )

    spouse_id = fields.Many2one(comodel_name="res.partner", string="Spouse")
    vehicle_id = fields.Many2one(comodel_name="res.partner", string="Vehicle")
