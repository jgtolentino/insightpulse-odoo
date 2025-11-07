"""
Meeting to PRD Agent
Converts meeting notes into structured PRD and tasks
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from tools.odoo_client import OdooClient
from tools.slack_client import SlackClient
from tools.llm_client import LLMClient
from memory.kv_store import MemoryKVStore

logger = logging.getLogger(__name__)


class MeetingToPRDAgent:
    """
    Agent that processes meeting notes and generates:
    1. Structured PRD (Product Requirements Document)
    2. Actionable tasks
    3. Slack notification

    Workflow:
    - Fetch meeting details from Odoo calendar
    - Get team writing style from memory
    - Generate PRD using LLM
    - Create ip.page record in Odoo
    - Extract tasks from PRD
    - Create project.task records
    - Post Slack summary with links
    """

    def __init__(
        self,
        odoo_client: OdooClient,
        slack_client: SlackClient,
        memory_store: MemoryKVStore,
        llm_client: Optional[LLMClient] = None
    ):
        self.odoo = odoo_client
        self.slack = slack_client
        self.memory = memory_store
        self.llm = llm_client or LLMClient()

    async def execute(
        self,
        meeting_id: int,
        run_id: int,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute the Meeting→PRD workflow

        Args:
            meeting_id: Odoo calendar.event ID
            run_id: ip.agent.run ID for tracking
            user_id: User who triggered the workflow

        Returns:
            dict: Results with page_id, task_ids, etc.
        """
        try:
            logger.info(f"[Run {run_id}] Starting Meeting→PRD for meeting {meeting_id}")

            # Step 1: Fetch meeting details
            meeting = await self._fetch_meeting(meeting_id)
            if not meeting:
                raise ValueError(f"Meeting {meeting_id} not found")

            logger.info(f"[Run {run_id}] Fetched meeting: {meeting['name']}")

            # Step 2: Get team context from memory
            team_context = await self._get_team_context(
                team_id=meeting.get('project_id'),
                user_id=user_id
            )

            # Step 3: Generate PRD using LLM
            logger.info(f"[Run {run_id}] Generating PRD...")
            prd_content = await self._generate_prd(
                meeting=meeting,
                team_context=team_context,
                run_id=run_id
            )

            # Step 4: Create ip.page record
            logger.info(f"[Run {run_id}] Creating page in Odoo...")
            page = await self._create_page(
                title=f"PRD: {meeting['name']}",
                content=prd_content,
                meeting_id=meeting_id,
                team_id=meeting.get('project_id'),
                run_id=run_id
            )

            page_id = page['id']
            logger.info(f"[Run {run_id}] Created page {page_id}")

            # Step 5: Extract tasks from PRD
            logger.info(f"[Run {run_id}] Extracting tasks...")
            tasks = await self._extract_tasks(
                prd_content=prd_content,
                page_id=page_id,
                team_id=meeting.get('project_id'),
                run_id=run_id
            )

            task_ids = [t['id'] for t in tasks]
            logger.info(f"[Run {run_id}] Created {len(task_ids)} tasks")

            # Step 6: Post Slack notification
            if meeting.get('slack_channel_id'):
                logger.info(f"[Run {run_id}] Posting to Slack...")
                await self._post_slack_summary(
                    meeting=meeting,
                    page_id=page_id,
                    task_ids=task_ids,
                    channel_id=meeting['slack_channel_id']
                )

            # Step 7: Update agent run as completed
            self.odoo.update_agent_run(
                run_id=run_id,
                status='completed',
                output_data={
                    'page_id': page_id,
                    'task_ids': task_ids,
                    'task_count': len(task_ids)
                }
            )

            logger.info(f"[Run {run_id}] ✅ Workflow completed successfully")

            return {
                'page_id': page_id,
                'task_ids': task_ids,
                'message': 'PRD and tasks created successfully'
            }

        except Exception as e:
            logger.error(f"[Run {run_id}] ❌ Error: {str(e)}", exc_info=True)

            # Update agent run as failed
            self.odoo.update_agent_run(
                run_id=run_id,
                status='failed',
                error_message=str(e)
            )

            raise

    async def _fetch_meeting(self, meeting_id: int) -> Optional[Dict[str, Any]]:
        """Fetch meeting details from Odoo"""
        meetings = self.odoo.search_read(
            model='calendar.event',
            domain=[('id', '=', meeting_id)],
            fields=[
                'name', 'description', 'start', 'stop',
                'partner_ids', 'user_id', 'project_id',
                'location', 'videocall_location'
            ]
        )
        return meetings[0] if meetings else None

    async def _get_team_context(
        self,
        team_id: Optional[int],
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """Get team writing style and preferences from memory"""
        context = {}

        # Get team writing style
        if team_id:
            style = self.memory.get(
                scope='team',
                key='writing_style',
                owner_id=team_id
            )
            if style:
                context['writing_style'] = style

        # Get org-wide PRD template
        template = self.memory.get(
            scope='org',
            key='prd_template'
        )
        if template:
            context['prd_template'] = template

        # Get user preferences
        if user_id:
            prefs = self.memory.get(
                scope='user',
                key='preferences',
                owner_id=user_id
            )
            if prefs:
                context['user_preferences'] = prefs

        return context

    async def _generate_prd(
        self,
        meeting: Dict[str, Any],
        team_context: Dict[str, Any],
        run_id: int
    ) -> str:
        """Generate PRD content using LLM"""

        # Build prompt
        prompt = self._build_prd_prompt(meeting, team_context)

        # Call LLM
        response = await self.llm.generate(
            prompt=prompt,
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            temperature=0.7,
            metadata={'run_id': run_id, 'workflow': 'meeting-to-prd'}
        )

        # Log token usage and cost
        self.odoo.update_agent_run(
            run_id=run_id,
            tokens_used=response['usage']['total_tokens'],
            cost_cents=response['cost_cents']
        )

        return response['content']

    def _build_prd_prompt(
        self,
        meeting: Dict[str, Any],
        team_context: Dict[str, Any]
    ) -> str:
        """Build LLM prompt for PRD generation"""

        template = team_context.get('prd_template', {})
        style = team_context.get('writing_style', {})

        prompt = f"""You are a product manager writing a PRD (Product Requirements Document) based on a meeting.

Meeting Details:
- Title: {meeting['name']}
- Date: {meeting['start']}
- Description: {meeting.get('description', 'N/A')}
- Attendees: {len(meeting.get('partner_ids', []))} people

Writing Style: {style.get('tone', 'professional and concise')}

Generate a structured PRD with the following sections:

## Executive Summary
Brief overview of what was decided/discussed

## Background
Context and problem statement

## Goals & Objectives
What we're trying to achieve

## Requirements
### Functional Requirements
- FR1: [Description]
- FR2: [Description]

### Non-Functional Requirements
- NFR1: [Description]

## User Stories
- As a [role], I want [feature] so that [benefit]

## Tasks
Break down into actionable tasks:
- [ ] Task 1
- [ ] Task 2

## Success Metrics
How we'll measure success

## Timeline
Proposed timeline and milestones

Keep it concise and actionable. Use markdown formatting.
"""

        return prompt

    async def _create_page(
        self,
        title: str,
        content: str,
        meeting_id: int,
        team_id: Optional[int],
        run_id: int
    ) -> Dict[str, Any]:
        """Create ip.page record in Odoo"""

        page_data = {
            'name': title,
            'body_md': content,
            'page_type': 'prd',
            'status': 'draft',
            'source_type': 'meeting',
            'source_id': str(meeting_id),
            'created_by_agent': True,
            'agent_run_id': run_id,
            'team_id': team_id,
        }

        page_id = self.odoo.create('ip.page', page_data)

        # Fetch created page
        pages = self.odoo.search_read(
            model='ip.page',
            domain=[('id', '=', page_id)],
            fields=['id', 'name']
        )

        return pages[0] if pages else {'id': page_id, 'name': title}

    async def _extract_tasks(
        self,
        prd_content: str,
        page_id: int,
        team_id: Optional[int],
        run_id: int
    ) -> List[Dict[str, Any]]:
        """Extract tasks from PRD and create project.task records"""

        # Use LLM to extract structured tasks
        prompt = f"""Extract actionable tasks from this PRD. Return as JSON array.

PRD:
{prd_content}

Format:
[
  {{"title": "Task title", "description": "Details", "priority": "1|2|3"}},
  ...
]

Only include tasks from the "Tasks" section. Be specific and actionable.
"""

        response = await self.llm.generate(
            prompt=prompt,
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.3,
            metadata={'run_id': run_id, 'step': 'task_extraction'}
        )

        # Parse JSON
        try:
            tasks_json = json.loads(response['content'])
        except json.JSONDecodeError:
            # Fallback: extract markdown checkboxes
            tasks_json = self._extract_tasks_from_markdown(prd_content)

        # Create tasks in Odoo
        created_tasks = []
        for task_data in tasks_json:
            task_id = self.odoo.create('project.task', {
                'name': task_data['title'],
                'description': task_data.get('description', ''),
                'priority': task_data.get('priority', '1'),
                'project_id': team_id,
                'page_id': page_id,
            })

            created_tasks.append({
                'id': task_id,
                'title': task_data['title']
            })

        return created_tasks

    def _extract_tasks_from_markdown(self, content: str) -> List[Dict[str, Any]]:
        """Fallback: extract tasks from markdown checkboxes"""
        import re

        tasks = []
        # Match: - [ ] Task name
        pattern = r'-\s*\[\s*\]\s*(.+)'
        matches = re.findall(pattern, content)

        for match in matches:
            tasks.append({
                'title': match.strip(),
                'description': '',
                'priority': '2'
            })

        return tasks

    async def _post_slack_summary(
        self,
        meeting: Dict[str, Any],
        page_id: int,
        task_ids: List[int],
        channel_id: str
    ):
        """Post summary to Slack"""

        # Get Odoo base URL
        base_url = "https://erp.insightpulseai.net"
        page_url = f"{base_url}/web#id={page_id}&model=ip.page&view_type=form"

        # Build message
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🤖 PRD Generated: {meeting['name']}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"I've created a PRD from your meeting:\n• *{len(task_ids)} tasks* extracted\n• <{page_url}|View PRD in Odoo>"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Meeting: {meeting['start'][:10]} | Generated by AI Agent"
                    }
                ]
            }
        ]

        await self.slack.post_message(
            channel=channel_id,
            text=f"PRD generated for {meeting['name']}",
            blocks=blocks
        )
