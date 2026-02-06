import base64

from odoo import http
from odoo.http import request

from .routes import FORM_CONCERN_SLIP_PATH, FORM_THANK_YOU_PATH


class ConcernSlipController(http.Controller):
    @http.route(
        FORM_CONCERN_SLIP_PATH, auth="public", website=True, name="user_info_form"
    )
    def unit_owner_info_form(self, **kwargs):
        match request.httprequest.method:
            case "GET":
                return request.render("pms.website_concern_slip", {})
            case "POST":
                # ------------------------------------------------------------
                # Validate requester
                # ------------------------------------------------------------
                partner = request.env.user.partner_id

                # ------------------------------------------------------------
                # Create Concern Slip Form
                # ------------------------------------------------------------
                concern = (
                    request.env["forms.concern_slip"]
                    .sudo()
                    .create(
                        {
                            "requester_id": partner.id,
                            "subject": kwargs.get("subject"),
                            "description": kwargs.get("description"),
                            "concern_type": kwargs.get("concern_type"),
                            "state": "submitted",
                        }
                    )
                )

                # ------------------------------------------------------------
                # Handle Attachments (if any)
                # ------------------------------------------------------------
                files = request.httprequest.files.getlist("attachment_ids")
                attachments = []

                for file in files:
                    if not file.filename:
                        continue
                    data = file.read()
                    attachment = (
                        request.env["ir.attachment"]
                        .sudo()
                        .create(
                            {
                                "name": file.filename,
                                "datas": base64.b64encode(data),
                                "res_model": "form.concern_slip",
                                "res_id": concern.id,
                                "type": "binary",
                            }
                        )
                    )
                    attachments.append(attachment.id)

                if attachments:
                    concern.write({"attachment_ids": [(6, 0, attachments)]})

                # ------------------------------------------------------------
                # Create Helpdesk Ticket
                # ------------------------------------------------------------
                team = (
                    request.env["helpdesk.team"]
                    .sudo()
                    .search([("name", "ilike", "Concern Slip")], limit=1)
                )

                ticket = (
                    request.env["helpdesk.ticket"]
                    .sudo()
                    .create(
                        {
                            "name": concern.subject,
                            "description": f"""
        Concern Type: {concern.concern_type}

        {concern.description}
                            """.strip(),
                            "partner_id": concern.requester_id.id,
                            "team_id": team.id if team else False,
                            "form_model": concern._name,
                            "form_id": concern.id,
                        }
                    )
                )

                # ------------------------------------------------------------
                # Link ticket back to the form
                # ------------------------------------------------------------
                concern.write(
                    {
                        "helpdesk_ticket_id": ticket.id,
                    }
                )

                # ------------------------------------------------------------
                # Redirect to thank-you page
                # ------------------------------------------------------------
                return request.redirect(FORM_THANK_YOU_PATH)
