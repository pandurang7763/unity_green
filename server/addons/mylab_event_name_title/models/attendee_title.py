from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


# in this we will get all the data present in event.registration
class EventRegistrationDuplicate(models.Model):
    _inherit = 'event.registration'

    select_title = fields.Selection([('Mr', 'Mr'), ('Miss', 'Miss'), ('Dr', 'Dr'),('Mrs','Mrs')],readonly=True)

    def _get_website_registration_allowed_fields(self):
        return {'name', 'phone', 'email', 'mobile', 'event_id', 'partner_id', 'event_ticket_id', 'user_city',
                'institute', 'job_title','select_title'}

    def create(self, vals_list):
        res = super().create(vals_list)
        print(res)

        if res.select_title:
            res.name = res.select_title + " " + res.name

        res['name'] = res['name'].title()


        return res


class User(models.Model):
    _inherit = "res.users"


    name_title = fields.Selection([('Mr', 'Mr'), ('Miss', 'Miss'), ('Dr', 'Dr'),('Mrs','Mrs')],store=True)

    @api.model_create_multi
    def create(self, vals_list):
        parent_fun = super().create(vals_list)
        print(parent_fun)

        if parent_fun.name_title:
            parent_fun.name = parent_fun.name_title + " " + parent_fun.name

        parent_fun['name'] = parent_fun['name'].title()

        return parent_fun

