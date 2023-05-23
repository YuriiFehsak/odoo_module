{
    'name': "EDI.Vchasno",

    'summary': """
        Edi.vchasno integration""",

    'description': """
        For integration with EDI.Vchasno
    """,

    'author': "Coodo-erp",
    'website': "https://codoo-erp.com/",
    'license': 'LGPL-3',
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'product',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/vchasno_set_view.xml',
        'data/ir_config_parameter_data.xml',
    ],
    'images': ['static/description/icon.png'],
}
