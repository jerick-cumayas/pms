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

        'views/forms/amenities_form.xml',
        'views/forms/pet_registration_form.xml',

        'views/website/amenities_form_web.xml',
        'views/website/pet_registration_web.xml',
        'views/website/thank_you.xml',

        'views/menu.xml'

    ],
    'license': 'LGPL-3',
    'author': 'Jerick Cumayas'
}