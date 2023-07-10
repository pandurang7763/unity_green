import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)
from odoo.addons.auth_signup.models.res_partner import SignupError, now





class ResUsers(models.Model):
    _inherit = 'res.users'




    def action_reset_password(self):

        print("reset password is printing...............")

        """ create signup token for each user, and send their signup url by email """
        if self.env.context.get('install_mode', False):
            return
        if self.filtered(lambda user: not user.active):
            raise UserError(_("You cannot perform this action on an archived user."))
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        template = True
        if create_mode:
            try:
                template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
            except ValueError:
                pass
        # (here we sending the mail tempalte for reset password only as we combined account activation mail tempalte in event registration mail template)
        # if template and self.state == 'new':
        #     template = self.env.ref('auth_signup.set_password_email')
        if template and self.state == 'active':
            template = self.env.ref('auth_signup.reset_password_email')
            assert template._name == 'mail.template'

        email_values = {
            'email_cc': False,
            'auto_delete': True,
            'recipient_ids': [],
            'partner_ids': [],
            'scheduled_date': False,
        }

        for user in self:
            if not user.login:
                raise UserError(_("Cannot send email: user %s has no email address.", user.name))
            email_values['email_to'] = user.login
            # TDE FIXME: make this template technical (qweb)
            with self.env.cr.savepoint():
                force_send = not (self.env.context.get('import_file', False))
                 #sending mail of reset password to the confirmed user only
                if template and self.state == 'active':
                    template.send_mail(user.id, force_send=force_send, raise_exception=True, email_values=email_values)
            _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)
        

    # # to call the anonymous event registration calling the function  
    # def action_user_invite(self):

    #     """ create signup token for each user, and send their signup url by email """
    #     if self.env.context.get('install_mode', False):
    #         return
    #     if self.filtered(lambda user: not user.active):
    #         raise UserError(_("You cannot perform this action on an archived user."))
    #     # prepare reset password signup
    #     create_mode = bool(self.env.context.get('create_user'))

    #     # no time limit for initial invitation, only for reset password
    #     expiration = False if create_mode else now(days=+1)

    #     self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

    #     # send email to users with their signup url
    #     template = False
    #     if create_mode:
    #         try:
    #             template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
    #         except ValueError:
    #             pass
    #     if not template:
    #         template = self.env.ref('auth_signup.set_password_email')
    #     assert template._name == 'mail.template'

    #     email_values = {
    #         'email_cc': False,
    #         'auto_delete': True,
    #         'recipient_ids': [],
    #         'partner_ids': [],
    #         'scheduled_date': False,
    #     }

    #     for user in self:
    #         if not user.login:
    #             raise UserError(_("Cannot send email: user %s has no email address.", user.name))
    #         email_values['email_to'] = user.login
    #         # TDE FIXME: make this template technical (qweb)
    #         with self.env.cr.savepoint():
    #             force_send = not (self.env.context.get('import_file', False))
    #             template.send_mail(user.id, force_send=force_send, raise_exception=True, email_values=email_values)
    #         _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)







