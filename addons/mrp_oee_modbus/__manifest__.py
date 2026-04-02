{
    'name': 'MRP OEE Modbus Integration',
    'version': '18.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Configurable Modbus TCP/IP interface for reading machine data and writing OEE to Omron NB HMI',
    'description': """
        Adds a fully configurable Modbus TCP/IP interface for:
        - Reading real-time machine data (run time, counts, machine status)
        - Computing OEE from Modbus inputs
        - Writing OEE results back to Omron NB HMI registers
        - Background polling with configurable interval
        - Connection test wizard
    """,
    'author': 'Arya',
    'depends': ['mrp', 'mrp_oee_custom'],
    'external_dependencies': {'python': ['pymodbus']},
    'data': [
        'security/ir.model.access.csv',
        'data/loss_reason_data.xml',
        'data/default_register_map.xml',
        'data/modbus_cron.xml',
        'wizards/modbus_test_wizard_views.xml',
        'views/modbus_config_views.xml',
        'views/modbus_register_map_views.xml',
        'views/modbus_workcenter_views.xml',
        'views/res_users_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
