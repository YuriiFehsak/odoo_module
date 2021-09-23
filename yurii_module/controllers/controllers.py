# -*- coding: utf-8 -*-
# from odoo import http


# class YuriiModule(http.Controller):
#     @http.route('/yurii_module/yurii_module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/yurii_module/yurii_module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('yurii_module.listing', {
#             'root': '/yurii_module/yurii_module',
#             'objects': http.request.env['yurii_module.yurii_module'].search([]),
#         })

#     @http.route('/yurii_module/yurii_module/objects/<model("yurii_module.yurii_module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('yurii_module.object', {
#             'object': obj
#         })
