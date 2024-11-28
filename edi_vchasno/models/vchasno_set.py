from odoo import api, fields, models, _
import datetime
import logging
import ast
import random
import string
import requests
from odoo.exceptions import UserError, ValidationError
import xml.etree.ElementTree as ET

_logger = logging.getLogger(__name__)


class VchasnoSet(models.Model):
    _name = "vchasno.set"
    _description = "Vchasno set"
    _rec_name = "pricelist_id"

    company_vat = fields.Char(string='Company Vat', default=lambda self: self.env.company.vat)
    pricelist_id = fields.Many2one('product.pricelist')
    action_vchasno = fields.Integer(string='Action', default=9)
    number = fields.Integer(string='Number document', default=1)
    date_document = fields.Date(string='Date document')
    date_from = fields.Date(string='Date from')
    supplirer = fields.Char(string='GLN supplier', size=13)
    buyer = fields.Char(string='GLN customer', size=13)
    sender = fields.Char(string='GLN sender', size=13)
    recipient = fields.Char(string='GLN recipient', size=13)
    action_vchasno_product = fields.Integer(string='Action for product', default=2)

    id_buyer = fields.Char(string='ID Buyer')
    additional_buyer_code = fields.Char(string='Additional Buyer code')
    test_line = fields.One2many('vchasno.set.line', 'vchasno_id', string='Test line')
    date_document = fields.Date(string='Date document')

    @api.constrains("company_vat", "supplirer", "buyer", "sender", "recipient", "id_buyer", "additional_buyer_code")
    def _checking_integer(self):
        fields = [self.company_vat, self.supplirer, self.buyer, self.sender, self.recipient, self.id_buyer, self.additional_buyer_code]
        invalid_fields = [field for field in fields if field and not field.isdigit()]
        if invalid_fields:
            field_names = ", ".join(invalid_fields)
            raise ValidationError(f"Please correct input for '{field_names}' (possible only digits)")

    def get_file_name(self):
        now = datetime.datetime.now()
        datetime_name = now.strftime("%Y-%d-%m/%H:%M:%S")
        add_char = ''.join(random.choices(string.ascii_uppercase, k=3))
        return f"Megatech_{datetime_name}_{add_char}"


    def send_set_price(self, body):
        token = self.env["ir.config_parameter"].search([("key", "=", "vchasno_token")]).value
        url = self.env["ir.config_parameter"].search([("key", "=", "vchasno_url")]).value
        if not token or not url:
            raise ValidationError(
                _("Sorry 'vchasno_token' or 'vchasno_url' not set  in settings/parameters/system parameters"))
        headers = {"Authorization": token}
        params = {"buyer_edrpou": 77777777}
        name = self.get_file_name()
        files = [
            ('file', (f"'{name}.xml'", body, 'text/xml'))
        ]
        try:
            response = requests.request(method="POST", url=f'{url}/api/documents/prices', headers=headers, params=params, files=files)
            if response.status_code == 200:
                msg = 'OK'
                _logger.info(response.content)
                return msg
            else:
                msg = ast.literal_eval(response.content.decode())
                _logger.error(
                    "Request failed.\nCode: %s\nContent: %s"
                    % (response.status_code, response.content)
                )
                raise UserError(f'{msg.get("reason")} & {msg.get("details")}')
        except Exception as e:
            raise UserError(_("Error with server:") + " %s" % e)

    def set_price(self):
        product = []
        for rec in self.pricelist_id:
            for line in rec.item_ids[:10]:
                if line.product_tmpl_id.sale_ok and \
                        line.product_tmpl_id.detailed_type == 'product':
                    price = line.fixed_price
                    if line.product_id:
                        ky_stock_quant_id = self.env['stock.quant'].sudo().search([
                            ('product_id', '=', line.product_id.id),
                            ('location_id.usage', '=', 'internal'),
                            ('location_id.name', '=', 'KYIV')
                        ])
                        ky_available = sum(
                            [x.available_quantity for x in ky_stock_quant_id if x.available_quantity > 0])
                        lv_stock_quant_id = self.env['stock.quant'].sudo().search([
                            ('product_id', '=', line.product_id.id),
                            ('location_id.usage', '=', 'internal'),
                            ('location_id.name', '=', 'LVIV')])
                        lv_available = sum(
                            [x.available_quantity for x in lv_stock_quant_id if x.available_quantity > 0])
                    else:
                        ky_stock_quant_id = self.env['stock.quant'].sudo().search(
                            [('product_id', 'in', line.product_tmpl_id.product_variant_ids.ids),
                             ('location_id.usage', '=', 'internal'),
                             ('location_id.name', '=', 'KYIV')])
                        ky_available = sum(
                            [x.available_quantity for x in ky_stock_quant_id if x.available_quantity > 0])
                        lv_stock_quant_id = self.env['stock.quant'].sudo().search(
                            [('product_id', 'in', line.product_tmpl_id.product_variant_ids.ids),
                             ('location_id.usage', '=', 'internal'),
                             ('location_id.name', '=', 'LVIV')])
                        lv_available = sum(
                            [x.available_quantity for x in lv_stock_quant_id if x.available_quantity > 0])
                    total_available = sum([ky_available, lv_available])
                    product.append({
                        "pricelist_product_id": line.id,
                        "barcode": line.product_tmpl_id.barcode if line.product_tmpl_id.barcode else None,
                        "id_buyer": self.id_buyer,
                        "additional_buyer_code": self.additional_buyer_code,
                        "id_supplier": line.product_tmpl_id.default_code if line.product_tmpl_id.default_code else None,
                        "name": line.name[:75],
                        "item_available": '1' if total_available > 0 else '0',
                        "price_with_vat": price if price > 0 else 1, ######
                        "min_order_qty": '1' if line.min_quantity <= 0 else line.min_quantity,
                        "unit_price": price if price > 0 else 1, #########
                        "tax_rate": '20',  ###########
                        "tax_category_code": 'S', ########
                        "action": self.action_vchasno_product

                    })
            if self.pricelist_id.currency_id:
                root = ET.Element("PRICAT")
                action_element = ET.SubElement(root, "ACTION")
                action_element.text = str(self.action_vchasno)
                number_element = ET.SubElement(root, "NUMBER")
                number_element.text = str(self.number)
                date_element = ET.SubElement(root, 'DATE')
                date_element.text = self.date_document.strftime('%Y-%m-%d')
                date_from_element = ET.SubElement(root, 'DATEFROM')
                date_from_element.text = self.date_from.strftime('%Y-%m-%d')
                currency_element = ET.SubElement(root, 'CURRENCY')
                currency_element.text = self.pricelist_id.currency_id.name
                supplier_element = ET.SubElement(root, "SUPPLIER")
                supplier_element.text = str(self.supplirer)
                buyer_element = ET.SubElement(root, "BUYER")
                buyer_element.text = str(self.buyer)
                sender_element = ET.SubElement(root, "SENDER")
                sender_element.text = str(self.sender)
                recipient_element = ET.SubElement(root, "RECIPIENT")
                recipient_element.text = str(self.recipient)
                catalog_element = ET.SubElement(root, 'CATALOGUE')
                for p in product:
                    # product_element = ET.SubElement(root, "product")
                    position_element = ET.SubElement(catalog_element, 'POSITION')
                    position_number_element = ET.SubElement(position_element, "POSITIONNUMBER")
                    position_number_element.text = str(p['pricelist_product_id'])
                    product_element = ET.SubElement(position_element, "PRODUCT")
                    product_element.text = str(p['barcode'])
                    id_buyer_element = ET.SubElement(position_element, "IDBUYER")
                    id_buyer_element.text = str(p['id_buyer'])
                    adittional_buyer_element = ET.SubElement(position_element, "ADDITIONALBUYERCODE")
                    adittional_buyer_element.text = str(p['additional_buyer_code'])
                    id_supplier_element = ET.SubElement(position_element, "IDSUPPLIER")
                    id_supplier_element.text = str(p['id_supplier'])
                    name_element = ET.SubElement(position_element, "PRODUCTNAME")
                    name_element.text = p['name']
                    item_available_element = ET.SubElement(position_element, "ITEMAVAILABLE")
                    item_available_element.text = p['item_available']
                    price_with_vat_element = ET.SubElement(position_element, "PRICEWITHVAT")
                    price_with_vat_element.text = str(p['price_with_vat'])
                    min_order_qty_element = ET.SubElement(position_element, "MINORDERQUANTITY")
                    min_order_qty_element.text = str(p['min_order_qty'])
                    unit_price_element = ET.SubElement(position_element, "UNITPRICE")
                    unit_price_element.text = str(p['unit_price'])
                    tax_rate_element = ET.SubElement(position_element, "TAXRATE")
                    tax_rate_element.text = p['tax_rate']
                    tax_category_code_element = ET.SubElement(position_element, "TAXCATEGORYCODE")
                    tax_category_code_element.text = p['tax_category_code']
                    action_element = ET.SubElement(position_element, "ACTION")
                    action_element.text = str(p['action'])
                # tree = ET.ElementTree(root)
                # b = tree.write("products.xml")
                xml_str = ET.tostring(root, encoding='utf-8', method='xml')
                msg = self.send_set_price(xml_str)
                if msg == 'OK':
                    return {
                        "type": "ir.actions.client",
                        "tag": "display_notification",
                        "params": {
                            "title": "EDI.Vshasno",
                            "message": "Set Success",
                            "type": "success",
                            "sticky": False,
                        },
                    }
                # self.send_set_price(xml_str)
                # name = "My Attachment"
                # a = self.env['ir.attachment'].create({
                #     'name': name,
                #     # 'type': 'binary',
                #     'datas': base64.b64encode(xml_str),
                #     'store_fname': name,
                #     'res_model': 'crm.lead',
                #     'res_id': 28,
                #     'mimetype': 'text/xml'
                # })

