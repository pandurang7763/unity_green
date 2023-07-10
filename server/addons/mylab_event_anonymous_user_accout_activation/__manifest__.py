{
    'name': 'Mylab Event Anonymous User Account Activation',
    'version': '16.0.0.0',
    'depends': ['web','auth_signup','mylab_event','website_event'],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'data': [
        'data/user_registration.xml',
        'view/user_job_title.xml',
        'view/attendee_title.xml',
    ]
}