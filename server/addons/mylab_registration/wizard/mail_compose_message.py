from odoo import api, fields, models, _


class MailComposer(models.TransientModel):
    _name = "attendee.send.mail"

    load_template_id = fields.Many2one("mail.template","Load Templates")
    event_id = fields.Many2one("event.event","Event Name")

    def action_send_email_bulk(self):
        template = self.load_template_id
        for attendee in self.event_id.registration_ids:
            if attendee.state == 'done':
                template.email_to = attendee.email
                template.send_mail(attendee.id,force_send=True)
                print(attendee)




