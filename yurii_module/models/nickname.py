# -*- coding: utf-8 -*-

from odoo import models, fields, api



class Nickname(models.Model):
     _inherit = 'res.partner'
     nick_description = fields.Char(string="Nickname")



     @api.model
     def create(self, values):
          company = self.env['res.partner'].search([('id', '=', values['parent_id'])])
          nick_description = f"{values['name']}_{company.name}"
          values['nick_description'] = nick_description
          self.nick_description = self.env['project.project'].create({
               'name': values['name'], })
          res = super(Nickname, self).create(values)

          # res.nick_description = f"{res['id']}_{ values['name']}_{res.parent_id.name}"
          return res



       # if 'project_id' in values and not values.get('project_id') and self._get_timesheet():
       #      raise UserError(_('This task must be part of a project because there are some timesheets linked to it.'))
       #  res = super(Task, self).write(values)
       #
       #  if 'project_id' in values:
       #      project = self.env['project.project'].browse(values.get('project_id'))
       #      if project.allow_timesheets:
       #          We write on all non yet invoiced timesheet the new project_id (if project allow timesheet)
                # self._get_timesheet().write({'project_id': values.get('project_id')})
        #
        # return res