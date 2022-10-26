import datetime
from odoo import fields, models, _
from datetime import datetime, timedelta, date


class PayrollAguinaldo(models.TransientModel):
    _name = "payroll.aguinaldo"
    _description = "Payroll Aguinaldo"

    def _default_year(self):
        date = datetime.now()
        return date.year

    year = fields.Char(u'Año', size=4, required=True, default=_default_year)
    company_id = fields.Many2one('res.company', readonly=False, string='Compañía',
                                 default=lambda self: self.env.company, required=True)

    def print_xlsx(self):
        report_name = 'l10n_bo_hr.payroll_agui_xlsx.xlsx'
        return self.env['ir.actions.report'].search(
            [('report_name', '=', report_name),
             ('report_type', '=', 'xlsx')], limit=1).report_action(self)
