from odoo import models, fields, api
import urllib.parse
import urllib.request
import json
import base64


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        record = super(ResPartner, self).create(vals)
        self._send_http_request(record, 'create')
        return record

    def write(self, vals):
        result = super(ResPartner, self).write(vals)
        for record in self:
            self._send_http_request(record, 'write')
        return result

    def unlink(self):
        for record in self:
            self._send_http_request(record, 'unlink')
        result = super(ResPartner, self).unlink()
        return result

    def _send_http_request(self, record, action):
        name_parts = record.name.split()
        group_parts = None
        if record.category_id:
            group_parts = "Vip" if record.category_id[0].id == 1 else \
                "Corretor" if record.category_id[0].id == 2 else \
                    "Recepcionista" if record.category_id[0].id == 3 else None
        fname = name_parts[0]
        if len(name_parts) > 1:
            lname = ' '.join(name_parts[1:])
        else:
            lname = '-'

        image_base64 = base64.b64encode(record.image_1920).decode('utf-8') if record.image_1920 else None
        if action == "create":
            base_url = 'http://192.168.10.186:7998/insert/'
            payload = {
                "user_id": record.id,
                "user_fname": fname,
                "user_lname": lname,
                "user_group": group_parts,
                "subject_photo": image_base64
            }

        elif action == "write":
            base_url = 'http://192.168.10.186:7998/write/'
            payload = {
                "user_id": record.id,
                "user_fname": fname,
                "user_lname": lname,
                "user_group": group_parts,
                "subject_photo": image_base64
            }

        elif action == "unlink":
            base_url = 'http://192.168.10.186:7998/delete/'
            payload = {
                "user_id": record.id
            }

        data_encoded = json.dumps(payload).encode('utf-8')

        headers = {
            'Content-Type': 'application/json',
            'Content-Length': len(data_encoded)
        }

        req = urllib.request.Request(url=base_url, data=data_encoded, headers=headers, method='POST')

        try:
            response = urllib.request.urlopen(req)
            # Handling redirection
            if response.getcode() == 307:
                redirected_url = response.geturl()
                req = urllib.request.Request(url=redirected_url, data=data_encoded, headers=headers, method='POST')
                response = urllib.request.urlopen(req)

            print(f'HTTP POST request sent successfully: {response.read().decode()}')
        except Exception as e:
            print(f'Failed to send HTTP POST request: {e}')