#!/usr/bin/env python3
"""
Odoo Sprint Creator
Creates a new sprint in Odoo Project module with predefined tasks

Usage:
    python create_sprint.py --sprint-number 12 --start-date 2025-11-01 --end-date 2025-11-15
"""

import argparse
import xmlrpc.client
from datetime import datetime
from typing import List, Dict, Any


class OdooSprintCreator:
    """Manages sprint creation in Odoo Project module"""
    
    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.models = None
        
    def connect(self):
        """Authenticate with Odoo"""
        common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.uid = common.authenticate(self.db, self.username, self.password, {})
        
        if not self.uid:
            raise Exception("Authentication failed")
            
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
        print(f"✅ Connected to Odoo as user {self.username}")
        
    def create_project(self, name: str, description: str = "") -> int:
        """Create or get existing project"""
        # Check if project exists
        project_ids = self.models.execute_kw(
            self.db, self.uid, self.password,
            'project.project', 'search',
            [[('name', '=', name)]]
        )
        
        if project_ids:
            print(f"📁 Using existing project: {name}")
            return project_ids[0]
            
        # Create new project
        project_id = self.models.execute_kw(
            self.db, self.uid, self.password,
            'project.project', 'create',
            [{
                'name': name,
                'description': description,
                'privacy_visibility': 'followers',
                'allow_timesheets': True,
            }]
        )
        print(f"✨ Created new project: {name}")
        return project_id
        
    def create_sprint(
        self, 
        project_id: int, 
        sprint_number: int,
        start_date: str,
        end_date: str
    ) -> int:
        """Create sprint milestone"""
        sprint_name = f"Sprint {sprint_number} - {start_date} to {end_date}"
        
        # Check if sprint exists
        sprint_ids = self.models.execute_kw(
            self.db, self.uid, self.password,
            'project.milestone', 'search',
            [[('name', '=', sprint_name), ('project_id', '=', project_id)]]
        )
        
        if sprint_ids:
            print(f"📅 Using existing sprint: {sprint_name}")
            return sprint_ids[0]
            
        # Create sprint milestone
        sprint_id = self.models.execute_kw(
            self.db, self.uid, self.password,
            'project.milestone', 'create',
            [{
                'name': sprint_name,
                'project_id': project_id,
                'deadline': end_date,
            }]
        )
        print(f"🚀 Created sprint: {sprint_name}")
        return sprint_id
        
    def create_task(
        self,
        project_id: int,
        sprint_id: int,
        task_data: Dict[str, Any]
    ) -> int:
        """Create individual task in sprint"""
        task_id = self.models.execute_kw(
            self.db, self.uid, self.password,
            'project.task', 'create',
            [{
                'name': task_data['name'],
                'project_id': project_id,
                'milestone_id': sprint_id,
                'description': task_data.get('description', ''),
                'tag_ids': [(6, 0, task_data.get('tag_ids', []))],
                'user_ids': [(6, 0, task_data.get('user_ids', []))],
                'date_deadline': task_data.get('deadline'),
                'priority': task_data.get('priority', '0'),
            }]
        )
        print(f"  ✓ Created task: {task_data['name']}")
        return task_id


def get_default_tasks(sprint_number: int, end_date: str) -> List[Dict[str, Any]]:
    """Get default Finance SSC sprint tasks"""
    return [
        {
            'name': f'BIR Form 1601-C Automation',
            'description': '''
# User Story
As a Finance Manager, I want automated BIR Form 1601-C generation.

## Acceptance Criteria
- [ ] XML generation in BIR eFPS format
- [ ] ATP validation
- [ ] Support all 8 agencies
- [ ] Audit trail in Odoo

## Technical Tasks
- Database schema design
- Odoo model creation
- XML generation logic
- Unit tests
- Integration tests

## Story Points: 8
            ''',
            'deadline': end_date,
            'priority': '3',  # Very High
        },
        {
            'name': f'October Month-End Bank Reconciliation (All Agencies)',
            'description': '''
# Task
Reconcile October bank statements for all 8 agencies.

## Agencies
- RIM
- CKVC
- BOM
- JPAL
- JLI
- JAP
- LAS
- RMQB

## Story Points: 13
            ''',
            'deadline': end_date,
            'priority': '3',
        },
        {
            'name': f'Multi-Agency Trial Balance Consolidation',
            'description': '''
# User Story
Generate consolidated trial balance across all agencies.

## Features
- Inter-company elimination
- Drill-down to agency detail
- Excel export
- < 5 minute processing time

## Story Points: 5
            ''',
            'deadline': end_date,
            'priority': '2',  # High
        },
        {
            'name': f'PaddleOCR Confidence Scoring Improvement',
            'description': '''
# User Story
Improve receipt OCR accuracy to >= 95%.

## Tasks
- Collect 500 receipt samples
- Retrain model
- Implement confidence thresholds
- Performance testing on RTX 4090

## Story Points: 8
            ''',
            'deadline': end_date,
            'priority': '2',
        },
        {
            'name': f'CI/CD Pipeline Optimization',
            'description': '''
# Goal
Reduce CI/CD time to < 10 minutes.

## Tasks
- Parallelize tests
- Optimize Docker builds
- Cache dependencies
- Add metrics dashboard

## Story Points: 5
            ''',
            'deadline': end_date,
            'priority': '1',  # Normal
        },
    ]


def main():
    parser = argparse.ArgumentParser(
        description='Create Odoo sprint with Finance SSC tasks'
    )
    parser.add_argument(
        '--url',
        default='http://localhost:8069',
        help='Odoo URL (default: http://localhost:8069)'
    )
    parser.add_argument(
        '--db',
        default='odoo',
        help='Database name (default: odoo)'
    )
    parser.add_argument(
        '--username',
        default='admin',
        help='Odoo username (default: admin)'
    )
    parser.add_argument(
        '--password',
        required=True,
        help='Odoo password'
    )
    parser.add_argument(
        '--sprint-number',
        type=int,
        required=True,
        help='Sprint number (e.g., 12)'
    )
    parser.add_argument(
        '--start-date',
        required=True,
        help='Sprint start date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end-date',
        required=True,
        help='Sprint end date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--project-name',
        default='InsightPulse AI - Finance SSC',
        help='Project name (default: InsightPulse AI - Finance SSC)'
    )
    
    args = parser.parse_args()
    
    # Validate dates
    try:
        datetime.strptime(args.start_date, '%Y-%m-%d')
        datetime.strptime(args.end_date, '%Y-%m-%d')
    except ValueError:
        print("❌ Error: Dates must be in YYYY-MM-DD format")
        return 1
        
    # Connect to Odoo
    creator = OdooSprintCreator(
        url=args.url,
        db=args.db,
        username=args.username,
        password=args.password
    )
    
    try:
        creator.connect()
        
        # Create or get project
        project_id = creator.create_project(
            name=args.project_name,
            description="Finance Shared Service Center Odoo Development"
        )
        
        # Create sprint
        sprint_id = creator.create_sprint(
            project_id=project_id,
            sprint_number=args.sprint_number,
            start_date=args.start_date,
            end_date=args.end_date
        )
        
        # Create default tasks
        print(f"\n📝 Creating sprint tasks...")
        tasks = get_default_tasks(args.sprint_number, args.end_date)
        
        for task_data in tasks:
            creator.create_task(
                project_id=project_id,
                sprint_id=sprint_id,
                task_data=task_data
            )
            
        print(f"\n✅ Sprint {args.sprint_number} created successfully!")
        print(f"   Project ID: {project_id}")
        print(f"   Sprint ID: {sprint_id}")
        print(f"   Tasks created: {len(tasks)}")
        print(f"\n🌐 View in Odoo: {args.url}/web#view_type=kanban&model=project.task&cids=1&menu_id={project_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
        
    return 0


if __name__ == '__main__':
    exit(main())
