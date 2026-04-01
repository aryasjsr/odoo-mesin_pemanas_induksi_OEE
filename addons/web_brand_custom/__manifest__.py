{
    'name': 'Web Brand — OEE Theme',
    'version': '18.0.1.0.0',
    'category': 'Website/Theme',
    'summary': 'Global OEE brand theming for entire Odoo 18 backend UI',
    'description': """
        Overrides all Odoo 18 backend colours, fonts, and component
        styles to match brandGuidelines.md (Primary Blue #1E3A8A,
        Accent Blue #3B82F6, Inter/Roboto font family, etc.).
        Covers: navbar, sidebar, login screen, home menu, control panel,
        forms, lists, kanban, chatter, status bar, settings, and more.
    """,
    'author': 'Arya',
    'depends': ['web'],
    'data': [
        'views/webclient_templates.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'web_brand_custom/static/src/scss/brand_variables.scss'),
        ],
        'web.assets_backend': [
            'web_brand_custom/static/src/scss/brand_backend.scss',
        ],
        'web.assets_frontend': [
            'web_brand_custom/static/src/scss/brand_login.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
