# Implementation Plan - Cheqroom Parity (Equipment Module)

## Goal
Refactor `ipai_equipment` to fully match the "Cheqroom on CE" specification, utilizing standard Odoo `maintenance.equipment` and adding robust booking and notification features.

## Proposed Changes

### [MODIFY] Module: `ipai_equipment`

#### Models
- **`models/equipment.py`**:
    - **CHANGE**: Inherit `maintenance.equipment` instead of defining `ipai.equipment.asset`.
    - **ADD**: Fields for `condition`, `status`, `current_custodian_id`, `equipment_code`.
- **`models/booking.py`** (New File):
    - **NEW**: `ipai.equipment.booking` model.
    - **FIELDS**: `equipment_ids` (Many2many), `start_datetime`, `end_datetime`, `state`, `is_overdue`.
    - **LOGIC**: Overlap prevention constraint, state transitions (Request -> Approve -> Check-out -> Return).
- **`models/notify.py`** (New File):
    - **NEW**: Cron logic for overdue checks and activity scheduling.

#### Views
- **`views/equipment_views.xml`**:
    - Extend `maintenance.hr_equipment_view_form` to add Cheqroom fields.
    - Add Kanban view showing status/condition.
- **`views/booking_views.xml`**:
    - Form, Tree, and **Calendar** view for bookings.
- **`views/menus.xml`**:
    - Update menus to point to the new views.

#### Data
- **`data/cron.xml`**:
    - Add cron job for `_cron_check_overdue`.

#### Tests
- **`tests/test_equipment_booking.py`**:
    - Implement automated tests for lifecycle, overlap, and overdue logic.

## Verification Plan
### Automated Tests
- Run `odoo-bin -c odoo.test.conf ... --test-tags=/ipai_equipment` to verify logic.

### Manual Verification
1.  **Equipment**: Create "Sony A7S3", set condition "Good".
2.  **Booking**: Book it for tomorrow. Verify Calendar view.
3.  **Conflict**: Try to book overlapping time. Expect error.
4.  **Overdue**: Backdate a booking, run cron, check for activity.
