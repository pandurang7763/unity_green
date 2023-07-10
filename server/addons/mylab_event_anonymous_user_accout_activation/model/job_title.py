from odoo import api, fields, models
from ast import literal_eval
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.misc import ustr

from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.addons.auth_signup.models.res_partner import SignupError, now
import logging
_logger = logging.getLogger(__name__)


class User(models.Model):
    _inherit = "res.users"

    new_job = fields.Char("Job")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    user_title = fields.Selection([('Mr', 'Mr'), ('Miss', 'Miss'), ('Dr', 'Dr'), ('Mrs', 'Mrs')], readonly=True)

    @api.model
    def signup_retrieve_info(self, token):
        """ retrieve the user info about the token
            :return: a dictionary with the user information:
                - 'db': the name of the database
                - 'token': the token, if token is valid
                - 'name': the name of the partner, if token is valid
                - 'login': the user login, if the user already exists
                - 'email': the partner email, if the user does not exist
        """
        partner = self._signup_retrieve_partner(token, raise_exception=True)
        res = {'db': self.env.cr.dbname}
        if partner.signup_valid:
            res['token'] = token
            res['name'] = partner.name
            res['new_job'] = partner.function
            res['new_city'] = partner.city
            res['institution'] = partner.company_name
            res['phone'] = partner.phone
            res['name_title'] = partner.user_title

        if partner.user_ids:
            res['login'] = partner.user_ids[0].login
        else:
            res['email'] = res['login'] = partner.email or ''
        return res


class EventRegistration(models.Model):
    _inherit = "event.registration"

    select_title = fields.Selection([('Mr', 'Mr'), ('Miss', 'Miss'), ('Dr', 'Dr'), ('Mrs', 'Mrs')], readonly=True)





    @api.model_create_multi
    def create(self, vals):
        res = super(EventRegistration, self).create(vals)
        if res.partner_id:
            event_names = self.env['event.registration'].search([('name', '=', res.partner_id.name)])
            event_mapping = event_names.mapped('event_id')
            print(event_names)
            res.partner_id.event = event_mapping
        return res

    def _get_website_registration_allowed_fields(self):
        return {'name', 'phone', 'email', 'mobile', 'event_id', 'partner_id', 'event_ticket_id', 'user_city',
                'institute', 'job_title','select_title'}


    def create(self, vals_list):
        res = super().create(vals_list)
        print(res)

        if not res.partner_id.user_ids.name_title:
            res.name = res.select_title + " " + res.name
        else:
            res.name
        res['name'] = res['name'].title()

        return res

    

     # send email to users about registration
    def action_registation_mail(self):
        template = False

        template = self.env.ref('mylab_event_view_reward_points.event_registration')


        email_values = {
            'email_cc': False,
            'auto_delete': True,
            'recipient_ids': [],
            'partner_ids': [],
            'scheduled_date': False,
        }

        for user in self:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.", user.name))
            email_values['email_to'] = user.email
            # TDE FIXME: make this template technical (qweb)
            with self.env.cr.savepoint():
                force_send = not (self.env.context.get('import_file', False))
                template.send_mail(user.id, force_send=force_send, raise_exception=True, email_values=email_values)
            _logger.info("Password reset email sent for user <%s> to <%s>", user.email)

    class User(models.Model):
        _inherit = "res.users"

        name_title = fields.Selection([('Mr', 'Mr'), ('Miss', 'Miss'), ('Dr', 'Dr'), ('Mrs', 'Mrs')], store=True)

        @api.model_create_multi
        def create(self, vals_list):
            parent_fun = super().create(vals_list)
            print(parent_fun)

            if parent_fun.name_title:
                parent_fun.name = parent_fun.name_title + " " + parent_fun.name

            parent_fun['name'] = parent_fun['name'].title()

            return parent_fun



class EventEvent(models.Model):
    _inherit = "event.event"

    #defining a function to create attendee based on current user
    def create_internal_attendee(self):
        return self.env['event.registration'].sudo().create({
            'email': self.env.user.login,
            'name': self.env.user.name,
            'phone': self.env.user.phone,
            'institute': self.env.user.institution,
            'user_city': self.env.user.new_city,
            'job_title': self.env.user.new_job,
            'select_title': self.env.user.name_title,
            'event_id' : self.id,
            'partner_id':self.env.user.partner_id.id
        })


    

#get the current user id from website and call this function in xml
    def _get_current_user(self):
        if self.env.user.state =="active":

            return True
        else:
            return False


