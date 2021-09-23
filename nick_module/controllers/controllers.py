# -*- coding: utf-8 -*-
# from odoo import http


# class NickModule(http.Controller):
#     @http.route('/nick_module/nick_module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nick_module/nick_module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('nick_module.listing', {
#             'root': '/nick_module/nick_module',
#             'objects': http.request.env['nick_module.nick_module'].search([]),
#         })

#     @http.route('/nick_module/nick_module/objects/<model("nick_module.nick_module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nick_module.object', {
#             'object': obj
#         })
