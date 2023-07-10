from odoo import api, fields, models, _


class MailComposer(models.TransientModel):
    _name = "attendee.send.mail"

    load_template_id = fields.Many2one("mail.template", "Load Templates")
    model = fields.Char('Related Document Model')
    event_id = fields.Many2one("event.event", "Event Name",readonly=True)
    state = fields.Selection([('open', 'Confirmed'), ('done', 'Attended')],
                             string='Status', default="done", copy=False, tracking=True)


    @api.depends('model')
    def _compute_render_model(self):
        for composer in self:
            composer.render_model = composer.model

    def action_send_email_bulk(self):
        template = self.load_template_id
        for attendee in self.event_id.registration_ids:
            if attendee.state == self.state:
                template.email_to = attendee.email
                template.send_mail(attendee.id, force_send=True)
                print(attendee)

    @api.onchange('state')
    def get_mail_template_domain(self):
        for i in self:
            if i.state == 'done':
                return {'domain': {'load_template_id': [('name', 'in', ['Event: Event Certification',
                                                                        'Event: Event Natspert Certification',
                                                                        
                                                                        ])]}}
            else:
                return {'domain': {'load_template_id': [('name', 'in',
                                                         ['Event: Reminder(3 days ago)', 'Event: Reminder(1 days ago)',
                                                          'Event: Reminder(15 Min ago)',
                                                         
                                                          'Event: Live Session','Event: Not Attended'])]}}
