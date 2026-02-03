from odoo import http
from odoo.http import request

from .routes import FORM_BASE_PATH, FORM_THANK_YOU_PATH, FORM_USER_INFO_PATH


class FormController(http.Controller):
    @http.route(f"{FORM_BASE_PATH}", auth="public", website=True)
    def display_homepage(self, **kwargs):
        # Display the form homepage
        return request.render(f"pms.website_form_homepage", {})

    @http.route(f"{FORM_THANK_YOU_PATH}", auth="public", website=True)
    def display_thankyou_page(self, **kwargs):
        # Display the thank-you page
        return request.render("website_helpdesk.ticket_submited", {})
