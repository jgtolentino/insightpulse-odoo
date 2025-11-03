# Example: Project Work Breakdown Structure (WBS)

## Use Case
Create a WBS for an Odoo ERP implementation project to replace SAP Concur.

## Request to Claude

```
Create a Work Breakdown Structure (WBS) for an Odoo ERP implementation project with the following structure:

**Level 0 (Project):**
Odoo ERP Implementation for Expense & Travel Management

**Level 1 (Major Deliverables):**
1. Project Management
2. Requirements & Design
3. Development & Configuration
4. Data Migration
5. Testing & Quality Assurance
6. Training & Change Management
7. Deployment & Go-Live
8. Post-Go-Live Support

**Level 2 (Sub-deliverables) - Expand each Level 1:**

1. Project Management
   - 1.1 Project Charter & Planning
   - 1.2 Resource Allocation
   - 1.3 Risk Management
   - 1.4 Status Reporting

2. Requirements & Design
   - 2.1 Business Requirements Gathering
   - 2.2 System Design
   - 2.3 Integration Design (Supabase, DigitalOcean)
   - 2.4 Architecture Review

3. Development & Configuration
   - 3.1 Odoo Module Configuration
   - 3.2 Custom Development
   - 3.3 AI/OCR Integration (PaddleOCR-VL)
   - 3.4 API Development
   - 3.5 Database Setup (PostgreSQL, Qdrant)

4. Data Migration
   - 4.1 SAP Concur Data Extraction
   - 4.2 Data Mapping & Transformation
   - 4.3 Data Validation
   - 4.4 Historical Data Load

5. Testing & Quality Assurance
   - 5.1 Unit Testing
   - 5.2 Integration Testing
   - 5.3 User Acceptance Testing (UAT)
   - 5.4 Performance Testing (RTX 4090 optimization)
   - 5.5 Security Testing

6. Training & Change Management
   - 6.1 Training Materials Development
   - 6.2 Admin Training
   - 6.3 End User Training (8 Finance SSC staff)
   - 6.4 Change Management Communications

7. Deployment & Go-Live
   - 7.1 Production Environment Setup (DigitalOcean)
   - 7.2 Deployment Automation (Docker)
   - 7.3 Go-Live Cutover
   - 7.4 Hypercare Support

8. Post-Go-Live Support
   - 8.1 Issue Resolution
   - 8.2 Performance Monitoring
   - 8.3 User Support
   - 8.4 Lessons Learned

**Formatting:**
- Use hierarchical numbering (1.0, 1.1, 1.2, etc.)
- Color scheme: Progressive shades of blue/green
  - Level 0: Dark Blue (#1ba1e2)
  - Level 1: Green (#60a917)
  - Level 2: Light Green (#d5e8d4)
- Box sizes: 200x80 for Level 0, 160x60 for Level 1, 140x50 for Level 2
- Vertical spacing: 40px between levels
- Horizontal spacing: 20px between boxes at same level
```

## Expected Output
A comprehensive WBS diagram with:
- Clear hierarchical structure (3 levels)
- Proper numbering (1.0, 1.1, 1.1.1)
- Color-coded by level
- Professional layout
- Well-aligned boxes
- Clear parent-child relationships

## Follow-up Requests

- "Add Level 3 work packages for Development & Configuration"
- "Create a corresponding RACI matrix for all Level 2 tasks"
- "Generate a Gantt chart from this WBS"
- "Add effort estimates to each work package"
- "Create a resource allocation chart"
