from odoo import http
from odoo.http import request
from .routes import FORM_AMENITIES_PATH, FORM_THANK_YOU_PATH

class AmenitiesFormController(http.Controller):
    @http.route(
        f'{FORM_AMENITIES_PATH}', 
        auth='public', 
        website=True, 
        name='amenities_form'
    )
    def amenities_form(self, **kwargs):
        # Logged user
        logged_user = request.env.user.partner_id
        # Display the contact form
        form_model = request.env['form.amenities']
        # Call the function to get eligible requestors
        requestors = form_model.get_requestors()
        return request.render('pms.website_form_amenities', {
            'user': logged_user,
            'requestors': requestors,
        })
    
    @http.route(
        f'{FORM_AMENITIES_PATH}/submit', 
        type='http', 
        auth="public", 
        website=True, 
        csrf=True, 
        name='amenities_form_submit'
    )
    def amenities_form_submit(self, **post):
        # Create record in form.amenities
        guest_ids = request.httprequest.form.getlist('guest_ids')
        guest_ids = [int(g) for g in guest_ids]
        print(f"GUESTIDS {guest_ids}")
        vals = {
            'requestor_id': post.get('requestor_id'),
            'sponsor_id': post.get('sponsor_id') or False,
            'activity_type': post.get('activity_type'),
            'relation': post.get('relation'),
            'date_from': post.get('date_from'),
            'date_to': post.get('date_to'),
            'guest_ids': [(6, 0, guest_ids)],
        }

        request.env['form.amenities'].sudo().create(vals)
        return request.redirect(f'{FORM_THANK_YOU_PATH}')
    
    # | Command       | Meaning                                                       |
    # | ------------- | ------------------------------------------------------------- |
    # | (6, 0, [ids]) | Replace all existing linked records with this new list of IDs |
    # | (4, id)       | Add a single record to the relation                           |
    # | (3, id)       | Remove a single record from the relation                      |
    # | (5, 0, 0)     | Remove all linked records                                     |
