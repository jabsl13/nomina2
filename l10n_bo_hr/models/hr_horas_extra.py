from odoo import fields, models, api, exceptions, _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import calendar


class HrHorasExtra(models.Model):
    _name = 'hr.horas.extra'

    date = fields.Date(string='Fecha')
    employee_id = fields.Many2one('hr.employee', string='Empleado', tracking=True,
                                  domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', readonly=False, default=lambda self: self.env.company, required=True)
    hour = fields.Float(string='Horas', help='Horas registradas')
    type = fields.Selection([('normal', 'Normales'),
                             ('nocturno', 'Nocturnas'),
                             ('dominical', 'Dominical')],
                            string='Tipo Hora extra', default='normal')
    state = fields.Selection([
        ('draft', 'Para Aprobar'),
        ('validate', 'Aprobado'),
        ('refuse', 'Rechazado')
    ], string='Estado', default='draft')
    payslip_id = fields.Many2one('hr.payslip', string='Planilla de Sueldos', index=True)

    def action_validate(self):
        self.write({'state': 'validate'})

    def action_refuse(self):
        self.write({'state': 'refuse'})
