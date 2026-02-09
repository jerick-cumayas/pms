import logging

from odoo import http
from odoo.http import request

from .routes import (
    FORM_THANK_YOU_PATH,
    FORM_USER_DETAILS_PATH,
    FORM_USER_INFO_PATH,
    PORTAL_USER_DETAILS_PATH,
)

_logger = logging.getLogger(__name__)


class UserInfoController(http.Controller):
    @http.route(FORM_USER_INFO_PATH, auth="public", website=True, name="user_info_form")
    def unit_owner_info_form(self, **kwargs):
        match request.httprequest.method:
            case "GET":
                return request.render(
                    "pms.website_user_info_form",
                    {},
                )
            case "POST":
                """
                Handle Unit Owner Info website form submission
                """

                # -----------------------------
                # 1. Create Unit Owner
                # -----------------------------
                user_vals = {
                    "first_name": kwargs.get("first_name"),
                    "middle_name": kwargs.get("middle_name"),
                    "last_name": kwargs.get("last_name"),
                    "age": kwargs.get("age"),
                    "gender": kwargs.get("gender"),
                    "civil_status": kwargs.get("civil_status"),
                    "birthday": kwargs.get("birthday"),
                    "nationality": kwargs.get("nationality"),
                    "home_mailing_address": kwargs.get("home_mailing_address"),
                    "home_mailing_address_tel_no": kwargs.get(
                        "home_mailing_address_tel_no"
                    ),
                    "abroad_address": kwargs.get("abroad_address"),
                    "abroad_address_tel_no": kwargs.get("abroad_address_tel_no"),
                    "office_address": kwargs.get("office_address"),
                    "office_address_tel_no": kwargs.get("office_address_tel_no"),
                    "email": kwargs.get("email"),
                    "mobile_number": kwargs.get("mobile_number"),
                    "office_business": kwargs.get("office_business"),
                    "position": kwargs.get("position"),
                    "occupation": kwargs.get("occupation"),
                    "religion": kwargs.get("religion"),
                    "state": "submitted",
                }

                user_info = request.env["form.user_info"].sudo().create(user_vals)

                # -----------------------------
                # 2. Create Spouse (optional)
                # -----------------------------
                spouse = None
                if kwargs.get("s_first_name") and kwargs.get("s_last_name"):
                    s_vals = {
                        "first_name": kwargs.get("s_first_name"),
                        "middle_name": kwargs.get("s_middle_name"),
                        "last_name": kwargs.get("s_last_name"),
                        "age": kwargs.get("s_age"),
                        "gender": kwargs.get("s_gender"),
                        "civil_status": kwargs.get("s_civil_status"),
                        "birthday": kwargs.get("s_birthday"),
                        "nationality": kwargs.get("s_nationality"),
                        "home_mailing_address": kwargs.get("s_home_mailing_address"),
                        "email": kwargs.get("s_email"),
                        "mobile_number": kwargs.get("s_mobile_number"),
                        "occupation": kwargs.get("s_occupation"),
                        "religion": kwargs.get("s_religion"),
                    }

                    spouse = request.env["form.spouse_info"].sudo().create(s_vals)

                    user_info.write({"spouse_info_id": spouse.id})

                # -----------------------------
                # 3. Create Vehicle (optional)
                # -----------------------------
                vehicle = None
                if kwargs.get("plate_no"):
                    vehicle_vals = {
                        "brand": kwargs.get("brand"),
                        "type": kwargs.get("type"),
                        "plate_no": kwargs.get("plate_no"),
                        "colour": kwargs.get("colour"),
                    }

                    vehicle = (
                        request.env["form.vehicle_info"].sudo().create(vehicle_vals)
                    )

                    user_info.write({"vehicle_info_id": vehicle.id})

                # -----------------------------
                # 4. Redirect on success
                # -----------------------------
                return request.redirect(f"{FORM_THANK_YOU_PATH}")

    @http.route(
        [PORTAL_USER_DETAILS_PATH],
        type="http",
        auth="user",
        website=True,
    )
    def partner_profile(self, **kwargs):
        match request.httprequest.method:
            case "GET":
                partner = request.env.user.partner_id.sudo()

                if not partner.exists():
                    return request.not_found()

                data = partner.read()[0]
                _logger.info("PARTNER DATA: %s", data)

                return request.render(
                    "pms.website_partner_profile_details",
                    {
                        "partner": partner,
                    },
                )

    @http.route(
        [FORM_USER_DETAILS_PATH],
        type="http",
        auth="user",
        website=True,
    )
    def update_partner_profile(self, **kwargs):
        partner = request.env.user.partner_id.sudo()
        match request.httprequest.method:
            case "GET":
                partner = request.env.user.partner_id.sudo()

                if not partner.exists():
                    return request.not_found()

                data = partner.read()[0]
                _logger.info("PARTNER DATA: %s", data)

                return request.render(
                    "pms.website_partner_profile_update",
                    {
                        "partner": partner,
                    },
                )
            case "POST":
                allowed_fields = [
                    "first_name",
                    "middle_name",
                    "last_name",
                    "gender",
                    "civil_status",
                    "birthday",
                    "age",
                    "nationality",
                    "religion",
                    "occupation",
                    "home_mailing_address",
                    "home_mailing_address_tel_no",
                    "office_address",
                    "office_address_tel_no",
                    "abroad_address",
                    "abroad_address_tel_no",
                ]

                values = {
                    f: kwargs.get(f) or False for f in allowed_fields if f in kwargs
                }
                partner.write(values)

                return request.redirect("/my/details")
