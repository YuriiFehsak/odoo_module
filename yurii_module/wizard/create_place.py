# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CreatePlaceWizard(models.TransientModel):
    _name = "create.place.wizard"
    _description = "Create Place Wizard"

    name = fields.Char(string="Contact", required=True)
    contact_from_id = fields.Many2one('res.partner', string="Contact_from Contacts")



