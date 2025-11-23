import datetime
import csv
import json
import os

# Configuration
YEAR = 2026
HOLIDAYS_2026 = {
    datetime.date(2026, 1, 1): "New Year's Day",
    datetime.date(2026, 2, 25): "EDSA Revolution Anniversary",
    datetime.date(2026, 3, 30): "Maundy Thursday",
    datetime.date(2026, 3, 31): "Good Friday",
    datetime.date(2026, 4, 9): "Araw ng Kagitingan",
    datetime.date(2026, 5, 1): "Labor Day",
    datetime.date(2026, 6, 12): "Independence Day",
    datetime.date(2026, 8, 26): "National Heroes Day",
    datetime.date(2026, 11, 1): "All Saints' Day",
    datetime.date(2026, 11, 30): "Bonifacio Day",
    datetime.date(2026, 12, 8): "Feast of the Immaculate Conception",
    datetime.date(2026, 12, 25): "Christmas Day",
    datetime.date(2026, 12, 30): "Rizal Day",
}

# Forms Configuration (Base Deadlines)
# Rule: "Day X of following month"
FORMS = [
    {"code": "1601-C", "day_offset": 10, "jan_exception": 15}, # Jan deadline is 15th
    {"code": "0619-E", "day_offset": 10, "jan_exception": 15},
    {"code": "1601-EQ", "day_offset": 30, "quarterly": True}, # End of month following quarter? Usually last day.
    {"code": "2550Q", "day_offset": 25, "quarterly": True},
    {"code": "SSS", "day_offset": 30}, # Example
    {"code": "PhilHealth", "day_offset": 15}, # Example
    {"code": "Pag-IBIG", "day_offset": 15}, # Example
]

# Roles Mapping (Placeholder based on prompt)
ROLES = {
    "Prep": "Finance Supervisor",
    "Review": "Senior Finance Manager",
    "Approval": "Finance Director"
}

def is_business_day(date):
    if date.weekday() >= 5: # Sat=5, Sun=6
        return False
    if date in HOLIDAYS_2026:
        return False
    return True

def get_next_business_day(date):
    while not is_business_day(date):
        date += datetime.timedelta(days=1)
    return date

def subtract_business_days(date, days):
    current = date
    count = 0
    while count < days:
        current -= datetime.timedelta(days=1)
        if is_business_day(current):
            count += 1
    return current

def generate_schedule():
    schedule = []
    
    # Generate for each month
    for month in range(1, 13):
        # Calculate target month/year for the deadline (usually the following month)
        deadline_month = month + 1
        deadline_year = YEAR
        if deadline_month > 12:
            deadline_month = 1
            deadline_year = YEAR + 1
            
        # Skip if deadline falls out of 2026 (for Dec 2026 tasks due in Jan 2027, we might want them, but let's stick to 2026 calendar year tasks or 2026 coverage)
        # Prompt says "2026 monthly closing workflow". Usually means tasks *happening* in 2026.
        # Jan 2026 tasks cover Dec 2025 period.
        
        # Let's iterate periods: Dec 2025 to Nov 2026 (which have deadlines in 2026)
        # Actually prompt example: "January 2026 (Example form: 1601-C) Legal deadline: Jan 15, 2026"
        # So we look at deadlines occurring in 2026.
        
        for form in FORMS:
            # Determine base deadline date
            if form.get("quarterly"):
                # Only process if deadline_month is relevant (e.g. Apr, Jul, Oct, Jan)
                # Quarters end Mar, Jun, Sep, Dec. Deadlines in Apr, Jul, Oct, Jan.
                if month not in [3, 6, 9, 12]: 
                    continue
            
            day = form["day_offset"]
            if month == 12 and form.get("jan_exception") and deadline_month == 1:
                 # Special case for Jan deadline (covering Dec)
                 day = form["jan_exception"]
            
            # Construct naive deadline
            try:
                base_deadline = datetime.date(deadline_year, deadline_month, day)
            except ValueError:
                # Handle Feb 30 etc.
                # Logic: Last day of month
                if day >= 28:
                    next_m = deadline_month + 1
                    next_y = deadline_year
                    if next_m > 12:
                        next_m = 1
                        next_y += 1
                    first_of_next = datetime.date(next_y, next_m, 1)
                    base_deadline = first_of_next - datetime.timedelta(days=1)
            
            # 1. Adjust Deadline (D)
            final_deadline = get_next_business_day(base_deadline)
            
            # 2. Calculate Milestones
            # Prep = D - 4 bus days
            # Review = D - 2 bus days
            # Approval = D - 1 bus day
            
            date_prep = subtract_business_days(final_deadline, 4)
            date_review = subtract_business_days(final_deadline, 2)
            date_approval = subtract_business_days(final_deadline, 1)
            
            period_name = datetime.date(YEAR, month, 1).strftime("%b %Y") # e.g. Jan 2026 covering Dec? 
            # Wait, if deadline is Jan 15 2026, it covers Dec 2025.
            # Prompt says "January 2026 (Example form: 1601-C)". 
            # Let's assume the "Period" label aligns with the deadline month for simplicity or the prompt's convention.
            # Actually prompt says "Period Covered (Dec 2025)" for Jan deadline.
            # Let's use Deadline Month as the grouper for the schedule.
            
            schedule.append({
                "Form": form["code"],
                "Deadline": final_deadline,
                "Prep": date_prep,
                "Review": date_review,
                "Approval": date_approval,
                "Period": f"Month {month}" # Simplified
            })

    return schedule

def write_csv(schedule):
    with open('calendar/2026_FinanceClosing_Master.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Form', 'Period', 'Deadline', 'Prep Date', 'Review Date', 'Approval Date'])
        for item in schedule:
            writer.writerow([
                item['Form'],
                item['Period'],
                item['Deadline'].isoformat(),
                item['Prep'].isoformat(),
                item['Review'].isoformat(),
                item['Approval'].isoformat()
            ])

def write_ics(schedule):
    with open('calendar/FinanceClosing_RecurringTasks.ics', 'w') as f:
        f.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//InsightPulse//Finance Schedule//EN\n")
        for item in schedule:
            # Create events for each stage
            stages = [
                ("Prep", item['Prep'], "Finance Supervisor"),
                ("Review", item['Review'], "Senior Finance Manager"),
                ("Approval", item['Approval'], "Finance Director"),
                ("Filing", item['Deadline'], "Finance Team")
            ]
            for stage, date, role in stages:
                dt_str = date.strftime("%Y%m%d")
                f.write("BEGIN:VEVENT\n")
                f.write(f"SUMMARY:{stage}: {item['Form']} ({role})\n")
                f.write(f"DTSTART;VALUE=DATE:{dt_str}\n")
                f.write(f"DTEND;VALUE=DATE:{dt_str}\n")
                f.write(f"DESCRIPTION:Task: {stage} for {item['Form']}. Role: {role}\n")
                f.write("END:VEVENT\n")
        f.write("END:VCALENDAR\n")

def write_odoo_seed(schedule):
    data = []
    for item in schedule:
        # Create a record for ipai.bir.form.schedule
        data.append({
            "id": f"schedule_{item['Form']}_{item['Deadline'].strftime('%Y%m%d')}",
            "model": "ipai.bir.form.schedule",
            "fields": {
                "form_code": item['Form'],
                "period": item['Period'],
                "bir_deadline": item['Deadline'].isoformat(),
                "prep_date": item['Prep'].isoformat(),
                "review_date": item['Review'].isoformat(),
                "approval_date": item['Approval'].isoformat(),
            }
        })
    
    with open('odoo/ipai_finance_closing_seed.json', 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    sched = generate_schedule()
    write_csv(sched)
    write_ics(sched)
    write_odoo_seed(sched)
    print("Artifacts generated successfully.")
