from odoo import models, fields
from lxml import etree

class IpaiAribaCxmlIngest(models.TransientModel):
    _name = "ipai.ariba.cxml.ingest"
    _description = "Ingest Ariba cXML PO/Invoice"

    doc_type = fields.Selection([("PO","PO"),("INV","Invoice")], required=True)
    xml = fields.Text(required=True)

    def action_parse(self):
        root = etree.fromstring(self.xml.encode("utf-8"))
        # TODO: parse header/lines, create purchase.order or vendor bill
        return {"status":"ok", "tag": root.tag}
