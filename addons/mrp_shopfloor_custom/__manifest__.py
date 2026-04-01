{
    'name': 'MRP Shopfloor Custom',
    'version': '18.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Custom Shop Floor tablet UI with dark mode for Induction Heating Machine',
    'description': """
        Replaces Odoo Enterprise Shop Floor module.
        - Dark mode OWL tablet interface with card view
        - Operator sidebar with MO assignment filtering
        - Start/Block/Resume/Close production buttons
        - Auto clock-in on Start
        - Block workcenter with loss reason popup
        - Production qty and scrap recording
        - Shopfloor Operator access group
        - HTTP API for Modbus Middleware integration
    """,
    'author': 'Arya',
    'depends': ['mrp', 'hr'],
    'data': [
        'security/shopfloor_groups.xml',
        'security/ir.model.access.csv',
        'views/mrp_workorder_views.xml',
        'views/shopfloor_action.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mrp_shopfloor_custom/static/src/css/shopfloor.css',
            'mrp_shopfloor_custom/static/src/js/shopfloor_main.js',
            'mrp_shopfloor_custom/static/src/js/shopfloor_main.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

