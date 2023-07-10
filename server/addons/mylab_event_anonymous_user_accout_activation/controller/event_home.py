from odoo import fields, http, _
from odoo.http import request
from odoo import Command
import werkzeug
from odoo.addons.mylab_event.controllers.main import MylabEvent


class MylabEventAnnonomous(MylabEvent):

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
                # adding new_job and name_title fetch job_title,select_title while registration of event
                "job_title": request.env.user.new_job,
                "select_title": request.env.user.name_title


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

     # once the anonymous user registers for an event this method will be fired
    @http.route(['''/event/<model("event.event"):event>/registration/confirm'''], type='http', auth="public",
                methods=['POST'], website=True)
    def registration_confirm(self, event, **post):
        # fetch the Registration Details
        registrations = self._process_attendees_form(event, post)
        #if not getting any data in post and he is a user then calling a function to create a attendee with current user deatils and storing them into a variable
        if event._get_current_user():
            event_attendees_sudo = event.create_internal_attendee()
            # the registration mail for confirmed user withount account activation button
            event_attendees_sudo.action_registation_mail()
            #returning to redirecting to the event success url bt passing 'attendees_sudo' variable where we are creating new record for event attendee
            return request.redirect(('/event/%s/registration/success?' % event.id) + werkzeug.urls.url_encode(
            {'registration_ids': ",".join([str(id) for id in event_attendees_sudo.ids])}))

        else:
            # check if there is any user already registered as portal user for the same email id
            searching_email = request.env['res.users'].search([('email', '=', registrations[0].get('email'))])
        attendees_sudo = self._create_attendees_from_registration_post(event, registrations)

        # if we did not find any portal user then as per the business requirement we should create
        # new Portal user

        if not searching_email:
            vals = request.env['res.users'].sudo().create({
                'login': registrations[0].get('email'),
                'name': registrations[0].get('name'),
                'groups_id': [Command.set([request.env.ref('base.group_portal').id])],
                'new_city': registrations[0].get('user_city'),
                'phone': registrations[0].get('phone'),
                'new_job': registrations[0].get('job_title'),
                'institution': registrations[0].get('institute'),
                'name_title': registrations[0].get('select_title')

            })
            # assigning the Event objet to Event Detail so that we can pass it on to password reset template
            # so We can add the Event details in Passowrd reset/ user invite template details itself.

            getting_name = request.env['res.partner'].sudo().search([('name', '=', vals.name), ('email', '=', False)],
                                                                    limit=1)
            if getting_name:
                getting_name.update({
                    'email': vals.login,
                    'event': attendees_sudo.event_id,
                    'phone': vals.phone,
                    'city': vals.new_city,
                    'company_name': vals.institution,
                    'function': vals.new_job,
                    'user_title': vals.name_title

                })

            searching_booked_by = attendees_sudo.sudo().search([('email', '=', getting_name.email)], limit=1)
            if searching_booked_by:
                searching_booked_by.update({
                    'partner_id': getting_name.id
                })


            # if you want the separte password reset template then you can just uncomment the method call.
            # vals.action_reset_password()

            # this method call is intended to merge two template as per business requirement.
            # action_reset_password in this account activation and reset password mail will send . if the user is already present then action_reset_password wont send mail if he is new then only it will send
            vals.action_reset_password()
            #the registration mail for new user with account activation button
            searching_booked_by.action_registation_mail()

        return request.redirect(('/event/%s/registration/success?' % event.id) + werkzeug.urls.url_encode(
            {'registration_ids': ",".join([str(id) for id in attendees_sudo.ids])}))

