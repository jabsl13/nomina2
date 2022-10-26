from odoo import models, fields, api
from .num_literal import to_word


class Payslip(models.Model):
    _inherit = "hr.payslip"

    def print_report(self):
        return self.env.ref('l10n_bo_hr.graphic_representation').report_action(self)

    def compute_sheet(self):
        for pay in self:
            adelantos = self.env['hr.adelantos']
            prestamos = self.env['hr.prestamos.line']
            input_pay = self.env['hr.payslip.input']
            unlink_input = input_pay.search([('input_type_id', '=', self.env.ref('l10n_bo_hr.input_bo_adelanto').id)])
            if unlink_input:
                unlink_input.unlink()
            unlink_input = input_pay.search([('input_type_id', '=', self.env.ref('l10n_bo_hr.input_bo_prestamo').id)])
            if unlink_input:
                unlink_input.unlink()
            for i in adelantos.search(
                    [('contract_id', '=', pay.contract_id.id), ('state', '=', 'process'), ('date', '>=', pay.date_from),
                     ('date', '<=', pay.date_to)]):
                input = {
                    'name': i.name,
                    'amount': i.amount,
                    'payslip_id': pay.id,
                    'input_type_id': self.env.ref('l10n_bo_hr.input_bo_adelanto').id,
                }
                input_pay.create(input)
            for a in prestamos.search(
                    [('prestamos_id.contract_id', '=', pay.contract_id.id),
                     ('state', '=', 'process'),
                     ('date', '>=', pay.date_from),
                     ('date', '<=', pay.date_to)]):
                input = {
                    'name': a.name,
                    'amount': a.amount_total_pay,
                    'payslip_id': pay.id,
                    'input_type_id': self.env.ref('l10n_bo_hr.input_bo_prestamo').id,
                }
                input_pay.create(input)

        return super().compute_sheet()

    def _get_base_local_dict(self):
        res = super()._get_base_local_dict()
        res.update({
            'calculo_bono_antiguedad': calculo_bono_antiguedad,
            'calculo_horas_extra': calculo_horas_extra,
            'calculo_horas_extra_domingo': calculo_horas_extra_domingo,
            'calculo_horas_recargo_nocturno': calculo_horas_recargo_nocturno,
            'calculo_otros_bonos': calculo_otros_bonos,
            'calculo_rciva': calculo_rciva,
            'importe_rciva': importe_rciva,
        })
        return res

    def amount_literal(self, payslip):
        pays_line = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id), ('code', '=', 'NETBO')])
        total = 0
        if pays_line:
            for pay_line in pays_line:
                total += pay_line.total
        letras = ''
        if total > 0:
            texto = to_word(total) + ' BOLIVIANOS'
            letras = str(texto).upper()
        return letras

    def neto_pagar(self, payslip):
        pays_line = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id), ('code', '=', 'NETBO')])
        total = 0
        if pays_line:
            for pay_line in pays_line:
                total += pay_line.total
        return total


# Funciones adicionales calculo HHRR Bolivia
def calculo_bono_antiguedad(payslip):
    contract = payslip.contract_id
    bono = payslip.dict.env['hr.bono.antiguedad']
    start = contract.date_start
    end = payslip.date_to
    number_of_month = (end.year - start.year) * 12 + (end.month - start.month) + 1
    year = round(number_of_month / 12, 2)
    busqueda_bono = bono.search([('anio_min', '<=', year), ('anio_max', '>', year)])
    monto_bono = 0
    if busqueda_bono:
        monto_bono = (contract.company_id.sueldo_min * 3) * (busqueda_bono[0].porcentaje / 100)
    return monto_bono


def calculo_horas_extra(payslip):
    contract = payslip.contract_id
    horas = payslip.dict.env['hr.horas.extra']
    start = payslip.date_from
    end = payslip.date_to
    horas_extra = horas.search(
        [('date', '<=', end),
         ('date', '>=', start),
         ('employee_id', '=', contract.employee_id.id),
         ('type', '=', 'normal'),
         ('state', '=', 'validate')])
    tot_horas = 0
    for hr_ex in horas_extra:
        tot_horas += hr_ex.hour
    monto_dia = contract.wage / 30
    monto_hora = (monto_dia / 8) * 2
    monto_bono = monto_hora * tot_horas
    return monto_bono


def calculo_horas_extra_domingo(payslip):
    contract = payslip.contract_id
    horas = payslip.dict.env['hr.horas.extra']
    start = payslip.date_from
    end = payslip.date_to
    horas_extra = horas.search(
        [('date', '<=', end),
         ('date', '>=', start),
         ('employee_id', '=', contract.employee_id.id),
         ('type', '=', 'dominical'),
         ('state', '=', 'validate')])
    tot_horas = 0
    for hr_ex in horas_extra:
        tot_horas += hr_ex.hour
    monto_dia = contract.wage / 30
    monto_hora = (monto_dia / 8) * 3
    monto_bono = monto_hora * tot_horas
    return monto_bono


def calculo_horas_recargo_nocturno(payslip):
    contract = payslip.contract_id
    horas = payslip.dict.env['hr.horas.extra']
    start = payslip.date_from
    end = payslip.date_to
    horas_extra = horas.search(
        [('date', '<=', end),
         ('date', '>=', start),
         ('employee_id', '=', contract.employee_id.id),
         ('type', '=', 'nocturno'),
         ('state', '=', 'validate')])
    tot_horas = 0
    for hr_ex in horas_extra:
        tot_horas += hr_ex.hour
    monto_dia = contract.wage / 30
    monto_hora = (monto_dia / 8) * 2
    monto_recar = monto_hora * (float(contract.recar_nocturno) / 100)
    monto_bono = monto_recar * tot_horas
    return monto_bono


def calculo_otros_bonos(payslip):
    contract = payslip.contract_id
    tot_bono = 0
    for bono in contract.bono_ids:
        tot_bono += bono.amount
    return tot_bono


def calculo_rciva(payslip, total_rciva):
    contract = payslip.contract_id
    rc = payslip.dict.env['hr.rciva']
    start = payslip.date_from
    end = payslip.date_to
    horas_rciva = rc.search(
        [('date_from', '<=', end),
         ('date_to', '>', start),
         ('employee_id', '=', contract.employee_id.id)])
    tot_rc = 0
    saldo_favor = 0
    saldo_favor_actual = 0
    if horas_rciva:
        tot_rc = horas_rciva[0].amount_iva
        total = total_rciva - tot_rc
        if total < 0:
            if horas_rciva:
                horas_rciva[0].amount_saldo = total * -1
                saldo_favor_actual = total * -1
        # Calcular el UFV con saldo anterior
        ufv_ini = float(horas_rciva[0].ufv_inicial_val)
        ufv_fin = float(horas_rciva[0].ufv_final_val)

        rciva_ant = rc.search(
            [('date_to', '<', start),
             ('employee_id', '=', contract.employee_id.id),
             ('amount_saldo', '>', 0)], order="date_to desc", limit=1)
        total_ufv = 0
        if rciva_ant:
            total_ufv = ((ufv_fin / ufv_ini) - 1) * rciva_ant[0].amount_saldo
            saldo_favor = rciva_ant[0].amount_saldo
        tot_rc -= total_ufv
    return tot_rc, saldo_favor, saldo_favor_actual


def importe_rciva(payslip):
    contract = payslip.contract_id
    rc = payslip.dict.env['hr.rciva']
    start = payslip.date_from
    end = payslip.date_to
    horas_rciva = rc.search(
        [('date_from', '<=', end),
         ('date_to', '>', start),
         ('employee_id', '=', contract.employee_id.id)])
    tot_rc = 0
    if horas_rciva:
        tot_rc = horas_rciva[0].amount_iva
    return tot_rc
