# -*- coding: utf-8 -*-

from odoo import models, fields, api


class yurii_module(models.Model):
     _name = 'yurii_module.yurii_module'
     _description = 'yurii_module.yurii_module'

     name = fields.Char()
     value = fields.Integer()
     value2 = fields.Float(compute="_value_pc", store=True)
     description = fields.Text()
     email = fields.Integer("Email")
     instagram = fields.Char("Instagram")
     add = fields.Boolean(string = "Add")
     level = fields.Selection([('low',' low'),
                               ('middle', 'middle'),
                               ('high', 'high')],
                                string = "Category")
     contact_from_id = fields.Many2one('res.partner', string="Contact_from Contacts")
     select_contact_from_ids = fields.Many2many('res.partner', string="Select_from Contacts")
     email_contact = fields.Char(string="Email_customer", related="select_contact_from_ids.email")
     project_field_id = fields.Many2one('project.project', string="Projects")
     task_field_id = fields.Many2one('project.task', string="Tasks")

     @api.depends('value')
     def _value_pc(self):
         for record in self:
             record.value2 = float(record.value) / 100
