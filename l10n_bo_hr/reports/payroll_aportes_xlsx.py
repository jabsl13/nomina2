# -*- coding: utf-8 -*-
import calendar
from odoo import models
from datetime import datetime, date
from odoo.exceptions import ValidationError


class PayrollAportesReportXls(models.AbstractModel):
    _name = 'report.l10n_bo_hr.payroll_aportes_xlsx.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_lines(self, object):
        days = calendar.monthrange(int(object.year), int(object.month))
        date_init = date(year=int(object.year), month=int(object.month), day=1)
        date_end = date(year=int(object.year), month=int(object.month), day=int(days[1]))
        lines_afp = []
        payslips = self.env['hr.payslip'].search([('date_from', '>=', date_init),
                                                  ('date_to', '<=', date_end),
                                                  ('state', '!=', 'cancel')])

        for payslip in payslips:
            pays = payslip
            employee = payslip.employee_id
            contract = payslip.contract_id
            day = 0
            for day_line in pays.worked_days_line_ids:
                day += day_line.number_of_days
            monto_neto = 0

            valid = 0
            caja = 0
            afp = 0
            provi = 0
            aportsol = 0
            for lines in payslip.line_ids:
                if lines.code == 'TOT_NETO':
                    monto_neto = lines.total

                if lines.code == 'afp_inf_8':
                    caja = lines.total

                if lines.code == 'afp_inf_2':
                    afp = lines.total
                if lines.code == 'afp_inf_7':
                    provi = lines.total
                if lines.code == 'afp_inf_3':
                    aportsol = lines.total

            name_complete = employee.all_name
            if employee.all_name_two:
                name_complete = employee.all_name + ' ' + employee.all_name_two

            vals = {
                'b7': name_complete,
                'c7': employee.paternal_surname,
                'd7': employee.maternal_surname,
                'e7': employee.identification_id,
                'f7': employee.expedido,
                'g7': monto_neto,
                'h7': caja,
                'i7': afp,
                'j7': provi,
                'k7': aportsol,
                'l7': caja + afp + provi + aportsol,
                'm7': monto_neto * 0.8333,
                'n7': monto_neto * 0.8333,
            }
            lines_afp.append(vals)
        return lines_afp

    def generate_xlsx_report(self, workbook, data, object):
        i = 8
        j = 1
        sheet = workbook.add_worksheet()
        sheet.set_column('A:D', 10)
        sheet.set_column('E:W', 10)
        sheet.set_row(6, 30)
        first_line_format = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'font_size': 12,
        })
        first_line_format_left = workbook.add_format({
            'bold': 1,
            'align': 'left',
            'font_size': 11,
        })
        first_line_format_left2 = workbook.add_format({
            'bold': 0,
            'align': 'left',
            'font_size': 11,
        })
        first_line_format_2 = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'font_size': 15,
        })

        blue_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'font_size': 9,
            'num_format': '0',
        })
        blue_format_b = workbook.add_format({
            'border': 1,
            'bold': 1,
            'align': 'center',
            'font_size': 9,
        })

        blue_format_num = workbook.add_format({
            'border': 1,
            'align': 'right',
            'font_size': 9,
            'num_format': '#,##0.00',
        })
        blue_format_num_b = workbook.add_format({
            'border': 1,
            'bold': 1,
            'align': 'right',
            'font_size': 9,
            'num_format': '#,##0.00',
        })

        border_format = workbook.add_format({
            'border': 1,
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D9E1F2',
            'font_size': 9,
            'text_wrap': True,
        })
        mes = dict(object._fields['month'].selection).get(object.month)
        sheet.write('B2', 'NOMBRE O RAZÓN SOCIAL', first_line_format_left2)
        sheet.write('B3', 'CÓDIGO DE EMPLEADOR', first_line_format_left2)
        sheet.merge_range('H2:M2', 'APORTES PATRONALES', first_line_format_2)
        sheet.merge_range('H3:M3', 'Correspondiente al mes de ' + mes, first_line_format)
        sheet.merge_range('H4:M4', '(Expresado en Bolivianos)', first_line_format)

        sheet.write('B7', 'NOMBRES', border_format)
        sheet.write('C7', 'APELLIDO \nPATERNO', border_format)
        sheet.write('D7', 'APELLIDO \nMATERNO', border_format)
        sheet.write('E7', 'N° DE\nDOCUMENTO', border_format)
        sheet.write('F7', 'TIPO DE \nDOCUMENTO', border_format)
        sheet.write('G7', 'TOTAL GANADO', border_format)
        sheet.write('H7', 'C.N.S.\n10%', border_format)
        sheet.write('I7', 'A.F.P.\n1.71%', border_format)
        sheet.write('J7', 'PRO VIVIENDA\n2%', border_format)
        sheet.write('K7', 'APORTE SOLIDARIO\n3%', border_format)
        sheet.write('L7', 'TOTAL', border_format)
        sheet.write('M7', 'AGUINALDO\n8.333%', border_format)
        sheet.write('N7', 'INDEMINACION\n8.333%', border_format)
        gt = ht = it = jt = kt = lt = mt = nt = 0
        for each in self.get_lines(object):
            sheet.write('B' + str(i), str(each['b7']), blue_format)
            sheet.write('C' + str(i), str(each['c7']), blue_format)
            sheet.write('D' + str(i), str(each['d7']), blue_format)
            sheet.write('E' + str(i), str(each['e7']), blue_format)
            sheet.write('F' + str(i), str(each['f7']), blue_format)
            sheet.write('G' + str(i), each['g7'], blue_format_num)
            sheet.write('H' + str(i), each['h7'], blue_format_num)
            sheet.write('I' + str(i), each['i7'], blue_format_num)
            sheet.write('J' + str(i), each['j7'], blue_format_num)
            sheet.write('K' + str(i), each['k7'], blue_format_num)
            sheet.write('L' + str(i), each['l7'], blue_format_num)
            sheet.write('M' + str(i), each['m7'], blue_format_num)
            sheet.write('N' + str(i), each['n7'], blue_format_num)
            gt += each['g7']
            ht += each['h7']
            it += each['i7']
            jt += each['j7']
            kt += each['k7']
            lt += each['l7']
            mt += each['m7']
            nt += each['n7']
            i += 1
            j += 1
        sheet.write('F' + str(i), 'TOTALES:', blue_format_b)
        sheet.write('G' + str(i), kt, blue_format_num_b)
        sheet.write('H' + str(i), kt, blue_format_num_b)
        sheet.write('I' + str(i), kt, blue_format_num_b)
        sheet.write('J' + str(i), kt, blue_format_num_b)
        sheet.write('K' + str(i), kt, blue_format_num_b)
        sheet.write('L' + str(i), lt, blue_format_num_b)
        sheet.write('M' + str(i), mt, blue_format_num_b)
        sheet.write('N' + str(i), nt, blue_format_num_b)
