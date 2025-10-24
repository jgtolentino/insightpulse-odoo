# Earned Value Management Formulas

## Core EVM Metrics

### Basic Calculations
- **Planned Value (PV)**: Budgeted cost of work scheduled
- **Earned Value (EV)**: Budgeted cost of work performed  
- **Actual Cost (AC)**: Actual cost of work performed
- **Budget at Completion (BAC)**: Total planned budget

### Variance Analysis
- **Schedule Variance (SV)**: EV - PV
  - SV > 0: Ahead of schedule
  - SV = 0: On schedule
  - SV < 0: Behind schedule

- **Cost Variance (CV)**: EV - AC
  - CV > 0: Under budget
  - CV = 0: On budget
  - CV < 0: Over budget

### Performance Indices
- **Schedule Performance Index (SPI)**: EV / PV
  - SPI > 1.0: Ahead of schedule
  - SPI = 1.0: On schedule
  - SPI < 1.0: Behind schedule

- **Cost Performance Index (CPI)**: EV / AC
  - CPI > 1.0: Under budget
  - CPI = 1.0: On budget
  - CPI < 1.0: Over budget

## Forecasting Formulas

### Estimate at Completion (EAC) Options

#### 1. Typical Method (CPI-based)
- **Formula**: EAC = BAC / CPI
- **When to use**: Current cost performance expected to continue
- **Assumption**: Future work at same efficiency as past

#### 2. Atypical Method (AC + Remaining)
- **Formula**: EAC = AC + (BAC - EV)
- **When to use**: Original estimate was flawed, but remaining work accurate
- **Assumption**: Past performance not indicative of future

#### 3. CPI/SPI Combined
- **Formula**: EAC = AC + [(BAC - EV) / (CPI × SPI)]
- **When to use**: Both cost and schedule performance considered
- **Assumption**: Both cost and schedule efficiency continue

#### 4. Revised Estimate
- **Formula**: EAC = AC + New ETC
- **When to use**: Bottom-up re-estimation of remaining work
- **Assumption**: New estimate more accurate than original

### Additional Forecasts
- **Estimate to Complete (ETC)**: EAC - AC
- **Variance at Completion (VAC)**: BAC - EAC
- **To Complete Performance Index (TCPI)**:
  - **Based on BAC**: TCPI = (BAC - EV) / (BAC - AC)
  - **Based on EAC**: TCPI = (BAC - EV) / (EAC - AC)

## Thresholds and Triggers

### Performance Thresholds
- **Green Zone**: CPI ≥ 0.95 and SPI ≥ 0.95
- **Yellow Zone**: 0.90 ≤ CPI < 0.95 or 0.90 ≤ SPI < 0.95
- **Red Zone**: CPI < 0.90 or SPI < 0.90

### Variance Thresholds
- **Minor Variance**: |CV| ≤ 5% of BAC and |SV| ≤ 5% of BAC
- **Significant Variance**: 5% < |CV| ≤ 10% of BAC or 5% < |SV| ≤ 10% of BAC
- **Major Variance**: |CV| > 10% of BAC or |SV| > 10% of BAC

## Calculation Examples

### Example 1: Basic EVM Calculation
```
Project: Website Development
BAC: $100,000
Current Status: 50% complete
PV: $60,000 (60% of budget should be spent)
EV: $50,000 (50% of work completed)
AC: $55,000 (actual spending)

Calculations:
SV = EV - PV = $50,000 - $60,000 = -$10,000 (behind schedule)
CV = EV - AC = $50,000 - $55,000 = -$5,000 (over budget)
SPI = EV / PV = 50,000 / 60,000 = 0.83 (behind schedule)
CPI = EV / AC = 50,000 / 55,000 = 0.91 (over budget)
```

### Example 2: EAC Forecasting
```
Using same project data:
EAC (CPI-based) = BAC / CPI = 100,000 / 0.91 = $109,890
EAC (Atypical) = AC + (BAC - EV) = 55,000 + (100,000 - 50,000) = $105,000
EAC (CPI/SPI) = AC + [(BAC - EV) / (CPI × SPI)] = 55,000 + [(100,000 - 50,000) / (0.91 × 0.83)] = $121,000

ETC = EAC - AC = 109,890 - 55,000 = $54,890
VAC = BAC - EAC = 100,000 - 109,890 = -$9,890
TCPI = (BAC - EV) / (BAC - AC) = (100,000 - 50,000) / (100,000 - 55,000) = 1.11
```

## Interpretation Guidelines

### Schedule Performance (SPI)
- **SPI > 1.10**: Significantly ahead of schedule
- **SPI 1.00-1.10**: Slightly ahead of schedule
- **SPI 0.90-1.00**: On or slightly behind schedule
- **SPI < 0.90**: Significantly behind schedule

### Cost Performance (CPI)
- **CPI > 1.10**: Significantly under budget
- **CPI 1.00-1.10**: Slightly under budget
- **CPI 0.90-1.00**: On or slightly over budget
- **CPI < 0.90**: Significantly over budget

### Corrective Actions

#### For Schedule Issues (SPI < 0.95)
- **Resource Reallocation**: Shift resources to critical path
- **Schedule Compression**: Fast tracking or crashing
- **Scope Review**: Evaluate scope for potential reduction
- **Process Improvement**: Identify and address bottlenecks

#### For Cost Issues (CPI < 0.95)
- **Cost Control**: Implement stricter spending controls
- **Value Engineering**: Find cost-effective alternatives
- **Resource Optimization**: Improve resource utilization
- **Vendor Negotiation**: Renegotiate contracts and terms

## Integration with Odoo

### Custom Field Mapping
```python
# Example Odoo custom fields for EVM
'planned_value': fields.Float('Planned Value (PV)'),
'earned_value': fields.Float('Earned Value (EV)'),
'actual_cost': fields.Float('Actual Cost (AC)'),
'schedule_variance': fields.Float('Schedule Variance', compute='_compute_evm'),
'cost_variance': fields.Float('Cost Variance', compute='_compute_evm'),
'schedule_performance_index': fields.Float('SPI', compute='_compute_evm'),
'cost_performance_index': fields.Float('CPI', compute='_compute_evm'),
'estimate_at_completion': fields.Float('EAC', compute='_compute_evm'),
```

### Automated Calculations
```python
def _compute_evm(self):
    for record in self:
        # Calculate variances
        record.schedule_variance = record.earned_value - record.planned_value
        record.cost_variance = record.earned_value - record.actual_cost
        
        # Calculate performance indices
        if record.planned_value != 0:
            record.schedule_performance_index = record.earned_value / record.planned_value
        else:
            record.schedule_performance_index = 0
            
        if record.actual_cost != 0:
            record.cost_performance_index = record.earned_value / record.actual_cost
        else:
            record.cost_performance_index = 0
            
        # Calculate EAC (CPI-based)
        if record.cost_performance_index != 0:
            record.estimate_at_completion = record.budget_at_completion / record.cost_performance_index
        else:
            record.estimate_at_completion = 0
```

## Reporting Templates

### Weekly EVM Status Report
```
Project: [Project Name]
Reporting Period: [Start Date] to [End Date]

EVM Metrics:
- Planned Value (PV): $[Amount]
- Earned Value (EV): $[Amount] 
- Actual Cost (AC): $[Amount]
- Schedule Variance (SV): $[Amount] ([Percentage]%)
- Cost Variance (CV): $[Amount] ([Percentage]%)
- SPI: [Value] ([Status])
- CPI: [Value] ([Status])
- EAC: $[Amount] (VAC: $[Amount])

Performance Analysis:
[Detailed analysis of performance trends]

Corrective Actions:
[List of actions being taken]

Next Steps:
[Planned activities for next period]
```

### Threshold Alerts
```python
# Example alert conditions
def check_evm_thresholds(self):
    alerts = []
    
    if self.schedule_performance_index < 0.90:
        alerts.append(f"Schedule performance critical: SPI = {self.schedule_performance_index}")
        
    if self.cost_performance_index < 0.90:
        alerts.append(f"Cost performance critical: CPI = {self.cost_performance_index}")
        
    if abs(self.schedule_variance) > 0.10 * self.budget_at_completion:
        alerts.append(f"Significant schedule variance: ${self.schedule_variance}")
        
    if abs(self.cost_variance) > 0.10 * self.budget_at_completion:
        alerts.append(f"Significant cost variance: ${self.cost_variance}")
        
    return alerts
```

## Best Practices

### Data Collection
- **Consistent Measurement**: Use same method throughout project
- **Regular Updates**: Update EVM metrics weekly
- **Accurate Progress**: Use objective completion criteria
- **Documentation**: Maintain audit trail for all calculations

### Analysis Frequency
- **Weekly**: Basic EVM calculations and variance analysis
- **Monthly**: Detailed forecasting and trend analysis
- **Quarterly**: Comprehensive performance review
- **Milestone**: Major reassessment at key milestones

### Communication
- **Stakeholder Reports**: Tailor detail level to audience
- **Visual Dashboards**: Use charts and graphs for clarity
- **Actionable Insights**: Focus on decisions and actions
- **Transparency**: Share both good and bad news promptly
