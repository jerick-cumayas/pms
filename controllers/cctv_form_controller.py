from odoo import http
from odoo.http import request

from .routes import FORM_CCTV_REQUEST_PATH, FORM_THANK_YOU_PATH


class CCTVRequestFormController(http.Controller):
    @http.route(
        f"{FORM_CCTV_REQUEST_PATH}", auth="user", website=True, name="amenities_form"
    )
    def cctv_request_form(self, **kwargs):
        return request.render(
            "pms.website_cctv_request_form",
        )

    @http.route(
        f"{FORM_CCTV_REQUEST_PATH}/submit",
        type="http",
        auth="user",
        website=True,
        csrf=True,
        name="cctv_request_form_submit",
    )
    def cctv_request_form_submit(self, **post):
        """
        Handle CCTV Request submission from website
        """
        partner = request.env.user.partner_id

        values = {
            "requestor_id": partner.id,
            "incident_datetime": post.get("incident_datetime"),
            "location": post.get("location"),
            "camera_number": post.get("camera_number"),
            "purpose": post.get("purpose"),
            "description": post.get("description"),
        }

        request.env["forms.cctv"].sudo().create(values)

        return request.redirect(FORM_THANK_YOU_PATH)
