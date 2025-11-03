# PMP Formulas Quick Reference

## Earned Value Management (EVM) Formulas

### Basic Metrics
```
PV (Planned Value) = % of planned work × BAC
EV (Earned Value) = % of actual work completed × BAC
AC (Actual Cost) = Actual costs incurred
BAC (Budget at Completion) = Total project budget
```

### Variance Analysis
```
CV (Cost Variance) = EV - AC
    Negative = Over budget
    Positive = Under budget
    Zero = On budget

SV (Schedule Variance) = EV - PV
    Negative = Behind schedule
    Positive = Ahead of schedule
    Zero = On schedule
```

### Performance Indexes
```
CPI (Cost Performance Index) = EV / AC
    < 1.0 = Over budget
    = 1.0 = On budget
    > 1.0 = Under budget

SPI (Schedule Performance Index) = EV / PV
    < 1.0 = Behind schedule
    = 1.0 = On schedule
    > 1.0 = Ahead of schedule
```

### Forecasting Formulas

**EAC (Estimate at Completion)**
```
Typical scenario (current performance continues):
EAC = BAC / CPI

Atypical scenario (one-time variance):
EAC = AC + (BAC - EV)

Budget rate not achievable:
EAC = AC + [(BAC - EV) / (CPI × SPI)]
```

**ETC (Estimate to Complete)**
```
ETC = EAC - AC
```

**VAC (Variance at Completion)**
```
VAC = BAC - EAC
    Positive = Under budget at completion
    Negative = Over budget at completion
```

**TCPI (To-Complete Performance Index)**
```
Based on BAC:
TCPI = (BAC - EV) / (BAC - AC)

Based on EAC:
TCPI = (BAC - EV) / (EAC - AC)

Interpretation:
< 1.0 = Easier to complete within budget
= 1.0 = Must maintain current performance
> 1.0 = Harder to complete within budget
```

## Schedule Formulas

### Critical Path Method (CPM)

**Forward Pass (Early dates)**
```
ES (Early Start) = Latest EF of predecessors
EF (Early Finish) = ES + Duration
```

**Backward Pass (Late dates)**
```
LF (Late Finish) = Earliest LS of successors
LS (Late Start) = LF - Duration
```

**Float/Slack**
```
Total Float = LS - ES
OR
Total Float = LF - EF

Free Float = ES (successor) - EF (current)
```

### PERT (Three-Point Estimates)
```
Optimistic (O): Best case scenario
Most Likely (M): Most probable duration
Pessimistic (P): Worst case scenario

Expected Duration (Mean):
Te = (O + 4M + P) / 6

Standard Deviation:
σ = (P - O) / 6

Variance:
σ² = [(P - O) / 6]²

For project (multiple activities):
Project σ = √(sum of variances)
```

## Communications Channels
```
Number of Communication Channels = n(n-1) / 2

Where n = number of people

Examples:
3 people: 3(2)/2 = 3 channels
5 people: 5(4)/2 = 10 channels
10 people: 10(9)/2 = 45 channels
```

## Cost Formulas

### Point of Total Assumption (PTA)
For Fixed Price Incentive Fee (FPIF) contracts:
```
PTA = ((Ceiling Price - Target Price) / Buyer's Share) + Target Cost
```

### Cost Plus Formulas
```
Cost Plus Fixed Fee (CPFF):
Total Cost = Actual Cost + Fixed Fee

Cost Plus Incentive Fee (CPIF):
Total Cost = Actual Cost + Fee (based on performance)

Cost Plus Award Fee (CPAF):
Total Cost = Actual Cost + Award Fee (subjective)
```

## Quality Formulas

### Expected Monetary Value (EMV)
```
EMV = Probability × Impact

For opportunities (positive):
EMV = P × Gain

For threats (negative):
EMV = P × Loss

Decision: Choose option with highest EMV
```

## Risk Formulas

### Risk Priority Number
```
RPN = Probability × Impact × Detection Difficulty

Where:
Probability: 1-10 (1=unlikely, 10=certain)
Impact: 1-10 (1=negligible, 10=catastrophic)
Detection: 1-10 (1=easy to detect, 10=hard to detect)
```

### Risk Score
```
Risk Score = Probability × Impact

Example:
High probability (0.7) × High impact (8) = 5.6
```

## Practical Examples

### Example 1: EVM Calculation
```
Given:
BAC = $500,000
PV = $250,000 (50% planned)
EV = $200,000 (40% complete)
AC = $220,000 (actual spent)

Calculate:
CV = EV - AC = $200,000 - $220,000 = -$20,000 (over budget)
SV = EV - PV = $200,000 - $250,000 = -$50,000 (behind schedule)

CPI = EV / AC = $200,000 / $220,000 = 0.91 (spending $1.10 for every $1 of work)
SPI = EV / PV = $200,000 / $250,000 = 0.80 (completing 80% of planned work)

EAC = BAC / CPI = $500,000 / 0.91 = $549,451 (forecast total cost)
ETC = EAC - AC = $549,451 - $220,000 = $329,451 (remaining cost)
VAC = BAC - EAC = $500,000 - $549,451 = -$49,451 (over budget at completion)

TCPI = (BAC - EV) / (BAC - AC) = ($500,000 - $200,000) / ($500,000 - $220,000) = 1.07
(Need 7% better performance to meet budget)
```

### Example 2: PERT Estimation
```
Given:
Optimistic = 10 days
Most Likely = 15 days
Pessimistic = 26 days

Calculate:
Expected Duration = (10 + 4(15) + 26) / 6 = 96 / 6 = 16 days

Standard Deviation = (26 - 10) / 6 = 16 / 6 = 2.67 days

Interpretation:
- 68% confident: 16 ± 2.67 days (13.33 to 18.67 days)
- 95% confident: 16 ± 5.34 days (10.66 to 21.34 days)
- 99.7% confident: 16 ± 8.01 days (7.99 to 24.01 days)
```

### Example 3: Communication Channels
```
Finance SSC Team:
8 people: 8(7)/2 = 28 communication channels

Adding 1 manager:
9 people: 9(8)/2 = 36 communication channels
(+8 new channels from adding 1 person!)
```

### Example 4: Critical Path
```
Activity Network:
A (5 days) → B (3 days) → D (4 days) → F (2 days) = 14 days
A (5 days) → C (6 days) → E (3 days) → F (2 days) = 16 days ← Critical Path
                                                      (longest path)

Total Float for B-D path:
Float = 16 - 14 = 2 days (can delay B or D by 2 days without affecting project)
```

## Quick Reference Table

| Metric | Formula | Good Performance |
|--------|---------|------------------|
| CV | EV - AC | Positive (under budget) |
| SV | EV - PV | Positive (ahead of schedule) |
| CPI | EV / AC | > 1.0 (efficient) |
| SPI | EV / PV | > 1.0 (fast) |
| TCPI | (BAC-EV)/(BAC-AC) | < 1.0 (achievable) |

## Exam Tips

1. **Memorize these formulas** - they will be on the exam
2. **Practice calculations** - know how to apply formulas
3. **Understand interpretations** - what does CPI=0.85 mean?
4. **Remember units** - keep $ with $, days with days
5. **Check reasonableness** - does the answer make sense?
6. **Know when to use which EAC formula** - typical vs atypical
7. **Be fast with calculator** - practice mental math
8. **Draw network diagrams** - visualize for CPM problems

## Common Mistakes to Avoid

1. Confusing CV and SV (which is cost, which is schedule?)
2. Dividing backwards in CPI/SPI formulas
3. Using wrong EAC formula for the scenario
4. Forgetting to subtract in TCPI formula
5. Mixing up ES/EF and LS/LF in CPM
6. Calculating standard deviation wrong in PERT
7. Forgetting to square when calculating variance
8. Using wrong share ratio in PTA formula

## Practice Problems

Try these to test your knowledge:

**Problem 1**: BAC=$100K, PV=$50K, EV=$40K, AC=$45K. Calculate CV, SV, CPI, SPI, EAC, VAC.

**Problem 2**: Activity durations: O=3, M=5, P=9. Calculate expected duration and standard deviation.

**Problem 3**: Project has 12 team members. How many communication channels?

**Problem 4**: Activity A: ES=0, Duration=5. Activity B follows A with Duration=3. Calculate all dates.
