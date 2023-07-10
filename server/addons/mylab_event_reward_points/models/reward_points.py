from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EventAttendeeList(models.Model):
    _inherit = 'event.event'

    def action_send_coupon(self):
        # to call a form of loaylty card wizard to generate points
        compose_form = self.env.ref('loyalty.loyalty_generate_wizard_view_form')
        ctx = dict(
            default_events=self.id,
            default_mode='selected',
            default_program_id=1,
            default_customer_ids=self.env['event.registration'].search([('event_id','=',self.id),('state','=','done')]).mapped('partner_id.id')

        )
        return {
            'name': _('Reward Points'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'loyalty.generate.wizard',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target':'new',
            'context' : ctx
        }

