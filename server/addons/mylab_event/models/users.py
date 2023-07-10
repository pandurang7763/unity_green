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


class User(models.Model):
    _inherit = "res.users"

    institution = fields.Char(string="Institution/Organisation")
    phone = fields.Char("Phone", size=10)
    new_city = fields.Char("City")
    # new_job = fields.Char("Job")


class websitevisitor(models.Model):

    _inherit = 'website.visitor'

    city = fields.Char("city")
    institute = fields.Char("Institute")


class ResPartner(models.Model):
    _inherit = "res.partner"

    # function = fields.Char(related="user_id.new_job",store=True)
    # phone = fields.Char(related="user_id.phone",store=True)
    # city = fields.Char(related="user_id.new_city",store=True)
