# Chart Type Decision Tree

## Quick Decision Flow

```
START: What do you want to show?

├─ Single Key Number
│  ├─ Just the value → Big Number
│  ├─ Value + trend → Big Number with Trendline
│  └─ Progress to goal → Gauge Chart

├─ Compare Categories
│  ├─ 2-7 categories → Bar Chart (Vertical or Horizontal)
│  ├─ 8-15 categories → Horizontal Bar Chart
│  ├─ 15+ categories → Table
│  └─ Need parts of whole → Stacked Bar or Donut

├─ Show Trends Over Time
│  ├─ Single metric → Line Chart
│  ├─ 2-3 metrics → Multi-Line Chart
│  ├─ Emphasize volume → Area Chart
│  ├─ Multiple periods → Grouped Bar Chart
│  └─ Cumulative → Stacked Area Chart

├─ Composition/Parts of Whole
│  ├─ 2-5 parts → Pie or Donut Chart
│  ├─ 6+ parts → Bar Chart (easier to read)
│  ├─ Hierarchical → Treemap or Sunburst
│  └─ Over time → Stacked Area or 100% Stacked Bar

├─ Detailed Data Exploration
│  ├─ List view → Table
│  ├─ Cross-tabulation → Pivot Table
│  └─ Pattern discovery → Heatmap

├─ Relationships
│  ├─ Two variables → Scatter Plot
│  ├─ Distribution → Histogram or Box Plot
│  └─ Flow/Network → Sankey Diagram

└─ Geographic Data
   ├─ Points → Deck.gl Scatterplot
   └─ Regions → Country Map or Deck.gl Polygon
```

## Finance SSC Use Cases

### BIR Compliance
| Question | Chart Type | Why |
|----------|-----------|-----|
| How many filings are overdue? | Big Number (Red) | Immediate KPI |
| Which agencies are behind? | Horizontal Bar | Easy comparison of many agencies |
| What's our compliance trend? | Line Chart | Time series pattern |
| What form types do we file most? | Donut Chart | Composition (4-5 types) |
| When do ATPs expire? | Table with formatting | Detailed dates + sorting |

### Month-End Closing
| Question | Chart Type | Why |
|----------|-----------|-----|
| What's our completion rate? | Gauge | Progress toward 100% |
| How many tasks remain? | Big Number | Quick count |
| Which tasks are blocking? | Table (filtered) | Need details + status |
| Progress by agency? | Horizontal Bar (Stacked) | Compare + composition |
| How long do tasks take? | Line Chart (avg time) | Trend over time |

### InsightPulse AI
| Question | Chart Type | Why |
|----------|-----------|-----|
| Documents processed today? | Big Number with Trend | Volume + comparison |
| Processing speed over time? | Line Chart | Performance trend |
| Error rate by document type? | Bar Chart | Category comparison |
| OCR confidence distribution? | Histogram | Value distribution |
| Processing status breakdown? | Donut Chart | Composition (4-5 states) |

## Anti-Patterns to Avoid

### ❌ Don't Use Pie Chart When:
- More than 5 categories
- Values are similar (hard to see differences)
- Comparing multiple pies side-by-side
- **Use Bar Chart instead**

### ❌ Don't Use Line Chart When:
- Comparing discrete categories (not time)
- Data is not sequential
- **Use Bar Chart instead**

### ❌ Don't Use Table When:
- Showing simple totals (use Big Number)
- Visualizing trends (use Line/Bar)
- **Use visualization instead of raw data**

### ❌ Don't Use 3D Charts
- Never. They're harder to read and less accurate.
- **Stick to 2D charts**

### ❌ Don't Use Too Many Colors
- Limit to 5-7 distinct colors
- Use shades of one color for related data
- **Use color meaningfully (status, categories)**

## Color-Blind Friendly Palettes

### Sequential (Low to High)
```
Light → Dark Blue: #E3F2FD → #1565C0
Light → Dark Green: #E8F5E9 → #2E7D32
Light → Dark Orange: #FFF3E0 → #E65100
```

### Categorical (Distinct Groups)
```
Safe 5-color: #1f77b4, #ff7f0e, #2ca02c, #d62728, #9467bd
Safe 8-color: Add #8c564b, #e377c2, #7f7f7f
```

### Diverging (Negative ↔ Positive)
```
Red → Gray → Green: #d32f2f → #9e9e9e → #388e3c
```

### Status (Universal)
```
Good:     #52C41A (Green)
Warning:  #FAAD14 (Yellow)
Critical: #F5222D (Red)
Info:     #1890FF (Blue)
```

## Performance Considerations

### Data Volume Guidelines
| Chart Type | Recommended Max Rows | Notes |
|-----------|---------------------|-------|
| Big Number | 1 (aggregated) | Single value |
| Bar Chart | 20 bars | 50+ becomes unreadable |
| Line Chart | 1000 points | Can handle more with proper time grain |
| Table | 100-500 | Use pagination for more |
| Pivot Table | 10,000 cells | Depends on dimensions |
| Heatmap | 1000 cells | Performance drops quickly |
| Scatter Plot | 10,000 points | Use sampling for more |

### Optimization Strategies
1. **Aggregate at database level** - Don't fetch raw rows
2. **Use appropriate time grain** - Day/Week/Month based on range
3. **Limit rows** - Set reasonable defaults
4. **Cache queries** - Enable for frequently accessed charts
5. **Async loading** - For slow queries (30+ seconds)

## Mobile Responsiveness

### Chart Behavior on Mobile
| Chart Type | Mobile Friendly? | Adjustments Needed |
|-----------|-----------------|-------------------|
| Big Number | ✅ Excellent | None |
| Bar Chart (Vertical) | ✅ Good | Reduce categories |
| Bar Chart (Horizontal) | ⚠️ Fair | Scrollable |
| Line Chart | ✅ Good | Reduce lines (max 3) |
| Table | ⚠️ Fair | Enable horizontal scroll |
| Donut/Pie | ✅ Good | Increase label font |
| Gauge | ✅ Good | None |

### Mobile Dashboard Tips
- **Prioritize KPIs** - Big numbers at top
- **Limit charts** - 3-5 per mobile dashboard
- **Stack vertically** - Don't rely on side-by-side
- **Larger touch targets** - Filters and buttons
- **Test on actual devices** - Not just browser resize

## Quick Wins for Better Charts

1. **Always start Y-axis at zero** for bar/area charts (unless percentage)
2. **Use horizontal bars** when labels are long
3. **Sort bars** meaningfully (by value, alphabetically)
4. **Add reference lines** for targets/benchmarks
5. **Enable drill-down** for aggregated data
6. **Show data labels** for small datasets (<10 points)
7. **Use consistent colors** across related charts
8. **Add descriptions** to explain what you're showing
9. **Test with real data** before publishing
10. **Get feedback** from actual users

## Chart Combinations for Common Scenarios

### Executive Dashboard
```
Row 1: Big Numbers (KPIs)
  - Total Revenue | Completion % | Overdue Count

Row 2: Trend + Comparison  
  - Revenue Trend (Line) | Revenue by Division (Bar)

Row 3: Detailed Breakdown
  - Top Customers (Table) | Product Mix (Donut)
```

### Operational Monitoring
```
Row 1: Status Overview
  - Success Rate (Gauge) | Error Count (Big Number - Red)

Row 2: Time Series
  - Volume Over Time (Area) | Response Time (Line)

Row 3: Drill-Down
  - Error Log (Table) | Status Breakdown (Donut)
```

### Compliance Tracking
```
Row 1: Headlines
  - Compliant Count (Green) | Non-Compliant (Red) | Due Soon (Yellow)

Row 2: Trends
  - Compliance Rate Trend (Line + Target Reference)

Row 3: Details
  - Compliance by Unit (Bar - Stacked) | Upcoming Deadlines (Table)
```

## Testing Checklist

Before publishing a chart:

**Data Accuracy:**
- [ ] Query returns expected results
- [ ] Aggregations are correct
- [ ] Filters work as intended
- [ ] Date ranges are accurate

**Visual Quality:**
- [ ] Labels are readable
- [ ] Colors make sense
- [ ] Chart type fits the data
- [ ] No visual clutter

**Performance:**
- [ ] Loads in < 10 seconds
- [ ] Caching is enabled
- [ ] No unnecessary data fetched

**Usability:**
- [ ] Tooltips provide context
- [ ] Drill-downs work (if enabled)
- [ ] Export functions properly
- [ ] Mobile view is acceptable

**Documentation:**
- [ ] Chart has clear title
- [ ] Description explains purpose
- [ ] Data source is identified
- [ ] Last update time shown
