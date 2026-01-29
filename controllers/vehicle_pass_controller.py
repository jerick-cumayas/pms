import base64

from odoo import http
from odoo.http import request

from .routes import FORM_THANK_YOU_PATH, FORM_VEHICLE_PASS_PATH


class VehiclePassFormController(http.Controller):
    @http.route(
        f"{FORM_VEHICLE_PASS_PATH}",
        auth="user",
        website=True,
        name="vehicle_pass_form",
    )
    def vehicle_pass_form(self, **kwargs):
        return request.render("pms.website_vehicle_pass_form", {})

    @http.route(
        f"{FORM_VEHICLE_PASS_PATH}/submit",
        type="http",
        auth="user",
        website=True,
        csrf=True,
        name="vehicle_pass_form_submit",
    )
    def vehicle_pass_form_submit(self, **post):
        logged_user = request.env.user.partner_id

        vals = {
            "requestor_id": logged_user.id,
            "application_type": post.get("application_type"),
            "vehicle_ownership": post.get("vehicle_ownership"),
        }

        # Create the record
        vehicle_pass = request.env["forms.vehicle_pass"].sudo().create(vals)

        # Handle attachments
        attachment_fields = [
            "lto_cr_attachment_ids",
            "plate_no_attachment_ids",
            "driver_license_attachment_ids",
            "deed_of_sale_attachment_ids",
            "homeowner_endorsement_attachment_ids",
        ]

        for field in attachment_fields:
            files = request.httprequest.files.getlist(field)
            attachments = []
            for file in files:
                data = file.read()
                attachment = (
                    request.env["ir.attachment"]
                    .sudo()
                    .create(
                        {
                            "name": file.filename,
                            "datas": base64.b64encode(data),
                            "res_model": "forms.vehicle_pass",
                            "res_id": vehicle_pass.id,
                            "type": "binary",
                        }
                    )
                )
                attachments.append(attachment.id)
            if attachments:
                vehicle_pass.write({field: [(6, 0, attachments)]})

        return request.redirect(f"{FORM_THANK_YOU_PATH}")
