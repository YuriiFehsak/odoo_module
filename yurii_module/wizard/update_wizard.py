
# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CreatePlaceWizard(models.TransientModel):
    _name = "update.wizard"
    _description = "Create Place Wizard"

    update_name = fields.Char(string="New name", required=True)
    update_contact_from_id = fields.Many2one('res.partner', string="Company")

    def update_fields(self):
        self.env['yurii_module.yurii_module'].browse(self._context.get("active_ids")).update({'name': self.update_name})
        return True
