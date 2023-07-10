from odoo import api, fields, models


class TripDetails(models.Model):
    _name = "fruitly.trip.details"
    _description = "Trip Details"

    date = fields.Date(required=True, default=fields.Date.today())
    name = fields.Many2one('fleet.vehicle', string="Vehicle Number")
    start_time = fields.Datetime(required=True, string="Vehicle Start Time")
    end_time = fields.Datetime(required=True, string="Vehicle End Time")
    vehicle_net_time = fields.Float(
        compute='_compute_net_time', string="Net Time Vehicle")
    diesel_litre = fields.Float(string="Diesel Litre")
    net_km = fields.Float(string="Net Km", compute="_compute_net_km")
    start = fields.Float(string=" Vehicle Start KM")
    end = fields.Float(string='Vehicle End KM')
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm')], default='draft')

    @api.depends('start', 'end')
    def _compute_net_km(self):
        for TripDetails in self:
            if TripDetails.start and TripDetails.end:
                TripDetails.net_km = TripDetails.end - TripDetails.start
            return TripDetails.net_km

    @api.depends('start_time', 'end_time')
    def _compute_net_time(self):
        for TripDetails in self:
            if TripDetails.start_time and TripDetails.end_time:
                start = fields.Datetime.from_string(TripDetails.start_time)
                end = fields.Datetime.from_string(TripDetails.end_time)
                duration = end - start
                vehicle_net_time = duration.total_seconds() / 3600  # Convert to hours
                TripDetails. vehicle_net_time = vehicle_net_time
            else:
                TripDetails. vehicle_net_time = 0.0

    labours_number_of = fields.Integer(string=" Number Of Labours")
    labours_contract_name = fields.Many2one('res.partner')
    perday_labours = fields.Integer(string="Labours Per Day Charge")
    perday_vehicle = fields.Integer(string="Vehicle Per Day Charge")
    total_labours_charge = fields.Integer(
        string="Total Labours Day Charge",  compute="_compute_total_labours_charge")
    trips_lines_ids = fields.One2many(
        "fruitly.trips.lines", 'labours_contract', string='Trips lines Ids')

    @api.depends('labours_number_of', 'perday_labours')
    def _compute_total_labours_charge(self):
        for TripDetails in self:
            if TripDetails.labours_number_of and TripDetails.perday_labours:
                TripDetails.total_labours_charge = TripDetails.labours_number_of * \
                    TripDetails.perday_labours
            return TripDetails.total_labours_charge

    # creating a purchase order from trip and manking it into confirmed state
    def create_purchase_order(self):
        # writing a state is confirm and creating purchase order
        self.write({'state': 'confirm'})

        for rec in self.trips_lines_ids:
            pstock_po = self.env['purchase.order'].create({

                'partner_id': rec.zone.id,
                'order_line': [
                    (0, 0, {'product_id': rec.product_id.id, 'product_qty': rec.total, 'date_planned': self.date})]
            })
            pstock_po.button_confirm()

        return pstock_po


class TripsLines(models.Model):
    _name = "fruitly.trips.lines"
    _description = "Trips Details"

    weight = fields.Float(string=" Tentative Weight")
    trip_id = fields.Char(string='Trip Id', store=True)

    zone = fields.Many2one("res.partner", string="Zone")
    unloading_id = fields.Many2one('stock.location', string="Unloading Site")
    stock_desk_id = fields.Many2one(
        'stock.location', string="stock desk  Site")
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type')

    in_time = fields.Datetime()
    out_time = fields.Datetime()
    net_time = fields.Float(digits=(16, 2))
    total = fields.Float(string="Actual Weight")
    description = fields.Char("Name")

    product_id = fields.Many2one('product.product', string='Product')
    labours_contract = fields.Many2one("fruitly.trip.details")

# creating a stock from trip independenetly
    def create_stock(self):
        self.ensure_one()
        # using ir.actions.action to open a tree form of stock
        result = self.env["ir.actions.actions"]._for_xml_id(
            'stock.action_picking_tree_all')
        # override the context to get rid of the default filtering on operation type
        # result['context'] = {'default_partner_id': self.zone.id, 'default_move_ids_product_id': self.product_id.id}

        # opening a form view as follows and storing it in res variable
        res = self.env.ref('stock.view_picking_form', False)
        form_view = [(res and res.id or False, 'form')]
        result['views'] = form_view + \
            [(state, view)
             for state, view in result.get('views', []) if view != 'form']
        # here craeting a stock picking values
        vals = self.env['stock.picking'].create({'partner_id': self.zone.id, 'location_id': self.unloading_id.id, 'location_dest_id': self.stock_desk_id.id, 'product_id': self.product_id.id,
                                                 'picking_type_id': self.picking_type_id.id, 'origin': self.description})
        # for stock picking values creating stock move values
        if vals:
            stock_move = self.env['stock.move'].create({'location_id': vals.location_id.id, 'product_id': self.product_id.id, 'location_dest_id': vals.location_dest_id.id,
                                                       'picking_type_id': vals.picking_type_id.id, 'name': self.description, 'product_uom_qty': self.total, 'picking_id': vals.id})
        result['res_id'] = vals.id

        return result
