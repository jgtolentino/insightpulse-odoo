---
name: superset-dashboard-designer
description: Expert guidance for designing effective Apache Superset dashboards with professional layouts, intuitive navigation, and optimized user experience. This skill helps you create dashboards that tell clear data stories - with specific templates for Finance SSC, BIR compliance, and operational monitoring.
license: MIT
---

# Superset Dashboard Designer Skill

## Purpose
Expert guidance for designing effective Apache Superset dashboards with professional layouts, intuitive navigation, and optimized user experience. This skill helps you create dashboards that tell clear data stories - with specific templates for Finance SSC, BIR compliance, and operational monitoring.

## When to Use This Skill
- Designing new dashboards from scratch
- Improving existing dashboard layouts
- Building executive/operational/analytical dashboards
- Creating Finance SSC monitoring solutions
- Implementing BIR compliance tracking
- Designing InsightPulse AI analytics views

## Dashboard Design Philosophy

### The 3-Second Rule
**Users should understand your dashboard's purpose in 3 seconds:**
1. **Clear title** - What is this dashboard about?
2. **Key metrics visible** - Most important numbers at top
3. **Visual hierarchy** - Eyes drawn to what matters most

### The 5-Click Rule
**Users should find any insight within 5 clicks:**
1. Dashboard selection
2. Date range filter (if needed)
3. Primary filter (agency, category, etc.)
4. Chart interaction (drill-down)
5. Detail view or export

## Dashboard Layout Grid System

### Superset Grid Basics
- **Grid Units:** 24 columns × infinite rows
- **Minimum Height:** 1 row = ~40px
- **Recommended Chart Heights:**
  - Big Numbers: 2-3 rows
  - Bar/Line Charts: 6-10 rows
  - Tables: 8-15 rows
  - Complex visuals: 10-20 rows

### Standard Layouts

#### **Layout 1: Executive Dashboard (F-Pattern)**
```
┌─────────────────────────────────────────────┐
│ Dashboard Title + Date Range Filter         │ Row 1-2
├─────────────────────────────────────────────┤
│ [KPI 1]  [KPI 2]  [KPI 3]  [KPI 4]         │ Row 3-5
│ Big Num  Big Num  Big Num  Big Num          │
├─────────────────────────────────────────────┤
│ [Primary Chart - Full Width]                │ Row 6-15
│ (Line/Area Chart - Trend Over Time)         │
├─────────────────────────────────────────────┤
│ [Chart Left] │ [Chart Right]                │ Row 16-25
│ (Bar Chart)  │ (Donut/Table)                │
└─────────────────────────────────────────────┘
```

**Use For:** Executive summaries, high-level monitoring
**Examples:** BIR Compliance Overview, Monthly Performance Summary

#### **Layout 2: Operational Dashboard (Grid)**
```
┌─────────────────────────────────────────────┐
│ Filters: [Agency] [Status] [Date Range]     │ Row 1-2
├─────────────────────────────────────────────┤
│ [Status 1] [Status 2] [Status 3] [Status 4] │ Row 3-5
│  Big Num    Big Num    Big Num    Big Num   │
├─────────────────────────────────────────────┤
│ [Chart 1]          │ [Chart 2]              │ Row 6-15
│ (Bar - Status)     │ (Line - Trend)         │
├─────────────────────────────────────────────┤
│ [Detailed Table - Full Width]               │ Row 16-30
│ (Task List with Actions)                    │
└─────────────────────────────────────────────┘
```

**Use For:** Daily operations, task tracking
**Examples:** Month-End Closing Tracker, InsightPulse Processing Monitor

#### **Layout 3: Analytical Dashboard (Drill-Down)**
```
┌─────────────────────────────────────────────┐
│ [Filter Bar] + [Time Comparison Toggle]     │ Row 1-2
├─────────────────────────────────────────────┤
│ [Summary KPI Row]                           │ Row 3-5
├─────────────────────────────────────────────┤
│ [Primary Analysis Chart - Full Width]       │ Row 6-18
│ (Interactive, Drill-Down Enabled)           │
├─────────────────────────────────────────────┤
│ [Chart A] │ [Chart B] │ [Chart C]          │ Row 19-28
│ (Related Metrics - Side by Side)            │
├─────────────────────────────────────────────┤
│ [Detail Table or Drill-Down View]           │ Row 29-40
└─────────────────────────────────────────────┘
```

**Use For:** Deep analysis, exploration
**Examples:** Revenue Analysis, Document Processing Performance

---

## Visual Hierarchy Principles

### 1. Size Hierarchy
**Larger = More Important**

```yaml
Priority 1 (Largest):
  - Primary KPI big numbers
  - Main trend chart
  - Critical alerts
  Size: 6-8 grid columns, 6-12 rows

Priority 2 (Medium):
  - Supporting charts
  - Comparison views
  - Category breakdowns
  Size: 6-12 grid columns, 6-10 rows

Priority 3 (Smaller):
  - Detail tables
  - Reference data
  - Supplementary metrics
  Size: 4-6 grid columns, 4-8 rows
```

### 2. Position Hierarchy
**Top-Left = Highest Priority**

Reading pattern: **F-Pattern** (Western audiences)
```
HIGH   → → → Medium
  ↓
  ↓
Medium → → → Low
  ↓
Low    → → → Low
```

**Dashboard Zones:**
- **Top Row:** Most critical KPIs (Big Numbers)
- **Upper Left:** Primary chart/analysis
- **Center:** Supporting visualizations
- **Right Side:** Filters, context, details
- **Bottom:** Detailed tables, drill-downs

### 3. Color Hierarchy
**Use color to guide attention:**

```yaml
High Attention:
  - Red: Alerts, overdue, errors (use sparingly!)
  - Green: Success, on-track, completed
  - Yellow/Orange: Warnings, pending

Medium Attention:
  - Blue: Primary data, informational
  - Purple: Secondary categories

Low Attention:
  - Gray: Inactive, disabled, context
  - White/Light: Background, spacing
```

---

## Filter Design Best Practices

### Filter Placement Options

#### **Option 1: Top Bar (Recommended)**
```
┌─────────────────────────────────────────────┐
│ [Filter 1] [Filter 2] [Filter 3] [Date]    │
└─────────────────────────────────────────────┘
```
**Pros:** Always visible, consistent location
**Use When:** 2-5 key filters, executive/operational dashboards

#### **Option 2: Left Sidebar**
```
┌─────┬───────────────────────────────────────┐
│ F1  │                                       │
│ F2  │        Dashboard Content              │
│ F3  │                                       │
│ F4  │                                       │
└─────┴───────────────────────────────────────┘
```
**Pros:** More filter space, doesn't push content down
**Use When:** 6+ filters, analytical dashboards

#### **Option 3: Collapsible Panel**
```
┌─────────────────────────────────────────────┐
│ [▼ Advanced Filters]                        │
└─────────────────────────────────────────────┘
```
**Pros:** Clean initial view, reduces clutter
**Use When:** Optional filters, mobile dashboards

### Filter Types and When to Use

| Filter Type | Best For | Example |
|------------|----------|---------|
| **Dropdown (Single)** | Select one option | Agency selection |
| **Dropdown (Multi)** | Select multiple | Multiple form types |
| **Date Range** | Time period selection | Filing date range |
| **Radio Buttons** | 2-4 options, always visible | Status (Active/Inactive) |
| **Text Search** | Finding specific items | Search invoice number |
| **Slider** | Numeric range | Amount range |
| **Checkbox** | Boolean toggles | Show only overdue |

### Filter Configuration

**Default Values:**
```yaml
# Set smart defaults
Agency Filter: "All Agencies" (not blank)
Date Range: "Current Month" or "Last 30 Days"
Status: "Active" (exclude archived by default)
```

**Filter Dependencies:**
```yaml
# Parent → Child relationship
Country → City → Region
  - City list updates based on Country selection
  - Region list updates based on City selection

Agency → Department → Employee
  - Cascade filters for organizational hierarchy
```

**Required vs Optional:**
```yaml
Required Filters:
  - Force user to make selection
  - Use for: Date range (to prevent huge queries)
  
Optional Filters:
  - Allow "All" option
  - Use for: Most category filters
```

---

## Cross-Filtering & Interactivity

### Cross-Filtering Setup

**What is Cross-Filtering?**
Clicking on a chart element filters other charts on the dashboard.

**Example:**
```
User clicks "CKVC" in Agency Bar Chart
  → All other charts update to show only CKVC data
  → Filter indicator appears at top
  → User can clear to return to all agencies
```

**Configuration:**
```yaml
Enable Cross-Filtering:
  Dashboard Settings → Enable cross-filtering
  
Per Chart:
  Chart Settings → Emit Dashboard Cross Filters: ON
  Chart Settings → Can Be Filtered By Dashboard Filters: ON
```

**Best Practices:**
- ✅ Enable on summary charts (pie, bar) that show categories
- ✅ Clear visual feedback when cross-filter is active
- ❌ Don't enable on too many charts (confusing)
- ❌ Avoid on charts with too many categories (performance)

### Drill-Down Patterns

**Pattern 1: Summary → Detail**
```
Dashboard 1: Executive Summary
  Click metric → Navigate to
Dashboard 2: Detailed Analysis
  With pre-filtered data
```

**Pattern 2: Chart → Table**
```
Same Dashboard:
  Top: Bar chart (aggregated)
  Bottom: Table (detailed rows)
  Cross-filter enabled: Click bar → Table filters
```

**Pattern 3: Dashboard Tabs**
```
Tab 1: Overview
Tab 2: By Agency
Tab 3: By Month
Tab 4: Detailed Reports
```

---

## Dashboard Templates for Finance SSC

### Template 1: BIR Compliance Dashboard

**Purpose:** Monitor filing status across multiple agencies

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ BIR Filing Compliance Dashboard - Q4 2025              │
│ Filters: [Agency ▼] [Form Type ▼] [Quarter: Q4 2025]  │ Row 1-2
├─────────────────────────────────────────────────────────┤
│ [Total]  [Completed]  [Pending]  [Overdue]             │ Row 3-6
│  245      198 (81%)    32 (13%)   15 (6%)              │
│          🟢            🟡          🔴                    │
├─────────────────────────────────────────────────────────┤
│ Compliance Trend (Line Chart - 12 months)              │ Row 7-16
│ Shows: Completion % over time + 90% target line        │
├─────────────────────────────────────────────────────────┤
│ Filings by Agency      │  Form Type Distribution       │ Row 17-26
│ (Horizontal Stacked Bar)│  (Donut Chart)                │
│ Status: Done/Pending/   │  1601-C, 2550Q, 1702-RT      │
│         Overdue         │                                │
├─────────────────────────────────────────────────────────┤
│ Upcoming Deadlines & Overdue Items (Table)              │ Row 27-40
│ Columns: Agency | Form | Due Date | Status | Assignee  │
│ Sorted: Overdue first, then by due date                │
└─────────────────────────────────────────────────────────┘
```

**Key Features:**
- Status color coding (Red/Yellow/Green)
- Trend with target benchmark line
- Drillable bar chart (click agency → filter table)
- Sortable table for actionable items

**SQL Snippets:**
```sql
-- KPI: Total Filings
SELECT COUNT(*) FROM bir_filing_tracker WHERE filing_period = '2025-Q4'

-- KPI: Completion Rate
SELECT 
  (COUNT(CASE WHEN filing_status = 'Completed' THEN 1 END)::FLOAT / 
   COUNT(*)::FLOAT * 100) as completion_percentage
FROM bir_filing_tracker WHERE filing_period = '2025-Q4'

-- Chart: Filings by Agency (Stacked)
SELECT 
  agency_name,
  filing_status,
  COUNT(*) as count
FROM bir_filing_tracker
WHERE filing_period = '2025-Q4'
GROUP BY agency_name, filing_status
ORDER BY agency_name
```

---

### Template 2: Month-End Closing Dashboard

**Purpose:** Track closing tasks progress across agencies

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ Month-End Closing Progress - October 2025              │
│ Filters: [Agency ▼] [Task Category ▼] [Assignee ▼]    │ Row 1-2
├─────────────────────────────────────────────────────────┤
│ [Overall Progress Gauge: 73%]  [Days Until Close: 5]   │ Row 3-8
│                                [Tasks Overdue: 8 🔴]    │
├─────────────────────────────────────────────────────────┤
│ Task Completion by Agency (Horizontal Bar - Stacked)    │ Row 9-20
│ Shows: % Done, In Progress, Not Started per agency     │
│ Sorted: By completion %                                 │
├─────────────────────────────────────────────────────────┤
│ Daily Completion Trend  │  Task Status Breakdown        │ Row 21-30
│ (Area Chart)            │  (Donut Chart)                │
│ Cumulative tasks done   │  Done/In Progress/            │
│                         │  Blocked/Not Started          │
├─────────────────────────────────────────────────────────┤
│ Task Details (Table - Sortable, Filterable)             │ Row 31-50
│ Columns: Task | Agency | Assignee | Due | Status |     │
│          Days Variance | Actions                        │
│ Conditional Formatting: Red (overdue), Yellow (due soon)│
└─────────────────────────────────────────────────────────┘
```

**Key Features:**
- Big progress gauge as focal point
- Agency comparison bar chart (identifies laggards)
- Cumulative completion trend (shows velocity)
- Actionable task table with status indicators

**Refresh:** Auto-refresh every 5 minutes during closing period

---

### Template 3: InsightPulse AI Monitoring

**Purpose:** Real-time document processing monitoring

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ InsightPulse AI - Document Processing Monitor           │
│ [Time Range: Last 24 Hours ▼] [Auto-refresh: ON]       │ Row 1-2
├─────────────────────────────────────────────────────────┤
│ [Docs Processed] [Avg Speed] [OCR Accuracy] [Errors]   │ Row 3-6
│   1,247 (+8%)     3.2s (-5%)   96.4%         23 (1.8%)  │
│   🟢              🟢           🟢             🟡         │
├─────────────────────────────────────────────────────────┤
│ Processing Volume Over Time (Area Chart - Hourly)       │ Row 7-18
│ Shows: Successful + Failed (stacked)                    │
├─────────────────────────────────────────────────────────┤
│ Processing Time Trend  │  Document Type Distribution    │ Row 19-28
│ (Line Chart)           │  (Bar Chart)                   │
│ Avg seconds per doc    │  Invoices, Receipts, etc.      │
├─────────────────────────────────────────────────────────┤
│ Recent Errors & Failed Processing (Table)               │ Row 29-45
│ Columns: Timestamp | Document ID | Type | Error |       │
│          Retry Status | Actions                         │
│ Auto-refresh: Every 30 seconds                          │
└─────────────────────────────────────────────────────────┘
```

**Key Features:**
- Real-time metrics with trend indicators
- Time-series area chart for volume patterns
- Error tracking table for immediate action
- Auto-refresh for operational monitoring

---

## Color Schemes & Theming

### Finance SSC Standard Palette

**Primary Colors:**
```yaml
Brand Blue:    #1890FF   # Primary actions, info
Success Green: #52C41A   # Completed, on-track
Warning Yellow:#FAAD14   # Pending, review needed
Danger Red:    #F5222D   # Overdue, errors, critical
```

**Status Indicators:**
```yaml
Completed: #52C41A (Green)
In Progress: #1890FF (Blue)
Pending: #FAAD14 (Yellow)
Overdue: #F5222D (Red)
Blocked: #FA8C16 (Orange)
Not Started: #8C8C8C (Gray)
```

**Agency Colors (Consistent across all dashboards):**
```yaml
RIM:  #1890FF (Blue)
CKVC: #52C41A (Green)
BOM:  #FA8C16 (Orange)
JPAL: #722ED1 (Purple)
JLI:  #13C2C2 (Cyan)
JAP:  #F5222D (Red)
LAS:  #FADB14 (Gold)
RMQB: #EB2F96 (Magenta)
```

### Dark Mode Considerations

If using dark theme:
```yaml
Background: #141414 (Very Dark Gray)
Text: #FFFFFF (White)
Charts: Brighter colors, higher contrast
Emphasis: Use white/light blue for highlights
```

---

## Mobile Dashboard Design

### Mobile-Specific Layouts

**Key Principles:**
1. **Vertical Stack** - All charts in single column
2. **Priority Order** - Most important at top
3. **Larger Touch Targets** - Buttons, filters 44px min
4. **Collapsible Sections** - Save vertical space

**Mobile Layout Example:**
```
┌─────────────┐
│ [Filters ▼] │  Collapsible
├─────────────┤
│ [KPI Card 1]│  Full width
│ [KPI Card 2]│  Stacked
│ [KPI Card 3]│  vertically
├─────────────┤
│ [Chart 1]   │  Full width
│ (Bar Chart) │  6-8 rows
├─────────────┤
│ [Chart 2]   │  Full width
│ (Line)      │  6-8 rows
├─────────────┤
│ [Table]     │  Horizontal
│ (Scrollable)│  scroll
└─────────────┘
```

**Mobile Optimizations:**
- Hide less critical charts
- Reduce chart complexity (fewer data points)
- Larger fonts (minimum 14px)
- Touch-friendly filter controls
- Consider separate mobile dashboard

---

## Performance Optimization

### Dashboard Load Time Goals
- **Good:** < 3 seconds
- **Acceptable:** 3-8 seconds
- **Poor:** > 8 seconds (optimize!)

### Optimization Strategies

**1. Query Optimization**
```yaml
Cache Results:
  - Enable query caching for stable data
  - Set cache timeout based on data freshness needs
  - BIR data: 1 hour cache
  - Real-time monitoring: 1 minute cache

Async Queries:
  - Enable for slow queries (> 10 seconds)
  - User sees loading spinner per chart
  - Dashboard still usable while loading
```

**2. Chart Optimization**
```yaml
Limit Data Points:
  - Line charts: Max 365 points (daily for 1 year)
  - Bar charts: Max 20-30 bars
  - Tables: Paginate at 100-500 rows

Use Appropriate Time Grain:
  - Last 7 days: Hourly
  - Last 30 days: Daily
  - Last year: Weekly or Monthly
```

**3. Dashboard Structure**
```yaml
Tabs for Related Views:
  - Split heavy dashboard into tabs
  - Load tabs on-demand (not all at once)
  
Lazy Loading:
  - Load visible charts first
  - Defer below-fold charts
```

---

## Dashboard Refresh Strategies

### Auto-Refresh Configuration

```yaml
Real-Time Monitoring (10-60 seconds):
  - Use For: Error monitoring, live operations
  - Example: InsightPulse processing errors
  - Warning: High database load

Operational Updates (5-15 minutes):
  - Use For: Task status, work-in-progress
  - Example: Month-end closing progress
  - Balance: Fresh data vs. performance

Periodic Refresh (1-24 hours):
  - Use For: Reports, historical analysis
  - Example: BIR compliance trends
  - Cache: Enable aggressive caching
```

**Manual Refresh:**
- Always provide refresh button
- Show last updated timestamp
- Clear cache on explicit refresh

---

## Accessibility Best Practices

### Color Contrast
```yaml
Minimum Contrast Ratios:
  - Normal Text: 4.5:1
  - Large Text (18px+): 3:1
  - UI Components: 3:1

Test Tools:
  - WebAIM Contrast Checker
  - Browser DevTools Accessibility
```

### Screen Reader Support
```yaml
Chart Descriptions:
  - Add meaningful alt text
  - Describe chart purpose and key findings
  
Table Headings:
  - Use proper header row markup
  - Sortable column labels
  
Filter Labels:
  - Clear, descriptive labels
  - Associated with input fields
```

### Keyboard Navigation
```yaml
Tab Order:
  - Logical flow (filters → charts → tables)
  - Skip links for long pages
  
Interactive Elements:
  - All clickable items keyboard accessible
  - Visible focus indicators
```

---

## Dashboard Checklist

Before publishing a dashboard:

**Content & Layout:**
- [ ] Clear, descriptive title
- [ ] Filters placed logically (top or left)
- [ ] Visual hierarchy guides user's eye
- [ ] Related charts grouped together
- [ ] White space for breathing room
- [ ] Consistent chart sizing

**Functionality:**
- [ ] All filters work correctly
- [ ] Cross-filtering enabled (if appropriate)
- [ ] Drill-downs configured
- [ ] Auto-refresh set (if needed)
- [ ] Cache settings optimized

**Performance:**
- [ ] Dashboard loads in < 8 seconds
- [ ] Individual charts < 5 seconds
- [ ] No unnecessary data fetching
- [ ] Query results cached

**User Experience:**
- [ ] Mobile view tested
- [ ] Color scheme is accessible
- [ ] Filters have smart defaults
- [ ] Help text / descriptions added
- [ ] Last updated timestamp visible

**Documentation:**
- [ ] Dashboard purpose documented
- [ ] Data sources identified
- [ ] Refresh schedule noted
- [ ] Owner/maintainer assigned

---

## Common Dashboard Anti-Patterns

### ❌ Don't: Chart Soup
**Problem:** Too many charts with no organization
**Solution:** Group related charts, use tabs, prioritize

### ❌ Don't: Filter Overload
**Problem:** 10+ filters, user overwhelmed
**Solution:** Collapsible filters, smart defaults, progressive disclosure

### ❌ Don't: Buried Insights
**Problem:** Key metrics at bottom or hidden
**Solution:** F-pattern layout, KPIs at top-left

### ❌ Don't: Inconsistent Design
**Problem:** Different color schemes, layouts per dashboard
**Solution:** Dashboard templates, style guide, consistent palette

### ❌ Don't: Static Data
**Problem:** No indication of data freshness
**Solution:** Show last updated time, auto-refresh for live data

### ❌ Don't: Desktop-Only
**Problem:** Unusable on mobile devices
**Solution:** Test mobile view, create mobile variant if needed

---

## Dashboard Versioning & Iteration

### Version Control Strategy

```yaml
Draft Version:
  - Visible only to creator
  - Experiment freely
  - Get feedback from stakeholders

Staging Version:
  - Share with test users
  - Validate with real data
  - Collect usability feedback

Production Version:
  - Published to all users
  - Monitor usage analytics
  - Plan improvements

Deprecated:
  - Old version archived
  - Redirect users to new version
```

### Feedback Collection

**Methods:**
1. **Usage Analytics** - Which charts get clicked most?
2. **User Surveys** - Is dashboard meeting needs?
3. **Support Tickets** - What questions arise?
4. **Direct Observation** - Watch users interact

**Iterate Based On:**
- Low engagement charts → Remove or improve
- Frequently filtered dimensions → Add as default
- Common drill-down paths → Pre-build views
- Performance issues → Optimize or split

---

## Integration with Your Stack

### Odoo + Supabase Context

**Data Refresh Patterns:**
```sql
-- Odoo data synced to Supabase every 15 minutes
-- Dashboard queries Supabase PostgreSQL
-- Cache dashboard results for 5-15 minutes
-- Result: Fresh data with good performance
```

**User Permissions:**
```yaml
Finance SSC Admins:
  - Can edit all dashboards
  - Access all agency data

Agency Leads:
  - View own agency data only
  - Cannot edit dashboards

Executives:
  - View all data (read-only)
  - Access executive dashboards only
```

### MCP Integration

**Using Superset MCP Server:**
```python
# Fetch dashboard via MCP
mcp.call_tool("get_superset_dashboard", {
  "dashboard_id": 123
})

# Update chart via MCP
mcp.call_tool("update_superset_chart", {
  "chart_id": 456,
  "config": {...}
})
```

---

## Quick Wins for Better Dashboards

1. **Add KPIs at top** - Big numbers, immediately visible
2. **Use consistent colors** - Status colors across all dashboards
3. **Enable cross-filtering** - Make dashboards interactive
4. **Set smart filter defaults** - Current month, active status
5. **Show last updated time** - Build trust in data
6. **Add descriptions** - Help users understand purpose
7. **Test on mobile** - Ensure usability on all devices
8. **Get user feedback** - Iterate based on actual usage
9. **Monitor performance** - Optimize slow charts
10. **Version control** - Keep drafts separate from production

---

## Next Steps

After designing your dashboard:
1. **Build charts first** - Use `superset-chart-builder` skill
2. **Test with real data** - Validate queries and performance
3. **Get stakeholder review** - Ensure it meets needs
4. **Publish to production** - With proper permissions
5. **Monitor usage** - Iterate based on feedback

**Related Skills:**
- `superset-chart-builder` - Build individual charts
- `superset-sql-developer` - Optimize data queries
- `pmbok-project-management` - Dashboard project planning

---

## Support

For Superset dashboard features:
```bash
# View dashboard list
http://your-superset-url/dashboard/list/

# Dashboard URL pattern
http://your-superset-url/superset/dashboard/{id}/
```

**Your Context:**
- Multiple Finance SSC agencies (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
- BIR compliance tracking requirements
- Month-end closing multi-agency coordination
- InsightPulse AI operational monitoring
- Odoo 18/19 + Supabase data stack
