#!/usr/bin/env python3
"""
generate_2026_finance_calendar.py

Generic engine to build a 2026 Finance Closing & Tax Filing calendar for TBWA,
based on:
- A list of BIR/legal deadlines for 2026
- A template of internal workflow stages (prep/review/approval) per form
- A list of PH business-day holidays for 2026

It outputs:
- finance_calendar_2026.csv  (one row per internal task-stage)
- finance_events_2026.json   (ECharts-ready events array)
"""

from __future__ import annotations
import csv
import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import List, Dict


# -----------------------------
# Configuration
# -----------------------------

# You can override these via CLI wrapper, but this is a sane default layout
BIR_DEADLINES_CSV = Path("bir_deadlines_2026.csv")
WORKFLOW_TEMPLATE_CSV = Path("workflow_template.csv")
HOLIDAYS_2026_CSV = Path("ph_holidays_2026.csv")

OUT_CALENDAR_CSV = Path("finance_calendar_2026.csv")
OUT_EVENTS_JSON = Path("finance_events_2026.json")


@dataclass
class Holiday:
    day: date
    name: str


@dataclass
class Deadline:
    form_code: str          # e.g. 1601C, 2550Q
    period: str             # e.g. "Jan 2026", "Q1 2026"
    legal_deadline: date    # actual filing/payment deadline


@dataclass
class WorkflowStage:
    form_code: str          # match to Deadline.form_code
    stage: str              # "Preparation" | "Review" | "Approval" | ...
    role: str               # "Finance Supervisor"
    person_code: str        # CKVC / BOM / JPAL ...
    objective: str          # IM1 / IM2 etc (optional)
    offset_business_days: int
    # positive = N business days BEFORE legal deadline


@dataclass
class Task:
    form_code: str
    period: str
    stage: str
    role: str
    person_code: str
    objective: str
    legal_deadline: date
    planned_date: date


# -----------------------------
# Helpers
# -----------------------------

def load_holidays(path: Path) -> List[Holiday]:
    holidays: List[Holiday] = []
    if not path.exists():
        return holidays
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            y, m, d = map(int, row["date"].split("-"))
            holidays.append(Holiday(date(y, m, d), row.get("name", "")))
    return holidays


def is_business_day(d: date, holidays: List[Holiday]) -> bool:
    if d.weekday() >= 5:  # 5=Sat, 6=Sun
        return False
    return all(h.day != d for h in holidays)


def business_days_before(d: date, n: int, holidays: List[Holiday]) -> date:
    cur = d
    remaining = n
    while remaining > 0:
        cur -= timedelta(days=1)
        if is_business_day(cur, holidays):
            remaining -= 1
    return cur


def adjust_to_next_business_day(d: date, holidays: List[Holiday]) -> date:
    cur = d
    while not is_business_day(cur, holidays):
        cur += timedelta(days=1)
    return cur


def load_deadlines(path: Path) -> List[Deadline]:
    deadlines: List[Deadline] = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            y, m, d = map(int, row["legal_deadline"].split("-"))
            deadlines.append(
                Deadline(
                    form_code=row["form_code"].strip(),
                    period=row["period"].strip(),
                    legal_deadline=date(y, m, d),
                )
            )
    return deadlines


def load_workflow_template(path: Path) -> List[WorkflowStage]:
    stages: List[WorkflowStage] = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stages.append(
                WorkflowStage(
                    form_code=row["form_code"].strip(),
                    stage=row["stage"].strip(),
                    role=row["role"].strip(),
                    person_code=row["person_code"].strip(),
                    objective=row.get("objective", "").strip(),
                    offset_business_days=int(row["offset_business_days"]),
                )
            )
    return stages


# -----------------------------
# Core generation
# -----------------------------

def build_calendar(
    deadlines: List[Deadline],
    stages: List[WorkflowStage],
    holidays: List[Holiday],
) -> List[Task]:
    tasks: List[Task] = []

    # index template by form_code
    by_form: Dict[str, List[WorkflowStage]] = {}
    for st in stages:
        by_form.setdefault(st.form_code, []).append(st)

    for dl in deadlines:
        legal = adjust_to_next_business_day(dl.legal_deadline, holidays)
        for st in by_form.get(dl.form_code, []):
            planned = business_days_before(legal, st.offset_business_days, holidays)
            tasks.append(
                Task(
                    form_code=dl.form_code,
                    period=dl.period,
                    stage=st.stage,
                    role=st.role,
                    person_code=st.person_code,
                    objective=st.objective,
                    legal_deadline=legal,
                    planned_date=planned,
                )
            )
    tasks.sort(key=lambda t: (t.planned_date, t.form_code, t.stage))
    return tasks


def write_calendar_csv(tasks: List[Task], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "form_code",
                "period",
                "stage",
                "role",
                "person_code",
                "objective",
                "planned_date",
                "legal_deadline",
            ]
        )
        for t in tasks:
            writer.writerow(
                [
                    t.form_code,
                    t.period,
                    t.stage,
                    t.role,
                    t.person_code,
                    t.objective,
                    t.planned_date.isoformat(),
                    t.legal_deadline.isoformat(),
                ]
            )


def write_events_json(tasks: List[Task], path: Path) -> None:
    """Flatten to ECharts-friendly event list."""
    events = []
    for t in tasks:
        label = f"{t.form_code} {t.period} – {t.stage}"
        status = "open"  # update from completion data later if you want
        objective = t.objective or ("IM2" if "Tax" in label or "BIR" in label else "IM1")
        events.append(
            {
                "date": t.planned_date.isoformat(),
                "value": 1,
                "label": label,
                "role": t.role,
                "person": t.person_code,
                "objective": objective,
                "legal_deadline": t.legal_deadline.isoformat(),
                "status": status,
            }
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)


def main():
    holidays = load_holidays(HOLIDAYS_2026_CSV)
    deadlines = load_deadlines(BIR_DEADLINES_CSV)
    stages = load_workflow_template(WORKFLOW_TEMPLATE_CSV)

    tasks = build_calendar(deadlines, stages, holidays)
    write_calendar_csv(tasks, OUT_CALENDAR_CSV)
    write_events_json(tasks, OUT_EVENTS_JSON)
    print(f"Wrote {len(tasks)} tasks to {OUT_CALENDAR_CSV} and {OUT_EVENTS_JSON}")


if __name__ == "__main__":
    main()
