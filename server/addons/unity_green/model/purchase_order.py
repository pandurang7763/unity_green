from odoo import api, fields, models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order.line"


    stock_location = fields.Many2one('stock.warehouse', string="Stock Location")