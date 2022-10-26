# -*- coding: utf-8 -*-
import calendar
from odoo import models
from datetime import datetime, date
from odoo.exceptions import ValidationError


class PayrollAguiReportXls(models.AbstractModel):
    _name = 'report.l10n_bo_hr.payroll_agui_xlsx.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_lines(self, object):
        days = calendar.monthrange(int(object.year), int(12))
        date_init = date(year=int(object.year), month=1, day=1)
        date_end = date(year=int(object.year), month=12, day=int(days[1]))
        date_init_sep = date(year=int(object.year), month=9, day=1)
        date_end_nov = date(year=int(object.year), month=11, day=30)
        lines_afp = []
        employees = self.env['hr.employee'].search([])
        cc_nro = 1
        ndias = (date_end - date_init).days
        print(ndias)
        nmeses = 0
        for employee in employees:
            nmeses = 0
            se = 0
            if employee.gender == 'male':
                se = 1
            ju = 0
            if employee.contract_id.retiree:
                ju = 1

            payslip_line = self.env['hr.payslip.line'].search([('date_from', '>=', date_init_sep),
                                                               ('date_from', '<=', date_end_nov),
                                                               ('employee_id', '=', employee.id),
                                                               ('slip_id.state', '!=', 'cancel')])

            nmeses = len(self.env['hr.payslip'].search([('employee_id', '=', employee.id),
                                                        ('state', '!=', 'cancel'),
                                                        ('date_from', '>=', date_init),
                                                        ('date_from', '<=', date_end)]))
            v10 = 0
            w10 = 0
            x10 = 0
            y10 = 0
            z10 = 0
            aa10 = 0
            ab10 = 0
            ac10 = 0
            ad10 = 0
            ae10 = 0

            for lines in payslip_line:
                if lines.code == 'BASICBO':
                    v10 = lines.total
                if lines.code == 'BONO_A':
                    w10 = lines.total
                if lines.code == 'BONO_F':
                    y10 = lines.total
                if lines.code in ('BONO_HEX', 'BONO_HEX_NOCT'):
                    z10 += lines.total
                if lines.code == 'BONO_HEX_DOM':
                    aa10 = lines.total
                if lines.code == 'BONO_O':
                    ab10 = lines.total

            porce_duo = ndias / 30
            v10 = v10 / 3
            w10 = w10 / 3
            y10 = y10 / 3
            z10 = z10 / 3
            aa10 = aa10 / 3
            ab10 = ab10 / 3
            total = v10 + w10 + y10 + z10 + aa10 + ab10
            total_ganado = 0
            if porce_duo > 2.999:
                total_ganado = (total * porce_duo) / 12
            vals = {
                'b7': cc_nro,
                'c7': employee.tipo_doc or '',
                'd7': employee.identification_id or '',
                'e7': employee.expedido or '',
                'f7': employee.contract_id.afp_manager_id.name or '',
                'g7': employee.contract_id.nua_cua or '',
                'h7': employee.paternal_surname or '',
                'i7': employee.maternal_surname or '',
                'j7': employee.maried_surname or '',
                'k7': employee.all_name or '',
                'l7': employee.all_name_two or '',
                'm7': employee.country_id.name or '',
                'n7': employee.birthday or '',
                'o7': se or 0,
                'p7': ju or 0,
                'q7': '',
                'r7': employee.contract_id.job_id.name or '',
                's7': employee.contract_id.date_start or '',
                't7': employee.contract_id.contract_modality or '',
                'u7': employee.contract_id.date_end or '',
                'v7': v10,
                'w7': w10,
                'x7': x10,
                'y7': y10,
                'z7': z10,
                'aa7': aa10,
                'ab7': ab10,
                'ac7': total,
                'ad7': nmeses,
                'ae7': total_ganado,
                'af7': employee.work_location_id.name or '',
                'ag7': '',
            }
            cc_nro += 1
            lines_afp.append(vals)
        return lines_afp

    def generate_xlsx_report(self, workbook, data, object):
        i = 11
        j = 1
        sheet = workbook.add_worksheet()
        sheet.set_column('A:A', 2)
        sheet.set_column('B:AF', 15)
        sheet.set_row(9, 40)
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
            'font_size': 8,
            'text_wrap': True,
        })
        sheet.merge_range('B2:D2', 'NOMBRE O RAZÓN SOCIAL', first_line_format_left)
        sheet.write('E2', object.company_id.name, first_line_format_left2)
        sheet.merge_range('B3:D3', 'N° EMPLEADOR MINISTERIO DE TRABAJO', first_line_format_left)
        sheet.write('E3', object.company_id.cod_empleador, first_line_format_left2)
        sheet.merge_range('B4:D4', 'N° DE NIT', first_line_format_left)
        sheet.write('E4', object.company_id.vat, first_line_format_left2)
        sheet.merge_range('B5:D5', 'N° DE EMPLEADOR(Caja de Salud)', first_line_format_left)
        sheet.write('E5', object.company_id.caja_salud, first_line_format_left2)
        sheet.merge_range('H6:M6', 'PLANILLA DE PAGO DE AGUINALDO DE NAVIDAD', first_line_format_2)
        sheet.merge_range('H7:M7', 'Correspondiente a la gestión ' + object.year, first_line_format)
        sheet.merge_range('H8:M8', '(Expresado en Bolivianos)', first_line_format)

        sheet.write('B10', 'N°', border_format)
        sheet.write('C10', 'TIPO DE DOCUMENTO DE INDENTIDAD', border_format)
        sheet.write('D10', 'NUMERO DE DOCUMENTO DE IDENTIDAD', border_format)
        sheet.write('E10', 'EXTENSIÓN DEL DOCUMENTO DE IDENTIDAD', border_format)
        sheet.write('F10', 'AFP A LA QUE APORTA', border_format)
        sheet.write('G10', 'NUA/CUA', border_format)
        sheet.write('H10', 'APELLIDO PATERNO', border_format)
        sheet.write('I10', 'APELLIDO MATERNO', border_format)
        sheet.write('J10', 'APELLIDO DE CASADA', border_format)
        sheet.write('K10', 'PRIMER NOMBRE', border_format)
        sheet.write('L10', 'OTROS NOMBRES', border_format)
        sheet.write('M10', 'PAIS NACIONALIDAD', border_format)
        sheet.write('N10', 'FECHA DE NACIMIENTO', border_format)
        sheet.write('O10', 'SEXO', border_format)
        sheet.write('P10', 'JUBILADO', border_format)
        sheet.write('Q10', 'CLASIFICACIÓN LABOR', border_format)
        sheet.write('R10', 'CARGO', border_format)
        sheet.write('S10', 'FECHA DE INGRESO', border_format)
        sheet.write('T10', 'MODALIDAD DE CONTRATO', border_format)
        sheet.write('U10', 'FECHA RETIRO', border_format)
        sheet.write('V10', 'PROMEDIO DEL HABER BÁSICO', border_format)
        sheet.write('W10', 'PROMEDIO DEL BONO DE ANTIGUEDAD', border_format)
        sheet.write('X10', 'PROMEDIO DEL BONO DE PRODUCCIÓN', border_format)
        sheet.write('Y10', 'PROMEDIO DEL SUBSIDIO DE FRONTERA', border_format)
        sheet.write('Z10', 'PROMEDIO TRABAJO EXTRAORDINARIO Y NOCTURNO', border_format)
        sheet.write('AA10', 'PROMEDIO PAGO DOMINICAL Y DOMINGO TRABAJADO', border_format)
        sheet.write('AB10', 'PROMEDIO OTROS BONOS', border_format)
        sheet.write('AC10', 'PROMEDIO TOTAL GANADO', border_format)
        sheet.write('AD10', 'MESES TRABAJADOS', border_format)
        sheet.write('AE10', 'TOTAL GANADO DESPUES DE DUODÉCIMAS', border_format)
        sheet.write('AF10', 'SUCURSAL O UBICACIÓN ADICIONAL', border_format)
        sheet.write('AG10', 'FIRMA EMPLEADO', border_format)
        vt = wt = xt = yt = zt = aat = abt = act = adt = aet = aft = 0
        for each in self.get_lines(object):
            sheet.write('B' + str(i), str(each['b7']), blue_format)
            sheet.write('C' + str(i), str(each['c7']), blue_format)
            sheet.write('D' + str(i), str(each['d7']), blue_format)
            sheet.write('E' + str(i), str(each['e7']), blue_format)
            sheet.write('F' + str(i), str(each['f7']), blue_format)
            sheet.write('G' + str(i), str(each['g7']), blue_format)
            sheet.write('H' + str(i), str(each['h7']), blue_format)
            sheet.write('I' + str(i), str(each['i7']), blue_format)
            sheet.write('J' + str(i), str(each['j7']), blue_format)
            sheet.write('K' + str(i), str(each['k7']), blue_format)
            sheet.write('L' + str(i), str(each['l7']), blue_format)
            sheet.write('M' + str(i), str(each['m7']), blue_format)
            sheet.write('N' + str(i), str(each['n7']), blue_format)
            sheet.write('O' + str(i), str(each['o7']), blue_format)
            sheet.write('P' + str(i), str(each['p7']), blue_format)
            sheet.write('Q' + str(i), str(each['q7']), blue_format)
            sheet.write('R' + str(i), str(each['r7']), blue_format)
            sheet.write('S' + str(i), str(each['s7']), blue_format)
            sheet.write('T' + str(i), str(each['t7']), blue_format)
            sheet.write('U' + str(i), str(each['u7']), blue_format)
            sheet.write('V' + str(i), each['v7'], blue_format_num)
            sheet.write('W' + str(i), each['w7'], blue_format_num)
            sheet.write('X' + str(i), each['x7'], blue_format_num)
            sheet.write('Y' + str(i), each['y7'], blue_format_num)
            sheet.write('Z' + str(i), each['z7'], blue_format_num)
            sheet.write('AA' + str(i), each['aa7'], blue_format_num)
            sheet.write('AB' + str(i), each['ab7'], blue_format_num)
            sheet.write('AC' + str(i), each['ac7'], blue_format_num)
            sheet.write('AD' + str(i), each['ad7'], blue_format_num)
            sheet.write('AE' + str(i), each['ae7'], blue_format_num)
            sheet.write('AF' + str(i), each['af7'], blue_format)
            vt += each['v7']
            wt += each['w7']
            xt += each['x7']
            yt += each['y7']
            zt += each['z7']
            aat += each['aa7']
            abt += each['ab7']
            act += each['ac7']
            adt += each['ad7']
            aet += each['ae7']
            i += 1
            j += 1
        sheet.write('U' + str(i), 'TOTALES:', blue_format_b)
        sheet.write('V' + str(i), vt, blue_format_num_b)
        sheet.write('W' + str(i), wt, blue_format_num_b)
        sheet.write('X' + str(i), xt, blue_format_num_b)
        sheet.write('Y' + str(i), yt, blue_format_num_b)
        sheet.write('Z' + str(i), zt, blue_format_num_b)
        sheet.write('AA' + str(i), aat, blue_format_num_b)
        sheet.write('AB' + str(i), abt, blue_format_num_b)
        sheet.write('AC' + str(i), act, blue_format_num_b)
        sheet.write('AD' + str(i), adt, blue_format_num_b)
        sheet.write('AE' + str(i), aet, blue_format_num_b)
