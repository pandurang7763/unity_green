from odoo import fields, http, _
from odoo.http import request
from odoo import Command
import werkzeug
from odoo.addons.website_event.controllers.main import WebsiteEventController


class MylabEvent(WebsiteEventController):

    @http.route(['/event/<model("event.event"):event>/registration/new'], type='json', auth="public", methods=['POST'],
                website=True)
    def registration_new(self, event, **post):
        tickets = self._process_tickets_form(event, post)
        availability_check = True
        if event.seats_limited:
            ordered_seats = 0
            for ticket in tickets:
                ordered_seats += ticket['quantity']
            if event.seats_available < ordered_seats:
                availability_check = False
        if not tickets:
            return False
        default_first_attendee = {}
        if not request.env.user._is_public():
            default_first_attendee = {
                "name": request.env.user.name,
                "email": request.env.user.email,
                "phone": request.env.user.mobile or request.env.user.phone,
                "institute": request.env.user.institution,
                "user_city": request.env.user.new_city,



            }
        else:
            visitor = request.env['website.visitor']._get_visitor_from_request()
            if visitor.email:
                default_first_attendee = {
                    "name": visitor.name,
                    "email": visitor.email,
                    "phone": visitor.mobile,
                    "institute": visitor.institute,
                }
        return request.env['ir.ui.view']._render_template("website_event.registration_attendee_details", {
            'tickets': tickets,
            'event': event,
            'availability_check': availability_check,
            'default_first_attendee': default_first_attendee,
        })

    @http.route(['''/event/<model("event.event"):event>/registration/confirm'''], type='http', auth="public",
                methods=['POST'], website=True)
    def registration_confirm(self, event, **post):
        registrations = self._process_attendees_form(event, post)
        searching_email = request.env['res.users'].search([('email', '=', registrations[0].get('email'))])
        attendees_sudo = self._create_attendees_from_registration_post(event, registrations)
        if not searching_email:
            vals = request.env['res.users'].sudo().create({
                'login': registrations[0].get('email'),
                'name': registrations[0].get('name'),
                'groups_id': [Command.set([request.env.ref('base.group_portal').id])],
                'new_city': registrations[0].get('user_city'),
                'phone': registrations[0].get('phone'),
                'new_job': registrations[0].get('job_title'),
                'institution': registrations[0].get('institute'),


            })


            getting_name = request.env['res.partner'].sudo().search([('name', '=', vals.name)])
            if getting_name:
                  getting_name.update({
                    'email': vals.login,
                    'event': attendees_sudo.event_id,
                    'phone': vals.phone,
                    'city': vals.new_city,
                    'company_name':vals.institution,
                    # 'function': vals.new_job,

                })


        return request.redirect(('/event/%s/registration/success?' % event.id) + werkzeug.urls.url_encode(
            {'registration_ids': ",".join([str(id) for id in attendees_sudo.ids])}))
