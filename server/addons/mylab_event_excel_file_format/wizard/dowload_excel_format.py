from odoo import api, fields, models, _


class UploadFile(models.TransientModel):
    _inherit = "attendee.upload.file"



    def download_format(self):
       return {
           'target': 'self',
           'url': 'mylab_event_excel_file_format/static/src/img/attendee_format.jpeg',
           'type': 'ir.actions.act_url'
       }