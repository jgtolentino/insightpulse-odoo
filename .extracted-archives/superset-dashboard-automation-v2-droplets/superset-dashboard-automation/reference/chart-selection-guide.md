# Chart Selection Guide

Framework for choosing the right visualization type in Apache Superset.

## Decision Tree

```
Is it a single number? → Big Number Total / KPI
Is it time-based data? → Timeseries / Line Chart
Is it comparing categories? → Bar Chart
Is it showing proportions? → Pie Chart
Is it detailed data? → Table / Pivot Table
Is it showing distribution? → Histogram
Is it showing relationships? → Scatter Plot
Is it geographic? → Map / GeoJSON
```

## Chart Type Catalog

### 1. Big Number Total
**Best for**: KPIs, metrics, totals

**Use cases**:
- Total revenue
- Open invoices count
- Overdue filings
- Cash balance
- Active users

**Example**:
```json
{
  "viz_type": "big_number_total",
  "metric": "SUM(amount)",
  "y_axis_format": "₱,.2f",
  "header_font_size": 0.4,
  "subheader": "vs last month",
  "comparison_type": "value"
}
```

**When to avoid**: When context is needed (use timeseries instead).

---

### 2. ECharts Timeseries
**Best for**: Trends over time, time-based comparisons

**Use cases**:
- Revenue trend
- Expense tracking
- Tax filing history
- User growth
- Performance metrics

**Example**:
```json
{
  "viz_type": "echarts_timeseries_line",
  "x_axis": "date",
  "metrics": ["SUM(revenue)", "SUM(expenses)"],
  "time_grain_sqla": "P1M",
  "rich_tooltip": true,
  "show_legend": true
}
```

**Variants**:
- `echarts_timeseries_bar`: For discrete periods
- `echarts_timeseries_smooth`: For smoothed trends
- `echarts_timeseries_step`: For step changes

**When to avoid**: Data is not time-based.

---

### 3. ECharts Bar Chart
**Best for**: Comparing categories, rankings

**Use cases**:
- Revenue by product
- Expenses by department
- Top vendors
- Agency performance
- Regional sales

**Example**:
```json
{
  "viz_type": "echarts_bar",
  "x_axis": "department",
  "metrics": ["SUM(expenses)"],
  "y_axis_format": "₱,.0f",
  "sort_series_type": "DESC",
  "show_legend": false
}
```

**Orientation**:
- Vertical: 2-8 categories
- Horizontal: 8+ categories or long labels

**When to avoid**: More than 20 categories (use table).

---

### 4. ECharts Pie Chart
**Best for**: Part-to-whole relationships, proportions

**Use cases**:
- Budget allocation
- Expense breakdown
- Market share
- Filing status distribution

**Example**:
```json
{
  "viz_type": "echarts_pie",
  "groupby": ["category"],
  "metric": "SUM(amount)",
  "show_legend": true,
  "show_labels": true,
  "label_type": "key_percent"
}
```

**Best practices**:
- Limit to 5-7 slices
- Combine small slices into "Other"
- Start largest slice at 12 o'clock
- Use consistent colors

**When to avoid**: More than 7 categories, exact values needed.

---

### 5. Pivot Table v2
**Best for**: Detailed analysis, cross-tabulation

**Use cases**:
- Multi-dimensional analysis
- Agency x Form x Period breakdown
- Vendor x Category spending
- Budget vs actual by department

**Example**:
```json
{
  "viz_type": "pivot_table_v2",
  "groupby": ["agency", "form_type"],
  "columns": ["period"],
  "metrics": ["SUM(amount)"],
  "row_limit": 5000,
  "conditional_formatting": [
    {
      "column": "amount",
      "operator": ">",
      "value": 100000,
      "colorScheme": "#ff0000"
    }
  ]
}
```

**Best practices**:
- Limit dimensions to 3 (rows, columns, metrics)
- Use conditional formatting
- Enable sorting
- Set reasonable row limits

**When to avoid**: Simple comparisons (use bar chart).

---

### 6. Table
**Best for**: Raw data display, detailed lists

**Use cases**:
- Transaction lists
- Invoice details
- Filing schedule
- Vendor directory
- User roster

**Example**:
```json
{
  "viz_type": "table",
  "groupby": ["invoice_number", "vendor", "amount", "due_date"],
  "order_by_cols": [["due_date", true]],
  "row_limit": 100,
  "page_length": 25
}
```

**Best practices**:
- Enable pagination
- Add sorting
- Use conditional formatting
- Limit columns to 8-10

**When to avoid**: Aggregated data (use pivot table).

---

### 7. ECharts Scatter Plot
**Best for**: Relationships, correlations, outliers

**Use cases**:
- Cost vs time analysis
- Budget vs actual
- Revenue vs marketing spend
- Performance metrics

**Example**:
```json
{
  "viz_type": "echarts_scatter",
  "x": "budget",
  "y": "actual_spend",
  "size": "variance",
  "entity": "department"
}
```

**When to avoid**: No clear relationship expected.

---

### 8. Gauge Chart
**Best for**: Progress, capacity, utilization

**Use cases**:
- Month-end closing progress
- Budget utilization
- Capacity used
- Goal achievement

**Example**:
```json
{
  "viz_type": "echarts_gauge",
  "metric": "AVG(completion_pct)",
  "min_val": 0,
  "max_val": 100,
  "intervals": [
    {"color": "#ff0000", "value": 50},
    {"color": "#ffaa00", "value": 80},
    {"color": "#00ff00", "value": 100}
  ]
}
```

**When to avoid**: Multiple metrics (use multiple gauges or bar chart).

---

### 9. Deck.gl GeoJSON
**Best for**: Geographic data, maps

**Use cases**:
- Regional sales
- Office locations
- Delivery zones
- Customer distribution

**Example**:
```json
{
  "viz_type": "deck_geojson",
  "geojson_column": "location",
  "metric": "SUM(sales)",
  "fill_color_picker": {
    "r": 0,
    "g": 122,
    "b": 135,
    "a": 0.8
  }
}
```

**When to avoid**: Data is not geographic.

---

## Color Scheme Guidelines

### For Status
- 🟢 Green: Good, on-time, success
- 🟡 Yellow: Warning, pending, attention
- 🔴 Red: Critical, overdue, failure
- 🔵 Blue: Neutral, informational

### For Finance
- 💚 Green: Revenue, income, assets
- 🔴 Red: Expenses, liabilities, losses
- 🔵 Blue: Budget, forecast

### For Multi-Agency
Use consistent colors across all dashboards:
- RIM: #E74C3C (Red)
- CKVC: #3498DB (Blue)
- BOM: #2ECC71 (Green)
- JPAL: #F39C12 (Orange)
- JLI: #9B59B6 (Purple)
- JAP: #1ABC9C (Teal)
- LAS: #E67E22 (Dark Orange)
- RMQB: #34495E (Dark Blue)

## Performance Considerations

### Fast Charts (< 1 second)
- Big Number Total
- Simple Bar Chart (< 20 bars)
- Simple Line Chart (< 1000 points)

### Medium Charts (1-3 seconds)
- Pivot Table (< 5000 rows)
- Detailed Table (< 1000 rows)
- Complex Timeseries (multiple metrics)

### Slow Charts (> 3 seconds)
- Large Pivot Table (> 5000 rows)
- Scatter Plot (> 10000 points)
- GeoJSON with many features

**Optimization tips**:
1. Use materialized views for complex queries
2. Add indexes on filter columns
3. Set appropriate cache timeouts
4. Limit date ranges with filters

## Accessibility Guidelines

### Colors
- Use colorblind-friendly palettes
- Don't rely on color alone (use labels)
- Ensure sufficient contrast

### Labels
- Keep axis labels short and clear
- Show units (₱, %, units)
- Use consistent formatting

### Tooltips
- Enable rich tooltips
- Show all relevant context
- Format numbers appropriately

## Mobile Considerations

### Best for Mobile
- Big Number Total
- Simple Bar Chart (< 5 bars)
- Pie Chart
- Gauge

### Avoid on Mobile
- Large tables
- Complex pivot tables
- Scatter plots with many points
- Maps with fine detail

## Common Mistakes

### ❌ Wrong Chart Type
**Problem**: Using pie chart for 15 categories  
**Fix**: Use horizontal bar chart

### ❌ Too Much Data
**Problem**: Table with 10,000 rows, no pagination  
**Fix**: Add filters, enable pagination, use aggregation

### ❌ Poor Colors
**Problem**: Red/green for non-status data  
**Fix**: Use neutral colors, reserve red/green for status

### ❌ Missing Context
**Problem**: Big number without comparison  
**Fix**: Add comparison to previous period or target

### ❌ Cluttered Layout
**Problem**: Too many metrics in one chart  
**Fix**: Split into multiple focused charts

## Quick Reference

| Data Type | Best Chart | Alternative |
|-----------|-----------|-------------|
| Single metric | Big Number | Gauge |
| Time trend | Timeseries | Bar Chart |
| Category comparison | Bar Chart | Pie Chart |
| Part-to-whole | Pie Chart | Stacked Bar |
| Detailed data | Table | Pivot Table |
| Cross-tab | Pivot Table | Grouped Bar |
| Distribution | Histogram | Box Plot |
| Correlation | Scatter | Heatmap |
| Geographic | Map | Table with regions |
| Progress | Gauge | Big Number |

## Testing Your Chart

Before finalizing:
1. ✅ Does it answer the question clearly?
2. ✅ Can users understand it without explanation?
3. ✅ Is it readable on mobile?
4. ✅ Does it load in < 3 seconds?
5. ✅ Are colors accessible?
6. ✅ Are labels clear?
7. ✅ Does it fit the dashboard layout?

---

**The right chart makes the data story clear!** 📊
