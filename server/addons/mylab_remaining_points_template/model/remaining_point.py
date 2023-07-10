from odoo import api, fields, models, _



class SaleOrder(models.Model):
    _inherit = 'loyalty.program'

    mail_tempalte_for_sale = fields.Many2one("mail.template","sale template")


class LoyaltyCard(models.Model):
    _inherit = 'loyalty.card'

    def _send_creation_community(self):

        """
        Sends the 'At Creation' communication plan if it exist for the given coupons.
        """
        if self.env.context.get('loyalty_no_mail', False) or self.env.context.get('action_no_send_mail', False):
            return
        # Ideally one per program, but multiple is supported
        create_comm_per_program = dict()
        for program in self.program_id:
            create_comm_per_program[program] = program.communication_plan_ids.filtered(lambda c: c.trigger == 'create')

        for coupon in self:
            if not create_comm_per_program[coupon.program_id] or coupon._get_mail_partner():
                program.mail_tempalte_for_sale.send_mail(res_id=coupon.id,
                                                         email_layout_xmlid='mail.mail_notification_light')
