from odoo import http
from odoo.http import request
from .routes import FORM_THANK_YOU_PATH

class FormController(http.Controller):
    @http.route(f'{FORM_THANK_YOU_PATH}', auth='public', website=True)
    def thank_you(self, **kwargs):
        # Display the thank-you page
        return request.render('pms.website_request_thankyou', {})