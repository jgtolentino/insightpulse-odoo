import csv
import datetime

INPUT_CSV = 'finance_calendar_2026.csv'
OUTPUT_XML = 'addons/ipai_finance_ppm/data/bir_schedule_seed.xml'

def convert():
    # Read CSV
    tasks = []
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tasks.append(row)

    # Group by Form+Period to create Schedule records
    schedules = {}
    for t in tasks:
        key = (t['form_code'], t['period'])
        if key not in schedules:
            schedules[key] = {
                'form_code': t['form_code'],
                'period': t['period'],
                'bir_deadline': t['legal_deadline'],
                'steps': []
            }
        
        # Map stage to specific date fields if they exist on the model
        if t['stage'] == 'Preparation':
            schedules[key]['prep_date'] = t['planned_date']
            schedules[key]['responsible_prep_id'] = t['person_code'] # Need to handle Many2one mapping later, for now string/char or ignore
        elif t['stage'] == 'Review':
            schedules[key]['review_date'] = t['planned_date']
            schedules[key]['responsible_review_id'] = t['person_code']
        elif t['stage'] == 'Approval':
            schedules[key]['approval_date'] = t['planned_date']
            schedules[key]['responsible_approval_id'] = t['person_code']
            
        schedules[key]['steps'].append(t)

    # Generate XML
    xml_content = '<?xml version="1.0" encoding="utf-8"?>\n<odoo>\n    <data noupdate="1">\n'
    
    for (form, period), data in schedules.items():
        record_id = f"schedule_{form}_{period.replace(' ', '_')}"
        xml_content += f'        <record id="{record_id}" model="ipai.bir.form.schedule">\n'
        xml_content += f'            <field name="form_code">{data["form_code"]}</field>\n'
        xml_content += f'            <field name="period">{data["period"]}</field>\n'
        xml_content += f'            <field name="bir_deadline">{data["bir_deadline"]}</field>\n'
        
        if 'prep_date' in data:
            xml_content += f'            <field name="prep_date">{data["prep_date"]}</field>\n'
        if 'review_date' in data:
            xml_content += f'            <field name="review_date">{data["review_date"]}</field>\n'
        if 'approval_date' in data:
            xml_content += f'            <field name="approval_date">{data["approval_date"]}</field>\n'
            
        # Add steps
        xml_content += '            <field name="step_ids">\n'
        for i, step in enumerate(data['steps']):
            xml_content += f'                <record id="{record_id}_step_{i}" model="ipai.bir.process.step">\n'
            xml_content += f'                    <field name="step_no">{i+1}</field>\n'
            xml_content += f'                    <field name="title">{step["stage"]}</field>\n'
            xml_content += f'                    <field name="role">{step["role"]}</field>\n'
            # Note: person_id is Many2one, skipping for now to avoid XML errors if record doesn't exist
            # xml_content += f'                    <field name="person_id" ref="..."/>\n' 
            xml_content += f'                </record>\n'
        xml_content += '            </field>\n'
        
        xml_content += '        </record>\n'

    xml_content += '    </data>\n</odoo>'

    with open(OUTPUT_XML, 'w') as f:
        f.write(xml_content)
    print(f"Generated {OUTPUT_XML}")

if __name__ == "__main__":
    convert()
