# RACI Matrix Template

Use this template when asking Claude to create a RACI (Responsible, Accountable, Consulted, Informed) matrix.

## RACI Definitions

- **R (Responsible)**: Does the work to complete the task
- **A (Accountable)**: Ultimately answerable for completion (only ONE per task)
- **C (Consulted)**: Provides input (two-way communication)
- **I (Informed)**: Kept up-to-date (one-way communication)

## Template Request Format

```
Create a RACI matrix for [PROCESS/PROJECT NAME] with the following:

**Roles (Columns):**
- [Role 1: e.g., Project Manager]
- [Role 2: e.g., Developer]
- [Role 3: e.g., QA Tester]
- [Role 4: e.g., Sponsor]
- [Role 5: ...]

**Activities/Tasks (Rows):**
1. [Activity 1: e.g., Define Requirements]
2. [Activity 2: e.g., Design Solution]
3. [Activity 3: e.g., Develop Code]
4. [Activity 4: e.g., Test Solution]
5. [Activity 5: e.g., Deploy to Production]
6. [Activity 6: ...]

**Color Coding:**
- R (Responsible): Green (#d5e8d4)
- A (Accountable): Blue (#dae8fc)
- C (Consulted): Yellow (#fff2cc)
- I (Informed): Purple (#e1d5e7)

**Format:** 
Create as a draw.io table or simple markdown table
```

## Example 1: Finance SSC Month-End Closing

```
Create a RACI matrix for month-end closing process with these roles:

**Roles:**
- RIM (Accounting Team)
- CKVC (Accounting Team)
- BOM (Accounting Team)
- JPAL (Senior Accountant)
- JLI (Senior Accountant)
- JAP (Finance Manager)
- LAS (Finance Manager)
- RMQB (Director)

**Activities:**
1. Trial Balance Preparation
2. Journal Entry Recording
3. Bank Reconciliations
4. Intercompany Reconciliations
5. Financial Statement Preparation
6. Review and Validation
7. Management Review
8. Final Approval
9. Period Close and Lock
10. Financial Report Distribution

Use standard RACI color coding.
```

## Example 2: BIR Tax Filing Process

```
Create a RACI matrix for BIR Form 1601-C monthly filing with:

**Roles:**
- Accounting Team (RIM, CKVC, BOM)
- Senior Accountants (JPAL, JLI)
- Finance Managers (JAP, LAS)
- Director (RMQB)
- BIR e-Filing System (External)

**Activities:**
1. Collect withholding tax data
2. Prepare Form 1601-C schedules
3. Review calculations
4. Validate against payroll
5. Approve for filing
6. Submit to BIR e-filing
7. Obtain confirmation receipt
8. Archive compliance documents
9. Update tax register
10. Report filing status

Use red theme (#f8cecc) for compliance activities.
```

## Example 3: Software Development Project

```
Create a RACI matrix for Odoo module development with:

**Roles:**
- Product Owner
- Scrum Master
- Backend Developer
- Frontend Developer
- QA Engineer
- DevOps Engineer
- Business Analyst
- End Users

**Activities:**
1. Define user stories
2. Prioritize backlog
3. Sprint planning
4. Backend development
5. Frontend development
6. Unit testing
7. Integration testing
8. User acceptance testing
9. Code review
10. Deployment to staging
11. Deployment to production
12. Post-deployment monitoring
13. Bug fixes
14. Documentation
15. Training
```

## RACI Rules

**Critical Rules:**
1. Every task must have exactly ONE "A" (Accountable)
2. Every task must have at least ONE "R" (Responsible)
3. Multiple people can be "R" for the same task
4. Multiple people can be "C" or "I"
5. One person can have multiple roles (e.g., both R and C)
6. Avoid too many "C"s - causes bottlenecks

**Best Practices:**
- If someone is "A", they might also be "R"
- Keep "C" consultations to minimum (3-5 people max)
- "I" people should get updates but not block progress
- Review with stakeholders - they know if roles are right
- Update as project evolves

## Common Patterns

**Development Task:**
- Developer: R (does the work)
- Tech Lead: A (accountable for completion)
- QA: C (consulted on testability)
- Product Owner: I (informed of progress)

**Approval Task:**
- Preparer: R (creates the document)
- Manager: A (accountable for approval)
- Subject Matter Expert: C (consulted for accuracy)
- Stakeholders: I (informed of decision)

**Review Task:**
- Reviewer: R (performs the review)
- Document Owner: A (accountable for addressing feedback)
- Other Reviewers: C (consulted for additional input)
- Team: I (informed of review outcome)

## Validation Checklist

Before finalizing RACI matrix:
- [ ] Every task has exactly one "A"
- [ ] Every task has at least one "R"
- [ ] No person is overloaded (too many A's or R's)
- [ ] Consulted people have relevant expertise
- [ ] Informed list is not too long
- [ ] Roles and tasks are clear and specific
- [ ] Stakeholders have reviewed and agreed
- [ ] Matrix is easy to read and understand

## When to Use RACI

**Good Use Cases:**
- Complex projects with many stakeholders
- Cross-functional processes
- Unclear responsibilities
- Frequent confusion about who does what
- Handoffs between teams/departments
- Compliance-heavy processes

**Not Necessary For:**
- Very small teams (2-3 people)
- Simple, straightforward tasks
- Well-established processes everyone knows
- Solo work

## Alternatives to RACI

**RASCI**: Adds "S" for Supportive (helps R but doesn't own it)
**RACI-VS**: Adds "V" for Verifier, "S" for Signatory
**DACI**: Driver, Approver, Contributors, Informed (emphasizes leadership)
**RAPID**: Recommend, Agree, Perform, Input, Decide (decision-focused)

Choose RACI for most general project management needs.

## Tips for Creating Effective RACI Matrices

1. **Start with activities** - list all tasks first
2. **Identify roles** - who needs to be involved?
3. **Assign one A per row** - find the decision maker
4. **Add R's** - who does the actual work?
5. **Be selective with C's** - only those who must be consulted
6. **Keep I's informed** - stakeholders who need to know
7. **Review with team** - validate assignments
8. **Use color coding** - makes it easier to scan
9. **Keep updated** - roles change over time
10. **Make it visible** - share with all stakeholders

## Integration with Other Documents

RACI matrices work well with:
- **WBS**: Map RACI to work packages
- **Organization Chart**: Shows reporting relationships
- **Communication Plan**: Defines how to communicate
- **Stakeholder Register**: Identifies all parties
- **Process Flowcharts**: Shows task sequence
