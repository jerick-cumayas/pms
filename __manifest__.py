{
    'name': 'PMS',
    'version': '1.0',
    'category': 'Services',
    'depends': [
        'base', 
        'contacts', 
        'account', 
        'documents',
        'helpdesk',
        'website', 
        'website_blog',
        'web',
        'sign',
        'portal'
    ],
    'data': [ 
        'security/ir.model.access.csv',
        'data/announcements/sample_posts.xml',
        'data/announcements/amenities.xml',
        'data/announcements/policies.xml',
        
        'data/teams.xml',
        'data/documents.xml',

        'views/homepage.xml',
        # 'views/sample.xml',
        # 'views/sample2.xml',
        # 'views/form.xml',
        # 'views/thank_you.xml',
        # 'views/sample4.xml',

        'views/pdf/amenities_sign.xml',
        'views/pdf/amenities_template.xml',
        'views/pdf/pet_registration_template.xml',
        'views/pdf/unit_owner_info_template.xml',
        'views/pdf/tenant_info_template.xml',

        'views/forms/amenities_form.xml',
        'views/forms/pet_registration_form.xml',
        'views/forms/unit_owner_info_form.xml',
        'views/forms/tenant_info_form.xml',

        'views/website/website_modifications.xml',
        'views/website/portal_modifications.xml',
        
        'views/website/homepage/portal_invoices_table.xml',
        'views/website/homepage/portal_tickets_table.xml',
        'views/website/homepage/portal_signatures_table.xml',

        'views/website/homepage.xml',
        'views/website/forms_homepage.xml',
        'views/website/amenities_form_web.xml',
        'views/website/pet_registration_web.xml',
        'views/website/base/person_base_form_web.xml',
        'views/website/base/spouse_person_base_form_web.xml',
        'views/website/base/vehicle_base_form_web.xml',
        'views/website/base/multiple_person_base_form_web.xml',
        'views/website/unit_owner_info_form_web.xml',
        'views/website/tenant_info_form_web.xml',
        'views/website/thank_you.xml',

        

        'views/menu.xml'

    ],
    'license': 'LGPL-3',
    'author': 'Jerick Cumayas'
}