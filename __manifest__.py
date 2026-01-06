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
        'data/announcements/sample_posts.xml',
        'data/announcements/amenities.xml',
        'data/announcements/policies.xml',
        
        'data/teams.xml',
        'data/documents.xml',

        'views/homepage.xml'
    ],
    'license': 'LGPL-3',
    'author': 'Jerick Cumayas'
}