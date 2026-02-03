from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FormBase(models.AbstractModel):
    _name = "form.base"
    _description = "Base Model"

    # ---------- STATES ----------
    STATE_TRANSITIONS = {
        "draft": ["submitted", "cancelled"],
        "submitted": ["approved", "under_review", "rejected"],
        "approved": ["signed", "rejected"],
        "under_review": ["completed", "cancelled"],
        "completed": ["draft"],
        "signed": [],
        "rejected": ["draft"],
        "cancelled": ["draft"],
    }

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("under_review", "Under Review"),
            ("approved", "Approved"),
            ("signed", "Signed"),
            ("completed", "Completed"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
    )

    # ---------- SIGNATURE FIELDS ----------
    approval_date = fields.Datetime(string="Approval Date", copy=False)
    approved_by = fields.Many2one("res.users", string="Approved By", copy=False)
    sign_request_id = fields.Many2one(
        "sign.request", string="Signature Request", copy=False
    )

    reject_date = fields.Datetime(string="Reject Date")
    rejected_by = fields.Many2one("res.users", string="Rejected By", copy=False)

    review_date = fields.Datetime(string="Review Date")
    review_by = fields.Many2one("res.users", string="Reviewed By", copy=False)

    completed_date = fields.Datetime(string="Completed Date")
    completed_by = fields.Many2one("res.users", string="Completed By", copy=False)

    # ---------- COMPUTED PERMISSIONS FOR BUTTONS ----------
    can_submit = fields.Boolean(compute="_compute_allowed_actions", store=False)
    can_under_review = fields.Boolean(compute="_compute_allowed_actions", store=False)
    can_complete = fields.Boolean(compute="_compute_allowed_actions", store=False)
    can_reject = fields.Boolean(compute="_compute_allowed_actions", store=False)
    can_approve = fields.Boolean(compute="_compute_allowed_actions", store=False)
    can_cancel = fields.Boolean(compute="_compute_allowed_actions", store=False)
    can_draft = fields.Boolean(compute="_compute_allowed_actions", store=False)
    can_sign = fields.Boolean(compute="_compute_allowed_actions", store=False)

    is_locked = fields.Boolean(compute="_compute_is_locked")
    review_section_locked = fields.Boolean(compute="_compute_is_locked")

    @api.depends("state")
    def _compute_is_locked(self):
        for rec in self:
            # The whole form is locked if completed or cancelled
            rec.is_locked = rec.state in [
                "completed",
                "under_review",
                "cancelled",
                "signed",
                "rejected",
            ]

            # Review section is editable only in under_review
            rec.review_section_locked = rec.state != "under_review"

    def _compute_allowed_actions(self):
        for rec in self:
            transitions = self.STATE_TRANSITIONS.get(rec.state, [])
            rec.can_submit = "submitted" in transitions
            rec.can_under_review = "under_review" in transitions
            rec.can_complete = "completed" in transitions
            rec.can_reject = "rejected" in transitions
            rec.can_approve = "approved" in transitions
            rec.can_cancel = "cancelled" in transitions
            rec.can_draft = "draft" in transitions
            rec.can_sign = "signed" in transitions

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

    # ---------- SPECIFIC STATE ACTIONS ----------
    def action_submit(self):
        self.action_set_state("submitted")

    def action_approve(self):
        self.action_set_state(
            "approved",
            approval_date=fields.Datetime.now(),
            approved_by=self.env.user.id,
        )

    def action_cancel(self):
        self.action_set_state("cancelled")

    def action_draft(self):
        self.action_set_state("draft")

    def action_sign(self):
        self.action_set_state("signed")

    def action_under_review(self):
        self.action_set_state(
            "under_review",
            review_date=fields.Datetime.now(),
            review_by=self.env.user.id,
        )

    def action_complete(self):
        self.action_set_state(
            "completed",
            completed_date=fields.Datetime.now(),
            completed_by=self.env.user.id,
        )

    def action_reject(self):
        self.action_set_state(
            "rejected",
            reject_date=fields.Datetime.now(),
            rejected_by=self.env.user.id,
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
