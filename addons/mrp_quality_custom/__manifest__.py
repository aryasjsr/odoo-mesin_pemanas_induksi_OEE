{
    'name': 'MRP Quality Custom',
    'version': '18.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Custom Quality Management with auto-scrap, QC checks, alerts, and toast notifications',
    'description': """
        Replaces Odoo Enterprise Quality module.
        - Quality Control Points (trigger rules)
        - Quality Checks (Pass/Fail, Measure, Take a Picture)
        - Quality Alerts (Kanban board for QC team)
        - Auto-scrap from reject sensor signals
        - Toast notifications on reject count increase
        - Dual trigger: API (automatic) + Manual (UI buttons)
    """,
    'author': 'Arya',
    'depends': ['mrp', 'stock', 'mrp_shopfloor_custom'],
    'data': [
        'security/ir.model.access.csv',
        'data/quality_alert_stage_data.xml',
        'views/quality_control_point_views.xml',
        'views/quality_check_views.xml',
        'views/quality_alert_views.xml',
        'views/quality_action.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mrp_quality_custom/static/src/css/quality.css',
            'mrp_quality_custom/static/src/js/quality_dashboard.js',
            'mrp_quality_custom/static/src/js/quality_dashboard.xml',
            'mrp_quality_custom/static/src/js/scrap_toast.js',
            'mrp_quality_custom/static/src/js/scrap_toast.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
