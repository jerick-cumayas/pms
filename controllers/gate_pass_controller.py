from odoo import http
from odoo.http import request

from .routes import FORM_GATE_PASS_PATH, FORM_THANK_YOU_PATH


class GatePassFormController(http.Controller):
    @http.route(
        f"{FORM_GATE_PASS_PATH}", auth="user", website=True, name="gate_pass_form"
    )
    def gate_pass_form(self, **kwargs):
        return request.render(
            "pms.website_gate_pass_form",
        )

    @http.route(
        f"{FORM_GATE_PASS_PATH}/submit",
        type="http",
        auth="user",
        website=True,
        csrf=True,
        name="gate_pass_form_submit",
    )
    def gate_pass_form_submit(self, **post):
        """
        Handle Gate Pass Form submission from website
        """
        GatePass = request.env["forms.gate_pass"].sudo()
        GatePassItem = request.env["forms.gate_pass_item"].sudo()

        # Create the main gate pass record
        gate_pass = GatePass.create(
            {
                "cn_no": post.get("cn_no"),
                "authorized_carrier": post.get("authorized_carrier"),
                "company": post.get("company"),
                "transaction": post.get("transaction"),
                "purpose": post.get("purpose"),
            }
        )

        # Handle multiple items
        descriptions = request.httprequest.form.getlist("item_description[]")
        quantities = request.httprequest.form.getlist("item_quantity[]")
        remarks = request.httprequest.form.getlist("item_remarks[]")

        for desc, qty, rem in zip(descriptions, quantities, remarks):
            if desc.strip():  # Only create items with description
                GatePassItem.create(
                    {
                        "gate_pass_id": gate_pass.id,
                        "description": desc,
                        "quantity": int(qty or 0),
                        "remarks": rem,
                    }
                )

        return request.redirect(FORM_THANK_YOU_PATH)
