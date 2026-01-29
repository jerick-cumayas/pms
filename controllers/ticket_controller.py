from odoo import http
from odoo.http import request

from .routes import FORM_THANK_YOU_PATH, TICKET_BASE_PATH


class TicketController(http.Controller):
    @http.route(
        [TICKET_BASE_PATH, f"{TICKET_BASE_PATH}/submit"],
        type="http",
        auth="public",
        website=True,
        methods=["GET", "POST"],
    )
    def submit_ticket(self, **post):
        match request.httprequest.method:
            case "GET":
                teams = request.env["helpdesk.team"].sudo().search([])
                return request.render("pms.website_ticket_submission", {"teams": teams})
            case "POST":
                ticket_obj = request.env["helpdesk.ticket"]

                logged_user = request.env.user.partner_id
                team_id = int(post.get("team_id") or 1)

                vals = {
                    "name": post.get("subject"),
                    "description": post.get("description"),
                    "partner_id": logged_user.id,
                    "team_id": team_id,
                }
                ticket_obj.sudo().create(vals)

                return request.redirect(f"{FORM_THANK_YOU_PATH}")
