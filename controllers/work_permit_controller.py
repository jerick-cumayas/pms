from odoo import http
from odoo.http import request

from .routes import FORM_THANK_YOU_PATH, FORM_WORK_PERMIT_PATH


class WorkPermitWebsiteController(http.Controller):
    @http.route(
        FORM_WORK_PERMIT_PATH,
        type="http",
        auth="user",
        website=True,
        name="work_permit_form",
    )
    def work_permit_form(self, **kwargs):
        work_types = request.env["form.work_types"].sudo().search([])
        work_scopes = request.env["form.work_scopes"].sudo().search([])
        checklist_items = (
            request.env["form.work_permit.checklist.item"].sudo().search([])
        )
        return request.render(
            "pms.website_work_permit",
            {
                "work_types": work_types,
                "work_scopes": work_scopes,
                "checklist_items": checklist_items,
            },
        )

    # =========================
    # SUBMIT FORM
    # =========================
    @http.route(
        f"{FORM_WORK_PERMIT_PATH}/submit",
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
        csrf=True,
        name="work_permit_form_submit",
    )
    def work_permit_form_submit(self, **post):
        # -------------------------
        # Create Work Permit
        # -------------------------
        permit = (
            request.env["form.work_permit"]
            .sudo()
            .create(
                {
                    "contractor": post.get("contractor"),
                    "contractor_no": post.get("contractor_no"),
                    "estimated_completion": post.get("estimated_completion"),
                    "work_details": post.get("work_details"),
                    "work_type_ids": [(6, 0, self._get_ids(post, "work_type_ids"))],
                    "work_scope_ids": [(6, 0, self._get_ids(post, "work_scope_ids"))],
                }
            )
        )

        # -------------------------
        # Create Checklist Lines
        # -------------------------
        # done_item_ids = set(map(int, post.getlist("checklist_done")))
        done_item_ids = []

        checklist_items = (
            request.env["form.work_permit.checklist.item"].sudo().search([])
        )

        for item in checklist_items:
            request.env["form.work_permit.checklist.line"].sudo().create(
                {
                    "permit_id": permit.id,
                    "item_id": item.id,
                    "done": item.id in done_item_ids,
                    "remarks": post.get(f"remarks_{item.id}"),
                }
            )

        # -------------------------
        # Redirect / Thank You
        # -------------------------
        return request.render(FORM_THANK_YOU_PATH)

    # =========================
    # HELPERS
    # =========================
    def _get_ids(self, post, field_name):
        """
        Safely extract many2many IDs from website POST
        """
        return [int(x) for x in post.getlist(field_name) if x.isdigit()]
