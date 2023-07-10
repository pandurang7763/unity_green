from odoo import api, models, fields
from odoo.exceptions import ValidationError

from pytz import utc, timezone
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.osv import expression
from odoo.tools.misc import get_lang, format_date



class PointsGiving(models.Model):
    _inherit = "res.partner"

    get_points = fields.Float(default=0.0, string="Points")

    event = fields.Many2many("event.event", string="Event")

    # def get_events(self):
    #     event_names = self.env['event.registration'].search([('name','=',self.name)])
    #     event_mapping = event_names.mapped('event_id')
    #     print(event_names)
    #     self.event = event_mapping
    #     return self.event


class EventRegistration(models.Model):
    _inherit = "event.registration"

    phone = fields.Char("Phone",size=10)
    institute = fields.Char("Institute")
    user_city = fields.Char("City")
    job_title = fields.Char("Job Title")
    series_name = fields.Char("Series Name")



    @api.model_create_multi
    def create(self, vals):
        res = super(EventRegistration, self).create(vals)
        if res.partner_id:
            event_names = self.env['event.registration'].search([('email', '=', res.partner_id.email)])
            event_mapping = event_names.mapped('event_id')
            print(event_names)
            res.partner_id.event = event_mapping
        return res

    def _get_website_registration_allowed_fields(self):
        return {'name', 'phone', 'email', 'mobile', 'event_id', 'partner_id', 'event_ticket_id', 'user_city',
                'institute', 'job_title'}


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_claimable(self, forced_coupons=None):
        # res = super(SaleOrder,self)._get_claimable_rewards(forced_coupons=forced_coupons)
        # print(res,"mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")

        all_coupons = forced_coupons or (
                self.coupon_point_ids.coupon_id | self.order_line.coupon_id | self.applied_coupon_ids)

        ewallet_sum = sum(all_coupons.mapped('points'))

        result = ewallet_sum

        return result


class LoyaltyGenerateWizard(models.TransientModel):
    _inherit = 'loyalty.generate.wizard'

    customer_ids = fields.Many2many('res.partner', string='Customers')
    events = fields.Many2one("event.event", "Event Name")

    @api.onchange('events')
    def get_partners(self):
        if self.events:
            var = self.env['event.registration'].search([('event_id','in',self.events.ids),('state','=','done')]).mapped('partner_id')
            self.customer_ids = var
        else:
            self.customer_ids = False



    def generate_coupons(self):
        self.ensure_one()

        coupon_create_vals = []
        for wizard in self:
            customers = wizard._get_partners() or range(wizard.coupon_qty)

            for partner in customers:
                # searching the partner who are already exist
                search_existing_partnr_cpn_id = self.env['loyalty.card'].search([('partner_id','=',partner.id),('program_id','=',wizard.program_id.id)])
                # searching the partner who's id present in res partner table with loyalty card partner id
                search_partner_from_contact = self.env['res.partner'].search([('id','=',partner.id)])
                # searching the partner who's id present in event registration table 
                search_event_attendee = self.env['event.registration'].search([]).mapped('partner_id')


                # if partner are not existing then create new record
                if not search_existing_partnr_cpn_id.ids:
                    coupon_create_vals.append(wizard._get_coupon_values(partner))
                if search_existing_partnr_cpn_id.ids:
                # if partner are  existing then add points to existing partner
                    search_existing_partnr_cpn_id.points += wizard.points_granted
                # if partner are  existing then add points to respartner
                if search_partner_from_contact.ids:
                    search_partner_from_contact.get_points += wizard.points_granted
                
                # if partner are  existing then add points to event regisrtan
                for rec in search_event_attendee:
                    if rec == partner.id:
                        rec.attendee_point += wizard.points_granted
                

        self.env['loyalty.card'].create(coupon_create_vals)

        # for serching the partner whom coupon are genrating
        # looping over the partner and calling a function to to send mail












        return True

class Event(models.Model):
    _inherit = 'event.event'

    @api.model
    def _search_build_dates(self):
        today = fields.Datetime.today()

        def sdn(date):
            return fields.Datetime.to_string(date.replace(hour=23, minute=59, second=59))

        def sd(date):
            return fields.Datetime.to_string(date)

        def get_month_filter_domain(filter_name, months_delta):
            first_day_of_the_month = today.replace(day=1)
            filter_string = _('This month') if months_delta == 0 \
                else format_date(self.env, value=today + relativedelta(months=months_delta),
                                 date_format='LLLL', lang_code=get_lang(self.env).code).capitalize()
            return [filter_name, filter_string, [
                ("date_end", ">=", sd(first_day_of_the_month + relativedelta(months=months_delta))),
                ("date_begin", "<", sd(first_day_of_the_month + relativedelta(months=months_delta + 1)))],
                    0]

        return [
            ['upcoming', _('Upcoming Webinars'), [("date_end", ">", sd(today))], 0],
            ['today', _('Today'), [
                ("date_end", ">", sd(today)),
                ("date_begin", "<", sdn(today))],
             0],
            get_month_filter_domain('month', 0),
            ['old', _('Past Events'), [
                ("date_end", "<", sd(today))],
             0],
            ['all', _('All Events'), [], 0]
        ]








