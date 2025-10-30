# -*- coding: utf-8 -*-
"""GitHub webhook controller for pulser-hub integration."""

from odoo import http
from odoo.http import request
import json
import hmac
import hashlib
import logging

_logger = logging.getLogger(__name__)


class GitHubWebhookController(http.Controller):
    """Handle GitHub webhook events from pulser-hub app."""

    @http.route('/odoo/github/webhook', type='json', auth='public', csrf=False, methods=['POST'])
    def github_webhook(self, **kwargs):
        """
        Main webhook endpoint for GitHub events.

        Headers:
            X-GitHub-Event: Event type (pull_request, issues, push, etc.)
            X-Hub-Signature-256: HMAC signature for verification
            X-GitHub-Delivery: Unique delivery ID

        Returns:
            dict: Status response
        """
        try:
            # Get request data
            payload = request.httprequest.data
            signature = request.httprequest.headers.get('X-Hub-Signature-256')
            event_type = request.httprequest.headers.get('X-GitHub-Event')
            delivery_id = request.httprequest.headers.get('X-GitHub-Delivery')

            _logger.info(f"Received GitHub webhook: {event_type} (delivery: {delivery_id})")

            # Verify signature
            webhook_secret = request.env['ir.config_parameter'].sudo().get_param('github.webhook_secret')
            if not self._verify_signature(payload, signature, webhook_secret):
                _logger.warning(f"Invalid webhook signature for delivery {delivery_id}")
                return {'error': 'Invalid signature'}, 401

            # Parse payload
            data = json.loads(payload)

            # Log webhook event
            webhook_record = request.env['github.webhook.event'].sudo().create({
                'event_type': event_type,
                'delivery_id': delivery_id,
                'payload': json.dumps(data, indent=2),
                'status': 'received',
            })

            # Route to appropriate handler
            handlers = {
                'pull_request': self._handle_pull_request,
                'pull_request_review': self._handle_pr_review,
                'issues': self._handle_issue,
                'push': self._handle_push,
                'issue_comment': self._handle_comment,
            }

            handler = handlers.get(event_type)
            if handler:
                try:
                    handler(data)
                    webhook_record.write({'status': 'processed'})
                    _logger.info(f"Successfully processed {event_type} webhook")
                    return {'status': 'ok', 'message': f'{event_type} processed'}
                except Exception as e:
                    webhook_record.write({
                        'status': 'error',
                        'error_message': str(e)
                    })
                    _logger.error(f"Error processing {event_type}: {str(e)}")
                    return {'error': str(e)}, 500
            else:
                webhook_record.write({'status': 'ignored'})
                _logger.info(f"Ignored {event_type} event (no handler)")
                return {'status': 'ignored', 'message': f'{event_type} not handled'}

        except Exception as e:
            _logger.error(f"Webhook processing failed: {str(e)}")
            return {'error': str(e)}, 500

    def _verify_signature(self, payload, signature, secret):
        """
        Verify GitHub webhook signature.

        Args:
            payload (bytes): Request body
            signature (str): X-Hub-Signature-256 header value
            secret (str): Webhook secret

        Returns:
            bool: True if signature is valid
        """
        if not signature or not secret:
            return False

        expected = 'sha256=' + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def _handle_pull_request(self, data):
        """Handle pull_request events."""
        action = data['action']
        pr = data['pull_request']
        repo = data['repository']['full_name']

        _logger.info(f"Processing PR #{pr['number']} ({action}) in {repo}")

        PullRequest = request.env['github.pull.request'].sudo()

        # Find or create PR record
        pr_record = PullRequest.search([
            ('number', '=', pr['number']),
            ('repository_name', '=', repo)
        ], limit=1)

        if action == 'opened':
            if not pr_record:
                pr_record = PullRequest.create({
                    'number': pr['number'],
                    'title': pr['title'],
                    'body': pr.get('body', ''),
                    'repository_name': repo,
                    'state': pr['state'],
                    'author': pr['user']['login'],
                    'url': pr['html_url'],
                    'head_ref': pr['head']['ref'],
                    'base_ref': pr['base']['ref'],
                    'created_at': pr['created_at'],
                })
                _logger.info(f"Created PR record: {pr_record.id}")

        elif action in ['closed', 'merged']:
            if pr_record:
                pr_record.write({
                    'state': 'closed',
                    'merged': pr.get('merged', False),
                    'closed_at': pr.get('closed_at'),
                })
                _logger.info(f"Updated PR #{pr['number']} state to closed/merged")

        elif action == 'synchronize':
            if pr_record:
                pr_record.write({
                    'updated_at': pr['updated_at'],
                })

        # Trigger Odoo automated actions if configured
        if pr_record and action in ['opened', 'closed']:
            self._trigger_automated_actions(pr_record, f'github_pr_{action}')

    def _handle_pr_review(self, data):
        """Handle pull_request_review events."""
        review = data['review']
        pr = data['pull_request']
        repo = data['repository']['full_name']

        _logger.info(f"Processing review for PR #{pr['number']} by {review['user']['login']}")

        PullRequest = request.env['github.pull.request'].sudo()
        pr_record = PullRequest.search([
            ('number', '=', pr['number']),
            ('repository_name', '=', repo)
        ], limit=1)

        if pr_record:
            # Update approval count
            if review['state'] == 'approved':
                pr_record.write({
                    'approvals': pr_record.approvals + 1
                })
                _logger.info(f"PR #{pr['number']} now has {pr_record.approvals} approvals")

    def _handle_issue(self, data):
        """Handle issues events."""
        action = data['action']
        issue = data['issue']
        repo = data['repository']['full_name']

        # Skip if issue is actually a PR
        if 'pull_request' in issue:
            return

        _logger.info(f"Processing issue #{issue['number']} ({action}) in {repo}")

        Issue = request.env['github.issue'].sudo()

        # Find or create issue record
        issue_record = Issue.search([
            ('number', '=', issue['number']),
            ('repository_name', '=', repo)
        ], limit=1)

        if action == 'opened' and not issue_record:
            issue_record = Issue.create({
                'number': issue['number'],
                'title': issue['title'],
                'body': issue.get('body', ''),
                'repository_name': repo,
                'state': issue['state'],
                'author': issue['user']['login'],
                'url': issue['html_url'],
                'created_at': issue['created_at'],
            })
            _logger.info(f"Created issue record: {issue_record.id}")

            # Auto-create Odoo task if configured
            self._create_task_from_issue(issue_record)

        elif action == 'closed' and issue_record:
            issue_record.write({
                'state': 'closed',
                'closed_at': issue.get('closed_at'),
            })

    def _handle_push(self, data):
        """Handle push events."""
        ref = data['ref']
        commits = data['commits']
        repo = data['repository']['full_name']

        _logger.info(f"Processing push to {ref} in {repo} ({len(commits)} commits)")

        # Log significant pushes (main/develop only)
        if ref in ['refs/heads/main', 'refs/heads/develop']:
            request.env['github.push.event'].sudo().create({
                'repository_name': repo,
                'ref': ref,
                'commits_count': len(commits),
                'pusher': data['pusher']['name'],
                'head_commit_sha': data['head_commit']['id'],
                'head_commit_message': data['head_commit']['message'],
            })

    def _handle_comment(self, data):
        """Handle issue_comment events."""
        comment = data['comment']
        issue = data['issue']
        repo = data['repository']['full_name']

        body = comment['body'].strip()

        _logger.info(f"Processing comment on issue #{issue['number']}: {body[:50]}")

        # Check for bot commands
        if body.startswith('/'):
            parts = body.split()
            command = parts[0][1:]  # Remove leading /
            args = parts[1:] if len(parts) > 1 else []

            _logger.info(f"Bot command detected: {command} with args {args}")
            self._execute_bot_command(issue, comment, command, args, repo)

    def _execute_bot_command(self, issue, comment, command, args, repo):
        """Execute bot command from issue/PR comment."""
        supported_commands = ['odoo-sync', 'odoo-link', 'odoo-status']

        if command not in supported_commands:
            _logger.info(f"Unsupported bot command: {command}")
            return

        # Example: /odoo-sync - Create Odoo task from GitHub issue
        if command == 'odoo-sync':
            Issue = request.env['github.issue'].sudo()
            issue_record = Issue.search([
                ('number', '=', issue['number']),
                ('repository_name', '=', repo)
            ], limit=1)

            if issue_record:
                self._create_task_from_issue(issue_record)

    def _create_task_from_issue(self, issue_record):
        """Create Odoo project task from GitHub issue."""
        Task = request.env['project.task'].sudo()

        # Check if task already exists
        existing = Task.search([
            ('github_issue_number', '=', issue_record.number),
            ('github_repository', '=', issue_record.repository_name)
        ], limit=1)

        if not existing:
            task = Task.create({
                'name': issue_record.title,
                'description': issue_record.body,
                'github_issue_number': issue_record.number,
                'github_issue_url': issue_record.url,
                'github_repository': issue_record.repository_name,
            })
            _logger.info(f"Created Odoo task {task.id} from GitHub issue #{issue_record.number}")
            issue_record.write({'odoo_task_id': task.id})

    def _trigger_automated_actions(self, record, trigger_name):
        """Trigger Odoo automated actions based on GitHub events."""
        # Find relevant automated actions (Odoo Studio feature)
        AutomatedAction = request.env['base.automation'].sudo()
        actions = AutomatedAction.search([
            ('trigger', '=', 'on_create' if 'opened' in trigger_name else 'on_write'),
            ('model_id.model', '=', record._name),
            ('active', '=', True),
        ])

        for action in actions:
            try:
                action._process(record)
                _logger.info(f"Triggered automated action: {action.name}")
            except Exception as e:
                _logger.error(f"Failed to trigger action {action.name}: {str(e)}")
