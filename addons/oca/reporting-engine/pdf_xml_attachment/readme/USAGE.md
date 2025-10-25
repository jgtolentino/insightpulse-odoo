Inside Odoo env:

    res = env["pdf.xml.tool"].pdf_get_xml_files(pdf_filecontent)

    new_pdf_filecontent = env["pdf.xml.tool"].pdf_embed_xml(pdf_filecontent, filename, xml)

Outside Odoo env:

    from odoo.addons.pdf_xml_attachment.utils import PDFParser
    [...]
    res = PDFParser(pdf_filecontent).get_xml_files()
