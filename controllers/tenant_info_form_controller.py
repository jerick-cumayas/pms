from odoo import http
from odoo.http import request
from .routes import FORM_TENANT_INFO_PATH, FORM_THANK_YOU_PATH

class TenantInfoFormController(http.Controller):
    @http.route(
        f'{FORM_TENANT_INFO_PATH}', 
        auth='public', 
        website=True, 
        name='tenant_info_form'
    )
    def unit_owner_info_form(self, **kwargs):
        # Logged user
        logged_user = request.env.user.partner_id
        return request.render('pms.website_tenant_info_form', {
            'user': logged_user,
        })
    
    @http.route(
        f'{FORM_TENANT_INFO_PATH}/submit', 
        type='http', 
        auth="public", 
        website=True, 
        csrf=True, 
        name='tenant_info_form_submit'
    )
    def unit_owner_info_form_submit(self, **post):
        """
        Handle Tenant Info website form submission
        """

        # -----------------------------
        # 1. Create Tenant
        # -----------------------------
        tenant_vals = {
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

        tenant = request.env['form.tenant_info'].sudo().create(tenant_vals)
        
        # -----------------------------
        # 2. Create Tenant Spouse (Optional)
        # -----------------------------
        spouse = None
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

            tenant.write({
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

            tenant.write({
                'vehicle_info_id': vehicle.id
            })

        # -----------------------------
        # 4. Tenant House Members
        # -----------------------------
        members_first_names = request.httprequest.form.getlist('first_name[]')
        members_middle_names = request.httprequest.form.getlist('middle_name[]')
        members_last_names = request.httprequest.form.getlist('last_name[]')
        members_ages = request.httprequest.form.getlist('age[]')
        members_genders = request.httprequest.form.getlist('gender[]')
        members_civil_statuses = request.httprequest.form.getlist('civil_status[]')
        members_birthdays = request.httprequest.form.getlist('birthday[]')
        members_nationalities = request.httprequest.form.getlist('nationality[]')
        members_home_mailing_addresses = request.httprequest.form.getlist('home_mailing_address[]')
        members_home_mailing_address_tel_nos = request.httprequest.form.getlist('home_mailing_address_tel_no[]')
        members_abroad_addresses = request.httprequest.form.getlist('abroad_address[]')
        members_abroad_address_tel_nos = request.httprequest.form.getlist('abroad_address_tel_no[]')
        members_office_addresses = request.httprequest.form.getlist('office_address[]')
        members_office_addresses_tel_nos = request.httprequest.form.getlist('office_address_tel_no[]')
        members_emails = request.httprequest.form.getlist('email[]')
        members_mobile_numbers = request.httprequest.form.getlist('mobile_number[]')
        members_office_businesses = request.httprequest.form.getlist('office_business[]')
        members_positions = request.httprequest.form.getlist('position[]')
        members_occupations = request.httprequest.form.getlist('occupation[]')
        members_religions = request.httprequest.form.getlist('religion[]')
        
        rows = zip(
            members_first_names,
            members_middle_names,
            members_last_names,
            members_ages,
            members_genders,
            members_civil_statuses,
            members_birthdays,
            members_nationalities,
            members_home_mailing_addresses,
            members_home_mailing_address_tel_nos,
            members_abroad_addresses,
            members_abroad_address_tel_nos,
            members_office_addresses,
            members_office_addresses_tel_nos,
            members_emails,
            members_mobile_numbers,
            members_office_businesses,
            members_positions,
            members_occupations,
            members_religions,
        )
        
        tenant_member_model = request.env['form.tenant_house_member'].sudo()
        
        for (
            first_name,
            middle_name,
            last_name,
            age,
            gender,
            civil_status,
            birthday,
            nationality,
            home_addr,
            home_tel,
            abroad_addr,
            abroad_tel,
            office_addr,
            office_tel,
            email,
            mobile,
            office_business,
            position,
            occupation,
            religion,
        ) in rows:

            # skip empty rows
            if not first_name and not last_name:
                continue

            tenant_member_model.create({
                'tenant_id': tenant.id,
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name,
                'age': age or False,
                'gender': gender,
                'civil_status': civil_status,
                'birthday': birthday or False,
                'nationality': nationality,
                'home_mailing_address': home_addr,
                'home_mailing_address_tel_no': home_tel,
                'abroad_address': abroad_addr,
                'abroad_address_tel_no': abroad_tel,
                'office_address': office_addr,
                'office_address_tel_no': office_tel,
                'email': email,
                'mobile_number': mobile,
                'office_business': office_business,
                'position': position,
                'occupation': occupation,
                'religion': religion,
            })
        
        # for i in range(len(members_first_names)):
        #     member_vals = {
        #         'tenant_id': tenant.id,
        #         'first_name': members_first_names[i],
        #         'middle_name': members_middle_names[i],
        #         'last_name': members_last_names[i],
        #         'age': members_ages[i],
        #         'gender': members_genders[i],
        #         'civil_status': members_civil_statuses[i],
        #         'birthday': members_birthdays[i],
        #         'nationality': members_nationalities[i],
        #         'home_mailing_address': members_home_mailing_addresses[i],
        #         'home_mailing_address_tel_no': members_home_mailing_address_tel_nos[i],
        #         'abroad_address': members_abroad_addresses[i],
        #         'abroad_address_tel_no': members_abroad_address_tel_nos[i],
        #         'office_address': members_office_addresses[i],
        #         'office_address_tel_no': members_office_addresses_tel_nos[i],
        #         'email': members_emails[i],
        #         'mobile_number': members_mobile_numbers[i],
        #         'office_business': members_office_businesses[i],
        #         'position': members_positions[i],
        #         'occupation': members_occupations[i],
        #         'religion': members_religions[i],
        #     } 
        #     tenant_member_model.create(member_vals)

        return request.redirect(f'{FORM_THANK_YOU_PATH}')