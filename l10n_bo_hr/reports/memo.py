#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from odoo import api, models, fields
from odoo.exceptions import UserError


class report_poi_hr_memo(models.AbstractModel):
    _name = 'report.poi_hr_memo.memo_print'


    def _get_report_values(self, doc_ids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('poi_hr_memo.memo_print')
        docs = self.env[report.model].browse(self._ids)

        # if docs.state != 'done':
        #     raise UserError('El Memorandum debe estar confirmado antes de poder ser imprimido.')

        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': docs,
            'smart_truncate': self.smart_truncate,
        }

    def smart_truncate(self, content, length=36, suffix=''):
        if len(content) <= length:
            return content
        else:
            return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix
