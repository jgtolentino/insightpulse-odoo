# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
import json
import subprocess
from pathlib import Path

_logger = logging.getLogger(__name__)


class KnowledgeAgent(models.Model):
    """Odoo Knowledge Agent - Forum scraper and error prevention"""

    _name = 'odoo.knowledge.agent'
    _description = 'Odoo Knowledge Agent'
    _order = 'create_date desc'

    name = fields.Char(string='Scrape Session', required=True, default='Forum Scrape')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ], default='draft', string='Status')

    scrape_date = fields.Datetime(string='Scrape Date', default=fields.Datetime.now)
    pages_scraped = fields.Integer(string='Pages Scraped', default=0)
    issues_found = fields.Integer(string='Issues Found', default=0)
    output_file = fields.Char(string='Output File')
    error_message = fields.Text(string='Error Message')

    log_ids = fields.One2many('odoo.knowledge.agent.log', 'agent_id', string='Logs')

    def action_run_scraper(self):
        """Run the forum scraper manually"""
        self.ensure_one()
        return self._run_forum_scraper()

    @api.model
    def cron_scrape_forum(self):
        """Cron job to scrape Odoo forum for solved issues"""
        _logger.info("🔍 Starting scheduled forum scraping...")

        # Create new scrape session
        agent = self.create({
            'name': f'Scheduled Scrape {fields.Datetime.now()}',
            'state': 'running',
        })

        try:
            agent._run_forum_scraper()
        except Exception as e:
            _logger.error(f"Forum scraping failed: {e}", exc_info=True)
            agent.write({
                'state': 'failed',
                'error_message': str(e),
            })

    def _run_forum_scraper(self):
        """Execute the forum scraper script"""
        self.ensure_one()

        try:
            self.write({'state': 'running'})

            # Path to scraper script
            scraper_path = Path(__file__).parent.parent.parent.parent.parent / 'agents' / 'odoo-knowledge' / 'scraper' / 'scrape_solved_threads.py'

            if not scraper_path.exists():
                raise FileNotFoundError(f"Scraper script not found: {scraper_path}")

            _logger.info(f"Running scraper: {scraper_path}")

            # Run the scraper script
            result = subprocess.run(
                ['python3', str(scraper_path)],
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hour timeout
            )

            if result.returncode == 0:
                # Parse output to get statistics
                output = result.stdout
                _logger.info(f"Scraper output: {output}")

                # Try to read the output file
                output_dir = scraper_path.parent.parent / 'knowledge'
                output_file = output_dir / 'solved_issues_raw.json'

                if output_file.exists():
                    with open(output_file, 'r') as f:
                        data = json.load(f)
                        issues_count = len(data)
                        pages_count = max([issue.get('page', 0) for issue in data]) if data else 0

                    self.write({
                        'state': 'done',
                        'pages_scraped': pages_count,
                        'issues_found': issues_count,
                        'output_file': str(output_file),
                    })

                    # Create log entry
                    self.env['odoo.knowledge.agent.log'].create({
                        'agent_id': self.id,
                        'message': f'Successfully scraped {pages_count} pages, found {issues_count} issues',
                        'level': 'info',
                    })

                    _logger.info(f"✅ Forum scraping completed: {issues_count} issues from {pages_count} pages")
                else:
                    raise FileNotFoundError(f"Output file not found: {output_file}")
            else:
                error_msg = result.stderr or result.stdout
                raise Exception(f"Scraper failed with code {result.returncode}: {error_msg}")

        except subprocess.TimeoutExpired:
            error_msg = "Scraper timeout after 1 hour"
            _logger.error(error_msg)
            self.write({
                'state': 'failed',
                'error_message': error_msg,
            })

        except Exception as e:
            error_msg = str(e)
            _logger.error(f"Forum scraping error: {error_msg}", exc_info=True)
            self.write({
                'state': 'failed',
                'error_message': error_msg,
            })

            # Create error log
            self.env['odoo.knowledge.agent.log'].create({
                'agent_id': self.id,
                'message': error_msg,
                'level': 'error',
            })


class KnowledgeAgentLog(models.Model):
    """Log entries for knowledge agent scraping"""

    _name = 'odoo.knowledge.agent.log'
    _description = 'Knowledge Agent Log'
    _order = 'create_date desc'

    agent_id = fields.Many2one('odoo.knowledge.agent', string='Agent', required=True, ondelete='cascade')
    message = fields.Text(string='Message', required=True)
    level = fields.Selection([
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ], default='info', string='Level')
    create_date = fields.Datetime(string='Date', default=fields.Datetime.now)
