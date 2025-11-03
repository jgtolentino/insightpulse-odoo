# Example: BIR Tax Compliance Workflow

## Use Case
Create a cross-functional flowchart for BIR Form 1601-C monthly withholding tax filing process for a Finance Shared Service Center.

## Request to Claude

```
Create a cross-functional flowchart (swimlane diagram) for BIR Form 1601-C monthly withholding tax filing with these departments:

**Swimlanes (Departments):**
1. Accounting Team (RIM, CKVC, BOM) - Data preparation
2. Senior Accountants (JPAL, JLI) - Review and validation
3. Finance Managers (JAP, LAS) - Approval
4. Director (RMQB) - Final sign-off

**Process Flow:**
1. Start: Month-end close completed (Accounting Team)
2. Collect withholding tax data from all agencies (Accounting Team)
3. Prepare Form 1601-C schedules (Accounting Team)
4. Decision: Data complete? If No, return to step 2
5. Submit for review (Senior Accountants)
6. Review calculations and schedules (Senior Accountants)
7. Decision: Review passed? If No, return to Accounting for corrections
8. Submit for approval (Finance Managers)
9. Approve submission (Finance Managers)
10. Final sign-off (Director)
11. File with BIR e-filing system (Senior Accountants)
12. Generate confirmation receipt (Senior Accountants)
13. Archive documents (Accounting Team)
14. End

**Color Scheme:**
- Use red theme (#f8cecc) for compliance/critical activities
- Use yellow (#fff2cc) for review activities
- Use green (#d5e8d4) for completed/success states

**Deadline Indicator:**
Add a note: "Deadline: 10th day of following month"
```

## Expected Output
A complete .drawio XML file with:
- 4 horizontal swimlanes (one per department)
- 14 process steps properly placed
- 2 decision diamonds with Yes/No paths
- Connectors showing process flow
- Professional red compliance color scheme
- Deadline notation
- All shapes properly aligned and sized

## Follow-up Requests

After initial creation, you can ask:
- "Add a parallel process for penalty calculation if deadline is missed"
- "Include a subprocess for multi-agency data consolidation"
- "Add icons from Material Design library for documents and approvals"
- "Create a RACI matrix for this same process"
