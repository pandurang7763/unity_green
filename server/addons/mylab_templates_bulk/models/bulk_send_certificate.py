import base64
import io
import logging
import xlrd
from xlrd import open_workbook
from tempfile import TemporaryFile
from odoo.tools import pycompat

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EventAttendeeList(models.Model):
    _inherit = 'event.event'

    def action_send_badge_email(self):
        """ Open a window to compose an email, with the template - 'event_badge'
            message loaded by default
        """
        self.ensure_one()

        # commented code is base code of odoo

        # template = self.env.ref('event.event_registration_mail_template_badge', raise_if_not_found=False)

        # storing a external id of wizard to give a context for button
        compose_form = self.env.ref('mylab_templates_bulk.event_bulk_mail_send_view')
        # passing a current event_id to the wizard as context
        ctx = dict(
            default_model='event.registration',
            default_event_id=self.id,

        )
        # returning as base code form
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'attendee.send.mail',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }




class PointsGiving(models.Model):
    _inherit = "res.partner"
  

    #adding new field for getting reward points
    get_points = fields.Float(default=0.0, string="Points")

    

