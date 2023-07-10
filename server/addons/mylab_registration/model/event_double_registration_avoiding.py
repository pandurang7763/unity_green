import base64
import io
import logging
import xlrd
from xlrd import open_workbook
from tempfile import TemporaryFile
from odoo.tools import pycompat

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


# in this we will get all the data present in event.registration
class EventRegistrationDuplicate(models.Model):
    _inherit = 'event.registration'



    # # giving a condition on email and event_id field
    # @api.constrains('email', 'event_id')
    # # defining a function to avoid double registration with same email id
    # def _check_login(self):
    #     # if event_id is there then only perform giving condition
    #     if self.event_id:
    #         # if event_id is present then looping over all event id registered by that partner
    #         # here partner id is current website user details will come
    #         for i in self.partner_id.event.ids:
    #             # if that event_id is already present in partner data Then raising error
    #             if i in self.event_id.ids:
    #                 raise ValidationError(_('You already registered for this Webinar!'))

    @api.model_create_multi
    def create(self, vals):
        res = super(EventRegistrationDuplicate, self).create(vals)
        # active_event_id = self.env['event.registration'].browse(self._context.get('active_ids'))
        search_current_event_id = self.env['event.registration'].search([('event_id', '=', res.event_id.id)])
        attendee_ids = search_current_event_id.mapped('email')
        if vals[0]['email'] in attendee_ids[1:]:
            raise ValidationError("You already registered for this Webinar!")
        return res





