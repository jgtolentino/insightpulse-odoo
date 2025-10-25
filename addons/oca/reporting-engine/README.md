
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/reporting-engine&target_branch=18.0)
[![Pre-commit Status](https://github.com/OCA/reporting-engine/actions/workflows/pre-commit.yml/badge.svg?branch=18.0)](https://github.com/OCA/reporting-engine/actions/workflows/pre-commit.yml?query=branch%3A18.0)
[![Build Status](https://github.com/OCA/reporting-engine/actions/workflows/test.yml/badge.svg?branch=18.0)](https://github.com/OCA/reporting-engine/actions/workflows/test.yml?query=branch%3A18.0)
[![codecov](https://codecov.io/gh/OCA/reporting-engine/branch/18.0/graph/badge.svg)](https://codecov.io/gh/OCA/reporting-engine)
[![Translation Status](https://translation.odoo-community.org/widgets/reporting-engine-18-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/reporting-engine-18-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# reporting-engine

reporting-engine

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[base_comment_template](base_comment_template/) | 18.0.1.0.1 |  | Add conditional mako template to any reporton models that inherits comment.template.
[bi_sql_editor](bi_sql_editor/) | 18.0.1.0.4 | <a href='https://github.com/legalsylvain'><img src='https://github.com/legalsylvain.png' width='32' height='32' style='border-radius:50%;' alt='legalsylvain'/></a> | BI Views builder, based on Materialized or Normal SQL Views
[pdf_xml_attachment](pdf_xml_attachment/) | 18.0.1.0.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> <a href='https://github.com/alexis-via'><img src='https://github.com/alexis-via.png' width='32' height='32' style='border-radius:50%;' alt='alexis-via'/></a> | Provides helpers to work w/ PDFs and XML attachments
[report_csv](report_csv/) | 18.0.1.0.0 |  | Base module to create csv report
[report_py3o](report_py3o/) | 18.0.1.0.1 |  | Reporting engine based on Libreoffice (ODT -> ODT, ODT -> PDF, ODT -> DOC, ODT -> DOCX, ODS -> ODS, etc.)
[report_py3o_fusion_server](report_py3o_fusion_server/) | 18.0.1.0.0 |  | Let the fusion server handle format conversion.
[report_qr](report_qr/) | 18.0.1.0.0 |  | Web QR Manager
[report_qweb_element_page_visibility](report_qweb_element_page_visibility/) | 18.0.1.0.0 |  | Report Qweb Element Page Visibility
[report_qweb_encrypt](report_qweb_encrypt/) | 18.0.1.0.0 | <a href='https://github.com/kittiu'><img src='https://github.com/kittiu.png' width='32' height='32' style='border-radius:50%;' alt='kittiu'/></a> | Allow to encrypt qweb pdfs
[report_qweb_field_option](report_qweb_field_option/) | 18.0.1.0.1 |  | Report Qweb Field Option
[report_qweb_parameter](report_qweb_parameter/) | 18.0.1.0.0 |  | Add new parameters for qweb templates in order to reduce field length and check minimal length
[report_qweb_pdf_cover](report_qweb_pdf_cover/) | 18.0.1.0.0 |  | Add front and back covers to your QWeb PDF reports
[report_qweb_pdf_watermark](report_qweb_pdf_watermark/) | 18.0.1.0.1 | <a href='https://github.com/hbrunn'><img src='https://github.com/hbrunn.png' width='32' height='32' style='border-radius:50%;' alt='hbrunn'/></a> | Add watermarks to your QWEB PDF reports
[report_substitute](report_substitute/) | 18.0.1.0.0 | <a href='https://github.com/sbejaoui'><img src='https://github.com/sbejaoui.png' width='32' height='32' style='border-radius:50%;' alt='sbejaoui'/></a> | This module allows to create substitution rules for report actions.
[report_wkhtmltopdf_param](report_wkhtmltopdf_param/) | 18.0.1.0.1 |  | Add new parameters for a paper format to be used by wkhtmltopdf command as arguments.
[report_xlsx](report_xlsx/) | 18.0.1.0.1 |  | Base module to create xlsx report
[report_xlsx_helper](report_xlsx_helper/) | 18.0.1.0.0 |  | Report xlsx helpers
[report_xml](report_xml/) | 18.0.1.0.1 |  | Allow to generate XML reports
[sql_export](sql_export/) | 18.0.1.1.1 | <a href='https://github.com/legalsylvain'><img src='https://github.com/legalsylvain.png' width='32' height='32' style='border-radius:50%;' alt='legalsylvain'/></a> <a href='https://github.com/florian-dacosta'><img src='https://github.com/florian-dacosta.png' width='32' height='32' style='border-radius:50%;' alt='florian-dacosta'/></a> | Export data in csv file with SQL requests
[sql_export_excel](sql_export_excel/) | 18.0.1.0.1 | <a href='https://github.com/florian-dacosta'><img src='https://github.com/florian-dacosta.png' width='32' height='32' style='border-radius:50%;' alt='florian-dacosta'/></a> | Allow to export a sql query to an excel file.
[sql_export_mail](sql_export_mail/) | 18.0.1.0.0 | <a href='https://github.com/legalsylvain'><img src='https://github.com/legalsylvain.png' width='32' height='32' style='border-radius:50%;' alt='legalsylvain'/></a> | Send csv file generated by sql query by mail.
[sql_request_abstract](sql_request_abstract/) | 18.0.1.0.0 | <a href='https://github.com/legalsylvain'><img src='https://github.com/legalsylvain.png' width='32' height='32' style='border-radius:50%;' alt='legalsylvain'/></a> | Abstract Model to manage SQL Requests

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
