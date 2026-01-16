# my_module/controllers/main.py
from odoo import http
from odoo.http import request
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

class WebsiteHomeRedirect(http.Controller):

    @http.route('/', type='http', auth='user', website=True)
    def homepage(self, **kwargs):
        page = kwargs.get('page', 'home')
        partner = request.env.user.partner_id

        # Always fetch counts for sidebar
        invoice_count = request.env['account.move'].search_count([
            ('partner_id', '=', partner.id),
            ('move_type', '=', 'out_invoice'),
            ('state', 'in', ['posted', 'draft'])
        ])
        ticket_count = request.env['helpdesk.ticket'].search_count([
            ('partner_id', '=', partner.id)
        ])
        signature_count = request.env['sign.request.item'].sudo().search_count([
            ('partner_id', '=', partner.id)
        ])

        events = request.env['event.event'].sudo().search(
            [], order='date_begin asc', limit=3
        )

        blogs = request.env['blog.post'].sudo().search(
            [('website_published', '=', True)],
            order='post_date desc',
            limit=10
        )
    
    # @http.route('/my', type='http', auth='user', website=True)
    # def redirect_my(self, **kw):
    #     return request.redirect('/')

        # Fetch detailed records depending on page
        # match page:
        #     case "invoices":
        #         invoices = request.env['account.move'].search([
        #             ('partner_id', '=', partner.id),
        #             ('move_type', '=', 'out_invoice'),
        #             ('state', 'in', ['posted', 'draft'])
        #         ])
        #     case "tickets":
        #         tickets = request.env['helpdesk.ticket'].search([
        #             ('partner_id', '=', partner.id)
        #         ])
        #     case "signatures":
        #         signatures = request.env['sign.request.item'].sudo().search([
        #             ('partner_id', '=', partner.id)
        #         ])
        #     case "home":
        #         # nothing extra, just show dashboard
        #         pass

        return request.render('pms.custom_homepage', {
            'page': page,
            'invoice_count': invoice_count,
            'ticket_count': ticket_count,
            'signature_count': signature_count,
            'events': events,
            'blogs': blogs,
        })
    

class CustomLoginRedirect(AuthSignupHome):

    @http.route('/web/login', type='http', auth='public', website=True)
    def web_login(self, redirect=None, **kw):
        # Force redirect to homepage
        redirect = '/'  # always redirect to /
        return super(CustomLoginRedirect, self).web_login(redirect=redirect, **kw)


class BlogUserOnly(WebsiteBlog):

    @http.route(['/blog', '/blog/<model("blog.post"):post>'], type='http', auth='user', website=True)
    def blog(self, post=None, tag=None, author=None, **kwargs):
        # restrict access to logged-in users
        return super(BlogUserOnly, self).blog(post=post, tag=tag, author=author, **kwargs)
