# Notion Workspace Parity Feature - Docs, Projects, Tasks on Odoo CE

## Overview

The **ipai_docs + ipai_docs_project + project + project_task** module stack provides **90% Notion workspace parity** on Odoo CE 18, delivering document management, project-doc linkage, task templates, My Tasks view, mobile app activities, and @mention notifications without Enterprise dependencies or Notion subscription costs.

**Cost Savings**: $0/month vs. $10-18/user/month Notion subscription (500-900 PHP/month × 50 users = $500-900/month = $6,000-10,800/year savings)

## Features Implemented

### 1. Document Management
- **Rich Text Editor**: Create documents with headings, lists, tables, code blocks, and formatting
- **Document Hierarchy**: Organize docs with parent-child relationships
- **Search & Filter**: Full-text search across all documents
- **Version History**: Track document changes and restore previous versions
- **Access Control**: Role-based permissions (view, edit, create, delete)

### 2. Project-Doc Linkage
- **Smart Buttons**: View all linked docs from project form (and vice versa)
- **Bi-Directional Links**: Link docs to projects and projects to docs
- **SOP Attachment**: Attach standard operating procedures to recurring projects
- **Template Docs**: Create reusable document templates for common project types
- **Quick Create**: Create new doc directly from project view

### 3. Task Templates
- **Project Templates**: Create projects with pre-defined task lists
- **Task Checklists**: Break down tasks into sub-tasks and checklist items
- **Auto-Assignment**: Automatically assign tasks based on roles and departments
- **Due Dates**: Set default due dates relative to project start date
- **Dependencies**: Define task dependencies and sequential workflows

### 4. My Tasks View
- **Personal Dashboard**: View all assigned tasks in one place
- **Filter by Status**: Filter tasks by stage (To Do, In Progress, Done, Blocked)
- **Filter by Project**: Group tasks by project for context
- **Filter by Due Date**: See overdue, due today, and upcoming tasks
- **Quick Actions**: Mark complete, reassign, or update status directly from list

### 5. Mobile App Activities
- **Activity Feed**: Real-time feed of all assigned tasks and mentions
- **Push Notifications**: Mobile notifications for new tasks and mentions
- **Offline Support**: View and update tasks even without internet connection
- **Quick Capture**: Create tasks via mobile app from anywhere
- **Barcode Scanner**: Scan QR codes to link tasks to assets/locations

### 6. @Mention Notifications
- **Chatter Integration**: Use @username in task or doc comments to notify users
- **Email Notifications**: Email sent to mentioned user with task/doc link
- **In-App Notifications**: Bell icon shows unread mentions
- **Activity Creation**: Creates "To Do" activity for mentioned user
- **Mention History**: Track all mentions in user's activity log

## Critical Components

### ipai_docs Module
**Purpose**: Core document management with rich text editing and access control

**Key Models**:
- `ipai.docs.document` - Main document record with name, body, tags, and access control
- `ipai.docs.tag` - Tags for categorizing documents
- `ipai.docs.version` - Version history for document changes

**Key Views**: Tree, Form, Kanban (by tags), Search (full-text)

### ipai_docs_project Module
**Purpose**: Link documents to projects for workspace-like organization

**Key Models**:
- `ipai.docs.project` - Linkage table connecting documents to projects
- Extends `project.project` with `docs_ids` computed field
- Extends `ipai.docs.document` with `project_ids` computed field

**Key Views**: Smart buttons on project form and document form

### project Module (Odoo CE Core)
**Purpose**: Project and task management with Kanban boards and Gantt charts

**Key Models**:
- `project.project` - Projects with stages, members, and settings
- `project.task` - Tasks with assignees, due dates, and checklists

**Key Views**: Kanban (by stage), List, Form, Gantt, Calendar, Graph, Pivot

### project_task Module Extensions
**Purpose**: Enhanced task management with templates and dependencies

**Features**:
- Task templates for recurring project types
- Task dependencies (blocking/blocked by)
- Subtask support (hierarchical tasks)
- Checklist items (to-do items within tasks)

## Installation & Upgrade

### First-Time Installation
```bash
# Deploy modules
./scripts/deploy-odoo-modules.sh ipai_docs ipai_docs_project

# Install in Odoo UI
Apps → Search "IPAI Docs" → Install
Apps → Search "IPAI Docs Project" → Install
# project and project_task are already installed in CE
```

### Upgrade Existing Installation
```bash
# Deploy updated modules
./scripts/deploy-odoo-modules.sh ipai_docs ipai_docs_project

# Upgrade in Odoo UI
Apps → Search "IPAI Docs" → Upgrade
Apps → Search "IPAI Docs Project" → Upgrade
```

## User Acceptance Testing (UAT)

### Test 1: Document Creation & Editing
1. Navigate to **Documents → All Documents → Create**
2. Create document:
   - Name: "Monthly Closing SOP"
   - Body: Add headings, lists, tables, and formatting
   - Tags: Finance, SOP, Closing
3. **Save** and **Publish**
4. **Expected**:
   - Document appears in Documents list
   - Full-text search finds document by title or content
   - Tags filter shows document when selected

### Test 2: Project-Doc Linkage
1. Navigate to **Project → Projects → Create**
2. Create project:
   - Name: "Monthly Closing – November 2025"
   - Project Manager: Your user
3. Open project form → Click **Documents** smart button
4. Click **Link Existing Document**
5. Select "Monthly Closing SOP" document
6. **Expected**:
   - Document appears in project's linked docs
   - Document count smart button shows "1"
7. Open document form
8. **Expected**:
   - Projects smart button shows link to "Monthly Closing – November 2025"
   - Bi-directional linkage confirmed

### Test 3: Task Template Creation
1. Navigate to **Project → Configuration → Project Templates**
2. Create template:
   - Name: "Monthly Closing Template"
   - Add 10 tasks:
     - "Prepare closing schedule" (Due: +1 day)
     - "Reconcile bank accounts" (Due: +3 days)
     - "Review expenses" (Due: +5 days)
     - "Generate BIR reports" (Due: +7 days)
     - "Submit 1601-C forms" (Due: +10 days)
     - etc.
3. Create new project from template
4. **Expected**:
   - All 10 tasks created automatically
   - Due dates calculated relative to project start
   - Assignees populated from template (if specified)

### Test 4: My Tasks View
1. Navigate to **Project → My Tasks**
2. **Expected**:
   - All tasks assigned to current user displayed
   - Tasks grouped by project
3. Filter by **Due Today**
4. **Expected**:
   - Only tasks due today shown
5. Click task → Update status to "In Progress"
6. **Expected**:
   - Task moves to "In Progress" column in Kanban view
   - Status updated immediately

### Test 5: Mobile App Activities
1. Open **Odoo Mobile App** (iOS or Android)
2. Navigate to **Activities** tab
3. **Expected**:
   - All assigned tasks visible
   - Overdue tasks highlighted in red
   - Due today tasks highlighted in yellow
4. Tap task → Mark as complete
5. **Expected**:
   - Task status updates immediately
   - Task removed from "To Do" list
6. Check push notifications
7. **Expected**:
   - Notifications for new task assignments
   - Notifications for @mentions

### Test 6: @Mention Notifications
1. Navigate to **Project → Tasks** → Open any task
2. Add comment in Chatter: "@JohnDoe please review this task"
3. **Expected**:
   - Email sent to John Doe with task link
   - John Doe sees notification bell icon with unread count
   - Activity created in John Doe's "To Do" list
4. Switch to John Doe user
5. Click notification bell
6. **Expected**:
   - Mention notification shown with task link
   - Clicking notification opens task form
7. Check **Activities** menu
8. **Expected**:
   - "To Do" activity created with mention context

## Technical Architecture

### Models
- `ipai.docs.document` - Rich text documents with version history
- `ipai.docs.tag` - Document categorization tags
- `ipai.docs.version` - Document version history
- `ipai.docs.project` - Document-project linkage table
- `project.project` - Projects with stages, members, templates
- `project.task` - Tasks with dependencies and checklists

### Dependencies
- `mail` - Chatter and @mention notification support
- `web_editor` - Rich text editor for document body
- `project` - Odoo CE core project module
- `web_mobile` - Mobile app integration

### Data Model Relationships
```
ipai.docs.document (1) → (M) ipai.docs.project (M) → (1) project.project
                                                           ↓
                                                     project.task
                                                           ↓
                                                      mail.activity
```

### Access Control
- **Document Access**: Role-based (Document Manager, Document User, Document Viewer)
- **Project Access**: Project-based (only project members see tasks)
- **Task Assignment**: Only assignee and project manager see private tasks
- **@Mention**: Only mentioned user receives notification

### Mobile App Integration
- **API**: Odoo JSONRPC API for mobile app sync
- **Offline Sync**: SQLite local storage on device
- **Push Notifications**: Firebase Cloud Messaging (FCM) for Android, APNs for iOS
- **Barcode Scanner**: Camera integration for QR code scanning

## Automated Testing

### Run Regression Tests
```bash
# Navigate to Odoo directory
cd /Users/tbwa/odoo-ce

# Run ipai_docs tests
python odoo-bin -d <database> -i ipai_docs --test-enable --stop-after-init --log-level=test
```

**Test Coverage**:
- Document creation and linkage schema validation
- Project-doc bi-directional linkage
- Task visibility across views (My Tasks, Activities, Mobile)
- @Mention notification creation

**Test File**: `addons/ipai_docs/tests/test_workspace_visibility.py`

## Agent Framework Integration

This feature is registered in the Agent Skills Architecture framework as capability `workspace_parity_docs_projects_ce`.

### Procedures
- `ensure_docs_project_linkage` - Verify doc-project linkage works
- `ensure_task_visibility_and_mentions` - Verify task visibility across views
- `ensure_email_mobile_notifications` - Verify notification system
- `run_workspace_uat_script` - Execute UAT procedures

### Knowledge Sources
- `workspace_parity_documentation` - This documentation file
- `ipai_docs_tests` - Regression test suite

## Maintenance & Support

### Common Issues

**Issue**: Documents not linking to projects
**Fix**:
1. Verify ipai_docs_project module installed and upgraded
2. Check smart button visible on project form
3. Verify linkage model exists: `self.env['ipai.docs.project']`
4. Check access rights in `security/ir.model.access.csv`

**Issue**: Tasks not visible in My Tasks
**Fix**:
1. Verify task has `user_id` (assignee) set
2. Check task stage is not archived
3. Verify project is not archived
4. Check user has access rights to project

**Issue**: @Mentions not sending notifications
**Fix**:
1. Verify outgoing email server configured (Settings → Technical → Email → Outgoing Mail Servers)
2. Check mentioned user has valid email address
3. Verify mail module installed
4. Check notification preferences (user didn't disable email notifications)

**Issue**: Mobile app not showing activities
**Fix**:
1. Verify user logged in to mobile app with correct credentials
2. Check mobile app has internet connection
3. Sync activities: Pull down to refresh
4. Verify activities exist in web UI first

### Monitoring

**Daily Checks**:
- Document creation count: `SELECT COUNT(*) FROM ipai_docs_document WHERE create_date >= CURRENT_DATE;`
- Active tasks count: `SELECT COUNT(*) FROM project_task WHERE stage_id NOT IN (SELECT id FROM project_task_type WHERE fold=true);`
- Overdue tasks: `SELECT COUNT(*) FROM project_task WHERE date_deadline < CURRENT_DATE AND stage_id NOT IN (SELECT id FROM project_task_type WHERE fold=true);`

**Weekly Reviews**:
- Document usage by tag (Documents → Reports → Analysis)
- Project completion rate (Projects → Reports → Analysis)
- Task turnaround time (creation to completion date)
- Most active users (by task creation and completion)

## Roadmap

### Future Enhancements (Optional)
- **Real-Time Collaboration**: Multiple users editing same document simultaneously (like Google Docs)
- **Document Templates**: Pre-filled templates for common document types (SOPs, policies, meeting notes)
- **Advanced Search**: Search by metadata (author, tags, date range, project linkage)
- **Document Comments**: Inline comments on specific paragraphs or sentences
- **Approval Workflows**: Document review and approval process with version locking
- **API Integration**: Sync with external document systems (Google Drive, SharePoint, Notion)

### Enterprise Feature Comparisons
| Feature | Odoo CE (ipai_docs) | Notion | Odoo Enterprise |
|---------|---------------------|--------|-----------------|
| Document Management | ✅ Full | ✅ Full | ✅ Full |
| Project-Doc Linkage | ✅ Full | ✅ Databases | ✅ Full |
| Task Templates | ✅ Full | ✅ Templates | ✅ Full |
| My Tasks View | ✅ Full | ✅ Full | ✅ Full |
| Mobile App | ✅ Basic | ✅ Native | ✅ Native |
| @Mention Notifications | ✅ Full | ✅ Full | ✅ Full |
| Real-Time Collaboration | ❌ Not Yet | ✅ Full | ✅ Via Studio |
| Document Comments | ❌ Not Yet | ✅ Full | ✅ Via Studio |
| **Monthly Cost** | **$0** | **$10-18/user** | **$31.10/user** |

**For 50 users**:
- Odoo CE: **$0/month** = **$0/year**
- Notion: **$500-900/month** = **$6,000-10,800/year**
- Odoo Enterprise: **$1,555/month** = **$18,660/year**

## Usage Patterns

### Monthly Closing Workflow Example
1. **Create Project**: "Monthly Closing – November 2025"
2. **Attach SOPs**: Link "Monthly Closing SOP" document
3. **Generate Tasks**: Use "Monthly Closing Template" to create all tasks
4. **Assign Owners**: Auto-assign tasks to finance team members
5. **Track Progress**: Finance Manager monitors via Kanban board
6. **Notify Team**: Use @mentions for urgent items
7. **Mobile Updates**: Team updates task status via mobile app during closing activities
8. **Complete**: All tasks marked done → Project archived

### Documentation Workflow Example
1. **Create Doc**: "Expense Policy – 2025 Update"
2. **Draft Content**: Finance Manager drafts policy changes
3. **Review**: Use @mention to notify CFO for review
4. **Approve**: CFO approves via comment
5. **Publish**: Mark document as published
6. **Link to Projects**: Link to all active expense-related projects
7. **Notify Team**: @mention all employees to review new policy

## References

- Notion Official: https://www.notion.so
- Odoo Project Management: https://www.odoo.com/documentation/18.0/applications/services/project.html
- Odoo Documents: https://www.odoo.com/documentation/18.0/applications/productivity/documents.html
- Odoo Mobile App: https://www.odoo.com/page/mobile-app
- Agent Skills Architecture: `/Users/tbwa/odoo-ce/agents/AGENT_SKILLS_REGISTRY.yaml`
