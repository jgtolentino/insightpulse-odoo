============================
Clarity PPM Parity for Odoo
============================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

|badge1| |badge2|

Complete Broadcom Clarity PPM feature parity implementation for Odoo 18 CE.

This module implements the complete Clarity PPM Work Breakdown Structure (WBS) hierarchy in Odoo:

- **Project**: Root container with Clarity ID, health status, and variance tracking
- **Phase**: WBS grouping via parent tasks with phase types and gates
- **Milestone**: Zero-duration progress markers with approval workflows
- **Task**: Units of work with dependencies (FS, SS, FF, SF) and critical path analysis
- **To-Do Item**: Granular checklists with assignees and due dates

**Table of contents**

.. contents::
   :local:

Features
========

Project Extensions
------------------

* **Clarity ID field** for project tracking and integration
* **Health status indicators** (Green/Yellow/Red)
* **Baseline vs Actual variance tracking** for schedule analysis
* **Portfolio/Program classification** via project categories
* **Overall progress metrics** rolled up from phases

Phase Management
----------------

* **Phases as specialized parent tasks** with phase types
* **Phase gates** with approval workflows
* **Progress rollup** from child tasks
* **Phase variance tracking** against baseline
* **Phase status lifecycle** (Not Started → In Progress → Completed)

Milestone Features
------------------

* **Milestone types** (Phase Gate, Deliverable, Approval, Decision Point, etc.)
* **Gate status tracking** (Not Started → Passed/Failed)
* **Approval workflows** with designated approvers
* **Completion criteria** and deliverables documentation
* **Automatic alerts** X days before deadline
* **Risk assessment** and mitigation notes

Task Enhancements
-----------------

* **Task dependencies** (Finish-to-Start, Start-to-Start, etc.) via OCA module
* **Critical path analysis** with total float and free float calculations
* **WBS code generation** (hierarchical numbering like 1.2.3.1)
* **Earned Value Management** (PV, EV, AC, SV, CV metrics)
* **Resource allocation** percentage tracking
* **Lag and lead** support for dependencies

To-Do Items
-----------

* **Granular checklists** within tasks
* **Individual assignees** and due dates per item
* **Priority levels** (Low/Normal/High/Urgent)
* **Effort tracking** (estimated vs actual hours)
* **Blocker management** with descriptions

Integration
-----------

* **Finance PPM integration** for BIR tax filing milestones
* **Mattermost notifications** for phase gate alerts
* **Gantt chart visualization** via OCA project_timeline
* **Complete WBS hierarchy** support

Installation
============

Dependencies
------------

This module requires the following OCA modules from the ``project`` repository:

* project_key
* project_category
* project_wbs
* project_parent_task_filter
* project_milestone
* project_task_milestone
* project_task_dependency
* project_task_checklist
* project_timeline

Installation Steps
------------------

1. Clone OCA project repository::

    git clone https://github.com/OCA/project.git -b 18.0 /path/to/addons/oca-project

2. Update Odoo configuration to include OCA addons path::

    addons_path = /path/to/odoo/addons,/path/to/addons/oca-project,/path/to/custom/addons

3. Update the addons list in Odoo

4. Install required OCA modules in this order:

   a. project_key
   b. project_category
   c. project_wbs
   d. project_parent_task_filter
   e. project_milestone
   f. project_task_milestone
   g. project_task_dependency
   h. project_task_checklist
   i. project_timeline

5. Install this module (ipai_clarity_ppm_parity)

Configuration
=============

1. **Set up Portfolios**: Go to Project → Configuration → Project Categories
2. **Configure Phase Types**: Standard Clarity phase types are pre-configured
3. **Set Baseline Dates**: For each project, use "Set Current as Baseline" button
4. **Configure Alerts**: Set alert days before milestone deadlines (default: 7 days)

Usage
=====

Creating a Clarity-Compliant Project
-------------------------------------

1. Create a new project with a unique Clarity ID (e.g., PRJ-2025-001)
2. Assign to a Portfolio
3. Set baseline dates
4. Add phases using the "Is Phase" checkbox
5. Create milestones with approval requirements
6. Add tasks under phases
7. Define task dependencies (predecessors/successors)
8. Add to-do items to tasks for granular tracking

Phase Gate Workflow
-------------------

1. Create a phase with "Has Phase Gate" enabled
2. Create a corresponding milestone of type "Phase Gate"
3. Add tasks to the phase
4. Link tasks to the gate milestone
5. When all tasks complete, approve the milestone
6. Approve the phase gate to proceed to next phase

Variance Analysis
-----------------

1. Set project baseline dates
2. Track actual start/finish dates
3. View variance in days on project form
4. Monitor health status and overall status
5. Use variance reports for stakeholder communication

Milestone Alerts
----------------

* Automatic alerts sent X days before deadline (configurable)
* Manual alert sending via "Send Alert" button
* Notifications posted to Mattermost (if configured)
* Alerts logged in project chatter

Known Issues / Roadmap
======================

* Critical path calculation is simplified (not full CPM network analysis)
* Earned Value metrics require manual cost input
* Resource leveling not implemented
* What-if scenario analysis not available
* Integration with external Clarity PPM via API (planned for v2.0)

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/insightpulseai/odoo-modules/issues>`_.

Credits
=======

Authors
~~~~~~~

* InsightPulse AI

Contributors
~~~~~~~~~~~~

* Jake Tolentino <jake@insightpulseai.net>

Maintainers
~~~~~~~~~~~

This module is maintained by InsightPulse AI for OCA compliance and Clarity PPM parity.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is part of the OCA project ecosystem.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.
