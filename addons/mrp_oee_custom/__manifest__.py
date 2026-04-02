{
    'name': 'MRP OEE Custom',
    'version': '18.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'OEE Dashboard with real-time OWL components for Induction Heating Machine',
    'description': """
        Calculates OEE (Availability, Performance, Quality) as computed fields
        on mrp.workcenter. Provides a real-time OWL dashboard with circular
        gauges and 5-second auto-polling.
    """,
    'author': 'Arya',
    'depends': ['mrp', 'mrp_shopfloor_custom'],
    'data': [
        'security/ir.model.access.csv',
        'views/oee_dashboard_action.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'mrp_oee_custom/static/src/scss/brand_variables.scss'),
        ],
        'web.assets_backend': [
            'mrp_oee_custom/static/src/scss/brand_backend.scss',
            'mrp_oee_custom/static/src/css/oee_dashboard.css',
            'mrp_oee_custom/static/src/js/oee_dashboard.js',
            'mrp_oee_custom/static/src/js/oee_dashboard.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
