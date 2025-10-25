# Copyright 2020 Creu Blanca
# Copyright 2020 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json

from werkzeug.urls import url_decode

from odoo.http import request, route

from odoo.addons.web.controllers.report import ReportController


class ReportControllerEncrypt(ReportController):
    @route()
    def report_download(self, data, context=None, token=None, readonly=True):
        result = super().report_download(
            data, context=context, token=token, readonly=readonly
        )
        # When report is downloaded from print action, this function is called,
        # but this function cannot pass context (manually entered password) to
        # report.render_qweb_pdf(), encrypton for manual password is done here.
        if result.headers.get("Content-Type") != "application/pdf":
            return result
        request_content = json.loads(data)
        url, ttype = request_content[0], request_content[1]
        if ttype != "qweb-pdf" or "?" not in url:
            return result
        args = dict(
            url_decode(url.split("?", 1)[1])
        )  # decoding the args represented in JSON
        data_context = json.loads(args.get("context", "{}"))
        encrypt_password = data_context.get("encrypt_password")
        if not encrypt_password:
            return result
        encrypted_data = request.env["ir.actions.report"]._encrypt_pdf(
            result.get_data(), encrypt_password
        )
        result.set_data(encrypted_data)
        return result
