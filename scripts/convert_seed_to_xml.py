import json

INPUT_FILE = 'odoo/ipai_finance_closing_seed.json'
OUTPUT_FILE = 'addons/ipai_finance_ppm/data/bir_schedule_seed.xml'

def convert():
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    xml_content = '<?xml version="1.0" encoding="utf-8"?>\n<odoo>\n    <data noupdate="1">\n'
    
    for record in data:
        record_id = record['id']
        model = record['model']
        fields = record['fields']
        
        xml_content += f'        <record id="{record_id}" model="{model}">\n'
        for fname, fval in fields.items():
            xml_content += f'            <field name="{fname}">{fval}</field>\n'
        xml_content += '        </record>\n'

    xml_content += '    </data>\n</odoo>'

    with open(OUTPUT_FILE, 'w') as f:
        f.write(xml_content)
    print(f"Generated {OUTPUT_FILE}")

if __name__ == "__main__":
    convert()
