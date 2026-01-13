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

        'views/forms/amenities_form.xml',
        'views/forms/pet_registration_form.xml',
        'views/forms/unit_owner_info_form.xml',
        'views/forms/tenant_info_form.xml',

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