# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    @api.depends('is_paid', 'number_of_hours', 'payslip_id', 'contract_id.wage',
                 'payslip_id.sum_worked_hours')
    def _compute_amount(self):
        # primero identificar los dias de falta
        n_dias_out = 0
        for worked_days in self.filtered(lambda wd: not wd.payslip_id.edited):
            if worked_days.work_entry_type_id.code != 'WORK100':
                n_dias_out = worked_days.number_of_days
                worked_days.amount = 0

        for worked_days in self.filtered(lambda wd: not wd.payslip_id.edited):
            if not worked_days.contract_id or worked_days.code == 'OUT':
                worked_days.amount = 0
                continue
            if worked_days.payslip_id.wage_type == "hourly":
                worked_days.amount = worked_days.payslip_id.contract_id.hourly_wage * worked_days.number_of_hours if worked_days.is_paid else 0
            else:
                sal_base = worked_days.payslip_id.contract_id.contract_wage
                if worked_days.work_entry_type_id.code == 'WORK100':
                    worked_days.amount = sal_base / 30 * (30 - n_dias_out)
                # worked_days.amount = worked_days.payslip_id.contract_id.contract_wage * worked_days.number_of_hours / (
                #            worked_days.payslip_id.sum_worked_hours or 1) if worked_days.is_paid else 0
