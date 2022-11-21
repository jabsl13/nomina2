from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import ValidationError


class custom_contract(models.Model):
    _inherit = 'hr.contract'

    salary_advance = fields.Monetary(string='Adelanto de sueldo')
    # transport_assignment = fields.Monetary(string='Asignación Transporte')
    # allowance_periods = fields.Monetary(string='Asignación Viaticos')
    # premium_bonus = fields.Monetary(string='Prima')
    bonus = fields.Monetary(string='Aguinaldo')
    health_manager_id = fields.Many2one(comodel_name='res.partner', string='Caja Salud',
                                        ondelete='cascade',
                                        required=False,
                                        default=False,
                                        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    avc_number = fields.Char(string='Matricula caja de salud')
    insured_code = fields.Char(string='Codigo Asegurado')
    nua_cua = fields.Char(string='NUA/CUA')
    contributes_afp = fields.Boolean(
        string='Aporta AFP', required=False, default=False)
    disabled_person = fields.Boolean(
        string='Persona con Discapacidad', required=False, default=False)
    disabled_person_tutor = fields.Boolean(
        string='Tutor Persona con Discapacidad', required=False, default=False)
    retiree = fields.Boolean(
        string='Es Jubilado', required=False, default=False)

    afp_manager_id = fields.Many2one(comodel_name='res.partner', string='Gestora AFP',
                                     ondelete='cascade',
                                     required=False,
                                     default=False,
                                     domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    contract_modality = fields.Selection(string='Modalidad Contrato', selection=[('1', 'Tiempo indefinido'),
                                                                                 ('2', 'A plazo fijo'),
                                                                                 ('3', 'Por Temporada'),
                                                                                 ('4',
                                                                                  'Por realizacion de Obra o Servicio'),
                                                                                 ('5', 'Condicional o Eventual')],
                                         copy=False, default='1')

    recar_nocturno = fields.Selection(string='Recargo Nocturno', selection=[('25', 'Oficina'),
                                                                            ('30', 'Obreros'),
                                                                            ('40', 'Mujeres o Menores de 18 años'),
                                                                            ('50', 'Alto Riesgo'), ],
                                      copy=False, default='25')
    contract_type_expiration = fields.Date(
        string='Vencimiento tipo de contratacion')
    calculate_overtime = fields.Boolean(
        string='Calcula Horas Extras', default=False)
    bono_front = fields.Boolean(
        string='Bono Frontera', default=False)
    dominical = fields.Boolean(
        string='Bono Dominical',
        help='Active esta opción se requiere calcular bono domincal para el trabajador(Aplicable solo a trabjadores '
             'Obreros)',
        default=False)
    cbu = fields.Integer(string='CBU')
    settlement_start_date = fields.Date('Fecha Inicio Finiquito')
    dismissal_date = fields.Date('Fecha retiro')
    dismissal_reason = fields.Text('Motivo Retiro')
    bank_company = fields.Many2one(comodel_name='res.bank', string='Banco')
    cta_bank = fields.Many2one(comodel_name='res.partner.bank', string='Cuenta Banco',
                               domain="[('bank_id','=',bank_company)]")
    cod_cliente = fields.Char(string='Código Cliente')
    divisa_id = fields.Many2one('res.currency', string='Moneda Cta.', copy=False)
    bono_ids = fields.One2many(
        'hr.bono.contract', 'contract_id', string='Contratos')

    # Habilitar para dos contratos pero solo un tipo de regla salarial
    @api.constrains('employee_id', 'state', 'kanban_state', 'date_start', 'date_end')
    def _check_current_contract(self):
        """ Two contracts in state [incoming | open | close] cannot overlap """
        for contract in self.filtered(lambda c: (c.state not in ['draft',
                                                                 'cancel'] or c.state == 'draft' and c.kanban_state == 'done') and c.employee_id):
            domain = [
                ('id', '!=', contract.id),
                ('employee_id', '=', contract.employee_id.id),
                ('company_id', '=', contract.company_id.id),
                ('structure_type_id', '=', contract.structure_type_id.id),
                '|',
                ('state', 'in', ['open']),
                '&',
                ('state', '=', 'draft'),
                ('kanban_state', '=', 'done')
            ]
            start_domain = []
            end_domain = []
            # if not contract.date_end:
            #     start_domain = []
            #     end_domain = ['|', ('date_end', '>=', contract.date_start), ('date_end', '=', False)]
            # else:
            #     start_domain = [('date_start', '<=', contract.date_end)]
            #     end_domain = ['|', ('date_end', '>', contract.date_start), ('date_end', '=', False)]

            domain = expression.AND([domain, start_domain, end_domain])
            if self.search_count(domain):
                raise ValidationError(
                    _(
                        'Un empleado solo puede tener un contrato al mismo tiempo. (Excluyendo borradores y contratos cancelados).\n\nEmpleado: %(employee_name)s',
                        employee_name=contract.employee_id.name
                    )
                )
