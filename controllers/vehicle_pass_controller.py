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
    def get_vehicle_pass_form(self, **kwargs):
        return request.render("pms.website_vehicle_pass_form", {})

    @http.route(
        f"{FORM_VEHICLE_PASS_PATH}/submit",
        type="http",
        auth="user",
        website=True,
        csrf=True,
        name="vehicle_pass_form_submit",
    )
    def submit_vehicle_pass_form(self, **post):
        partner = request.env.user.partner_id

        # 1️⃣ Create Vehicle Pass record
        vehicle_pass = (
            request.env["forms.vehicle_pass"]
            .sudo()
            .create(
                {
                    "requestor_id": partner.id,
                    "application_type": post.get("application_type"),
                    "vehicle_ownership": post.get("vehicle_ownership"),
                    "type": post.get("vehicle_type"),
                    "color": post.get("vehicle_color"),
                    "plate_no": post.get("vehicle_plate_no"),
                }
            )
        )

        # 3️⃣ Vehicle attachments
        self._create_attachment(vehicle_pass, "lto_or", "LTO Official Receipt")
        self._create_attachment(vehicle_pass, "cr", "Certificate of Registration")
        self._create_attachment(
            vehicle_pass, "vehicle_photo", "Vehicle Photo with Plate Number"
        )

        # 4️⃣ Form attachments
        self._create_attachment(
            vehicle_pass, "accomplished_form", "Accomplished Application Form"
        )
        self._create_attachment(vehicle_pass, "driver_license", "Driver's License")

        # Optional attachments
        self._create_attachment(
            vehicle_pass, "notarized_dos", "Copy of Duly Notarized DOS"
        )
        self._create_attachment(
            vehicle_pass, "endorsed_homeowner", "Endorsed by Homeowner"
        )
        self._create_attachment(
            vehicle_pass, "lease_contract", "Photocopy of Lease Contract"
        )
        self._create_attachment(vehicle_pass, "company_cert", "Company Certification")

        return request.redirect(FORM_THANK_YOU_PATH)

    def _create_attachment(self, record, field_name, attachment_name):
        """Create an ir.attachment for the given record."""
        file = request.httprequest.files.get(field_name)
        if file:
            request.env["ir.attachment"].sudo().create(
                {
                    "name": attachment_name or file.filename,
                    "type": "binary",
                    "datas": base64.b64encode(file.read()),
                    "res_model": record._name,
                    "res_id": record.id,
                    "mimetype": file.content_type,
                }
            )
