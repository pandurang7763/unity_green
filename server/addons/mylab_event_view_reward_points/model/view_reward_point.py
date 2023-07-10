from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EventRewardPointsView(models.Model):
    _inherit = 'event.event'



    def action_open_reward_points(self):
        self.ensure_one()
        action = self.env.ref("loyalty.loyalty_card_view_tree")

        return {
            'name': _('View Reward Points'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'loyalty.card',
            'views': [(action.id, 'tree')],
            'view_id': action.id,
            'target': 'new',
            'context': dict(
                default_mode='selected',
                default_program_id=1)
        }
