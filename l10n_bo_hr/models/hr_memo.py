from odoo import models, fields, api, _, tools
import time
from odoo.exceptions import ValidationError, AccessError


class HrMemo(models.Model):
    _name = 'hr.memo'
    _description = 'Memo Empleado'

    def _get_user_create(self):
        user_create = self.env['res.users'].browse(self.env.user.id).id
        if not user_create:
            return False
        return user_create

    def _get_employee(self):
        context = self.env.context
        active_id = context.get('active_id', [])
        employee_id = self.env['hr.employee'].browse(active_id).id
        if not employee_id:
            return False
        return employee_id

    def _get_employee_from(self):
        employee_obj = self.env['hr.employee']
        employee_id = employee_obj.search([('user_id', '=', self.env.user.id)], limit=1)
        if employee_id:
            return employee_id[0].id

    number = fields.Char('Numero')
    name = fields.Char(string='Descripción:', required=True, readonly=True, states={'draft': [('readonly', False)]})
    title = fields.Char('Titulo', default="MEMORANDUM", readonly=True, states={'draft': [('readonly', False)]})
    with_sign = fields.Boolean('Con Firma', readonly=True, states={'draft': [('readonly', False)]})
    memo_type_id = fields.Many2one('hr.memo.type', string='Tipo:', required=True, readonly=True,
                                   states={'draft': [('readonly', False)]})
    date = fields.Date('Fecha:', default=lambda *a: time.strftime('%Y-%m-%d'))
    company_id = fields.Many2one('res.company', string='Compañia',
                                 default=lambda self: self._context.get('company_id', self.env.user.company_id.id),
                                 readonly=True, states={'draft': [('readonly', False)]})
    mensaje = fields.Html('Mensaje', readonly=True, states={'draft': [('readonly', False)]})
    employee_from_ids = fields.Many2many('hr.employee', 'memo_employee_rel2', 'memo_id', 'emp_id', string='De:',
                                         required=True, readonly=True, states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Dirigido a:', default=_get_employee, required=True,
                                  readonly=True, states={'draft': [('readonly', False)]})
    user_create = fields.Many2one('res.users', string='Creado por:', default=_get_user_create, required=True,
                                  readonly=True, states={'draft': [('readonly', False)]})
    employee_cc_ids = fields.Many2many('hr.employee', string='C.C.:', readonly=True,
                                       states={'draft': [('readonly', False)]})
    template_id = fields.Many2one('hr.memo.template', string='Plantilla', select=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Confirmado'),
    ], 'Status', readonly=True, default="draft")

    def write(self, vals):
        dirigido_a = self.employee_id
        memo_type = self.memo_type_id
        memo_count = self.search_count([('employee_id', '=', dirigido_a.id), ('memo_type_id', '=', memo_type.id)])
        permitido = self.memo_type_id.number_permit
        if memo_count > permitido:
            raise ValidationError(
                'No permitido! El empleado superó el número permitido de Memo especificado en el Tipo de Memo.')

        return super(HrMemo, self).write(vals)

    def action_confirm_memo(self):
        number = self.memo_type_id.sequence_id.next_by_id()
        self.number = number
        self.state = 'done'

    def action_memo_print(self):
        return self.env.ref('l10n_bo_hr.hr_memo_report').report_action(self)

    def save_as_template(self):
        template_obj = self.env['hr.memo.template']
        if self.template_id:
            self.template_id.template = self.mensaje
            self.template_id.title = self.title
            self.template_id.with_sign = self.with_sign
            self.template_id.name = self.name
        else:
            template_id = template_obj.create({
                'name': self.name,
                'template': self.mensaje,
                'memo_type_id': self.memo_type_id.id,
                'with_sign': self.with_sign,
                'title': self.title,
            })
            self.template_id = template_id.id

    @api.onchange('template_id')
    def on_change_template(self):
        if self.template_id:
            self.mensaje = self.template_id.template
            self.name = self.template_id.name
            self.with_sign = self.template_id.with_sign
            self.title = self.template_id.title


class HrMemoTemplate(models.Model):
    _name = 'hr.memo.template'
    _description = 'templates de los memos'

    name = fields.Char('Descripción')
    memo = fields.Char('Descripción del Memo')
    title = fields.Char('Titulo')
    with_sign = fields.Boolean('Con Firma')
    template = fields.Html('Template del Mensaje')
    memo_type_id = fields.Many2one('hr.memo.type', 'Tipo de Memo')


class HeMemoType(models.Model):
    _name = 'hr.memo.type'
    _description = 'Tipo de memo'

    name = fields.Char(string='Tipo Memo', required=True)
    number_permit = fields.Float(string='Número Permitido')
    sequence_id = fields.Many2one('ir.sequence', 'Secuencia')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    def _memo_count(self):
        memo = self.env['hr.memo']
        for s in self:
            s.memo_count = memo.search_count([('employee_id', '=', s.id)])

    memo_ids = fields.One2many('hr.memo', 'employee_id', string='Memos', required=False, readonly=True)
    memo_count = fields.Float(compute="_memo_count", type='integer', string='Memo')

    def open_memo(self):
        res = self.env['ir.actions.act_window'].for_xml_id('poi_hr_advanced', 'act_hr_employee_memo_list')
        hr_memo_ids = [po.id for po in self.browse(self.id)[0].memo_ids]
        res['domain'] = ((res.get('domain', []) or []) + [('id', 'in', hr_memo_ids)])
        return res
