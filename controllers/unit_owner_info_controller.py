from odoo import http
from odoo.http import request
from .routes import FORM_UNIT_OWNER_INFO_PATH, FORM_THANK_YOU_PATH

class UnitOwnerInfoFormController(http.Controller):
    @http.route(
        f'{FORM_UNIT_OWNER_INFO_PATH}', 
        auth='public', 
        website=True, 
        name='unit_owner_info_form'
    )
    def unit_owner_info_form(self, **kwargs):
        # Logged user
        logged_user = request.env.user.partner_id
        return request.render('pms.website_unit_owner_info_form', {
            'user': logged_user,
        })
    
    @http.route(
        f'{FORM_UNIT_OWNER_INFO_PATH}/submit', 
        type='http', 
        auth="public", 
        website=True, 
        csrf=True, 
        name='unit_owner_info_form_submit'
    )
    def unit_owner_info_form_submit(self, **post):
        """
        Handle Unit Owner Info website form submission
        """

        # -----------------------------
        # 1. Create Unit Owner
        # -----------------------------
        unit_owner_vals = {
            'first_name': post.get('first_name'),
            'middle_name': post.get('middle_name'),
            'last_name': post.get('last_name'),
            'age': post.get('age'),
            'gender': post.get('gender'),
            'civil_status': post.get('civil_status'),
            'birthday': post.get('birthday'),
            'nationality': post.get('nationality'),
            'home_mailing_address': post.get('home_mailing_address'),
            'home_mailing_address_tel_no': post.get('home_mailing_address_tel_no'),
            'abroad_address': post.get('abroad_address'),
            'abroad_address_tel_no': post.get('abroad_address_tel_no'),
            'office_address': post.get('office_address'),
            'office_address_tel_no': post.get('office_address_tel_no'),
            'email': post.get('email'),
            'mobile_number': post.get('mobile_number'),
            'office_business': post.get('office_business'),
            'position': post.get('position'),
            'occupation': post.get('occupation'),
            'religion': post.get('religion'),
        }

        unit_owner = request.env['form.unit_owner_info'].sudo().create(unit_owner_vals)

        # -----------------------------
        # 2. Create Spouse (optional)
        # -----------------------------
        spouse = None
        if post.get('s_first_name') and post.get('s_last_name'):
            s_vals = {
                'first_name': post.get('s_first_name'),
                'middle_name': post.get('s_middle_name'),
                'last_name': post.get('s_last_name'),
                'age': post.get('s_age'),
                'gender': post.get('s_gender'),
                'civil_status': post.get('s_civil_status'),
                'birthday': post.get('s_birthday'),
                'nationality': post.get('s_nationality'),
                'home_mailing_address': post.get('s_home_mailing_address'),
                'email': post.get('s_email'),
                'mobile_number': post.get('s_mobile_number'),
                'occupation': post.get('s_occupation'),
                'religion': post.get('s_religion'),
            }

            spouse = request.env['form.spouse_info'].sudo().create(s_vals)

            unit_owner.write({
                'spouse_info_id': spouse.id
            })

        # -----------------------------
        # 3. Create Vehicle (optional)
        # -----------------------------
        vehicle = None
        if post.get('plate_no'):
            vehicle_vals = {
                'brand': post.get('brand'),
                'type': post.get('type'),
                'plate_no': post.get('plate_no'),
                'colour': post.get('colour'),
            }

            vehicle = request.env['form.vehicle_info'].sudo().create(vehicle_vals)

            unit_owner.write({
                'vehicle_info_id': vehicle.id
            })

        # -----------------------------
        # 4. Redirect on success
        # -----------------------------
        return request.redirect(f'{FORM_THANK_YOU_PATH}')