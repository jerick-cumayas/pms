from odoo import http
from odoo.http import request

# class WebsiteRequestController(http.Controller):

#     @http.route('/website-request', auth='public', website=True)
#     def website_request_page(self, **kw):
#         return request.render('pms.website_request_page')

class WebsiteRequestController(http.Controller):

    @http.route('/contact-us', auth='public', website=True)
    def contact_form(self, **kwargs):
        # Display the contact form
        return request.render('pms.website_request_form', {})
    
    @http.route('/contact-us/submit', type='http', auth="public", website=True, csrf=True)
    def submit_request(self, **post):
        request.env['website.request'].sudo().create({
            'name': post.get('name'),
            'email': post.get('email'),
            'message': post.get('message'),
        })
        return request.redirect('/contact-us/thank-you')
    
    @http.route('/contact-us/thank-you', auth='public', website=True)
    def thank_you(self, **kwargs):
        # Display the thank-you page
        return request.render('pms.website_request_thankyou', {})

    # @http.route('/contact-us/submit', type='http', auth='public', website=True, methods=['POST'])
    # def contact_form_submit(self, **kwargs):
    #     # Create a record in website.request
    #     if kwargs.get('name'):
    #         request.env['website.request'].sudo().create({
    #             'name': kwargs.get('name'),
    #             'email': kwargs.get('email'),
    #             'message': kwargs.get('message'),
    #         })
    #     # Show thank you page
    #     return request.render('pms.website_request_thankyou', {})
