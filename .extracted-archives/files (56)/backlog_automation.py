#!/usr/bin/env python3
"""
Automated Backlog Management Workflow
Orchestrates feature discovery, classification, and Notion sync
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class BacklogAutomation:
    """Orchestrates the complete backlog automation workflow"""
    
    def __init__(self, 
                 repo_path: str = ".",
                 github_repo: str = "jgtolentino/insightpulse-odoo",
                 output_dir: str = "backlog_output"):
        self.repo_path = Path(repo_path)
        self.github_repo = github_repo
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Timestamp for this run
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Output files
        self.backlog_json = self.output_dir / f"backlog_{self.run_timestamp}.json"
        self.backlog_latest = self.output_dir / "backlog_latest.json"
        self.summary_report = self.output_dir / f"summary_{self.run_timestamp}.md"
        self.notion_commands = self.output_dir / f"notion_commands_{self.run_timestamp}.txt"
        self.diff_report = self.output_dir / f"diff_{self.run_timestamp}.md"
    
    def run_discovery(self) -> bool:
        """Execute feature discovery"""
        print("="*80)
        print("🔍 STEP 1: FEATURE DISCOVERY")
        print("="*80)
        
        try:
            # Import and run discovery
            sys.path.insert(0, str(Path(__file__).parent))
            from feature_discovery import FeatureDiscovery
            
            discovery = FeatureDiscovery(
                repo_path=str(self.repo_path),
                github_repo=self.github_repo
            )
            
            features = discovery.discover_modules()
            
            if not features:
                print("❌ No features discovered")
                return False
            
            # Export results
            discovery.export_to_json(str(self.backlog_json))
            discovery.print_summary()
            
            # Create latest symlink
            if self.backlog_latest.exists():
                self.backlog_latest.unlink()
            self.backlog_latest.symlink_to(self.backlog_json.name)
            
            # Generate summary report
            self._generate_summary_report(discovery)
            
            print(f"\n✅ Discovery complete: {len(features)} features")
            return True
            
        except Exception as e:
            print(f"❌ Discovery failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_notion_sync(self) -> bool:
        """Generate Notion sync commands"""
        print("\n" + "="*80)
        print("📋 STEP 2: NOTION SYNC GENERATION")
        print("="*80)
        
        try:
            from notion_sync import NotionBacklogSync
            
            sync = NotionBacklogSync(backlog_json_path=str(self.backlog_latest))
            sync.export_mcp_commands(output_path=str(self.notion_commands))
            
            print(f"✅ Notion commands generated: {self.notion_commands}")
            return True
            
        except Exception as e:
            print(f"❌ Notion sync generation failed: {e}")
            return False
    
    def compare_with_previous(self) -> Optional[Dict]:
        """Compare current backlog with previous run"""
        print("\n" + "="*80)
        print("📊 STEP 3: DIFF ANALYSIS")
        print("="*80)
        
        # Find previous backlog
        backlog_files = sorted(self.output_dir.glob("backlog_*.json"))
        if len(backlog_files) < 2:
            print("ℹ️  No previous backlog found for comparison")
            return None
        
        previous_backlog = backlog_files[-2]
        
        try:
            with open(previous_backlog, 'r') as f:
                previous_data = json.load(f)
            
            with open(self.backlog_latest, 'r') as f:
                current_data = json.load(f)
            
            diff = self._compute_diff(previous_data, current_data)
            self._generate_diff_report(diff, previous_backlog)
            
            return diff
            
        except Exception as e:
            print(f"⚠️  Diff analysis failed: {e}")
            return None
    
    def _compute_diff(self, previous: Dict, current: Dict) -> Dict:
        """Compute differences between two backlog snapshots"""
        
        prev_features = {f['external_id']: f for f in previous.get('features', [])}
        curr_features = {f['external_id']: f for f in current.get('features', [])}
        
        # New features
        new_ids = set(curr_features.keys()) - set(prev_features.keys())
        new_features = [curr_features[fid] for fid in new_ids]
        
        # Removed features
        removed_ids = set(prev_features.keys()) - set(curr_features.keys())
        removed_features = [prev_features[fid] for fid in removed_ids]
        
        # Modified features
        modified_features = []
        for fid in set(curr_features.keys()) & set(prev_features.keys()):
            prev_f = prev_features[fid]
            curr_f = curr_features[fid]
            
            changes = {}
            for key in ['version', 'deployment_status', 'priority', 'business_area', 'epic']:
                if prev_f.get(key) != curr_f.get(key):
                    changes[key] = {
                        'from': prev_f.get(key),
                        'to': curr_f.get(key)
                    }
            
            if changes:
                modified_features.append({
                    'module': curr_f['module_name'],
                    'display_name': curr_f['display_name'],
                    'changes': changes
                })
        
        return {
            'new_features': new_features,
            'removed_features': removed_features,
            'modified_features': modified_features,
            'total_previous': len(prev_features),
            'total_current': len(curr_features)
        }
    
    def _generate_summary_report(self, discovery):
        """Generate markdown summary report"""
        
        summary = discovery.generate_summary_report()
        
        report_lines = [
            f"# Feature Backlog Summary",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Repository:** {self.github_repo}",
            f"",
            f"## Overview",
            f"- **Total Features:** {summary['total_features']}",
            f"- **Total Story Points:** {summary['total_story_points']}",
            f"",
            f"## By Business Area",
            ""
        ]
        
        for area, count in sorted(summary['by_business_area'].items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"- **{area}:** {count}")
        
        report_lines.extend([
            "",
            "## By Deployment Status",
            ""
        ])
        
        for status, count in sorted(summary['by_status'].items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"- **{status}:** {count}")
        
        report_lines.extend([
            "",
            "## By Priority",
            ""
        ])
        
        for priority, count in sorted(summary['by_priority'].items()):
            report_lines.append(f"- **{priority}:** {count}")
        
        report_lines.extend([
            "",
            "## By Epic",
            ""
        ])
        
        for epic, count in sorted(summary['by_epic'].items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"- **{epic}:** {count}")
        
        report_lines.extend([
            "",
            "## Top Dependencies",
            ""
        ])
        
        for dep, count in list(summary['top_dependencies'].items())[:10]:
            report_lines.append(f"- **{dep}:** {count} modules")
        
        report_lines.extend([
            "",
            "## Files Generated",
            f"- Backlog JSON: `{self.backlog_json.name}`",
            f"- Latest symlink: `{self.backlog_latest.name}`",
            f"- Notion commands: `{self.notion_commands.name}`",
            ""
        ])
        
        with open(self.summary_report, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"📄 Summary report: {self.summary_report}")
    
    def _generate_diff_report(self, diff: Dict, previous_file: Path):
        """Generate markdown diff report"""
        
        report_lines = [
            f"# Backlog Changes Report",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Comparing to:** {previous_file.name}",
            f"",
            f"## Summary",
            f"- **Previous Total:** {diff['total_previous']}",
            f"- **Current Total:** {diff['total_current']}",
            f"- **Net Change:** {diff['total_current'] - diff['total_previous']:+d}",
            f"",
            f"## New Features ({len(diff['new_features'])})",
            ""
        ]
        
        if diff['new_features']:
            for feature in diff['new_features']:
                report_lines.append(
                    f"- ✨ **{feature['display_name']}** "
                    f"({feature['business_area']}, {feature['deployment_status']})"
                )
        else:
            report_lines.append("*No new features*")
        
        report_lines.extend([
            "",
            f"## Removed Features ({len(diff['removed_features'])})",
            ""
        ])
        
        if diff['removed_features']:
            for feature in diff['removed_features']:
                report_lines.append(
                    f"- ❌ **{feature['display_name']}** "
                    f"({feature['business_area']})"
                )
        else:
            report_lines.append("*No removed features*")
        
        report_lines.extend([
            "",
            f"## Modified Features ({len(diff['modified_features'])})",
            ""
        ])
        
        if diff['modified_features']:
            for feature in diff['modified_features']:
                report_lines.append(f"- 🔄 **{feature['display_name']}**")
                for field, change in feature['changes'].items():
                    report_lines.append(
                        f"  - {field}: `{change['from']}` → `{change['to']}`"
                    )
        else:
            report_lines.append("*No modified features*")
        
        report_lines.append("")
        
        with open(self.diff_report, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"📄 Diff report: {self.diff_report}")
    
    def cleanup_old_files(self, keep_last_n: int = 10):
        """Remove old backlog files, keeping last N"""
        print("\n" + "="*80)
        print("🧹 CLEANUP")
        print("="*80)
        
        # Get all backlog files sorted by date
        backlog_files = sorted(self.output_dir.glob("backlog_*.json"))
        
        if len(backlog_files) <= keep_last_n:
            print(f"ℹ️  Only {len(backlog_files)} backlog files, no cleanup needed")
            return
        
        # Remove old files
        files_to_remove = backlog_files[:-keep_last_n]
        
        for file in files_to_remove:
            # Also remove associated reports
            timestamp = file.stem.split('_', 1)[1]
            summary_file = self.output_dir / f"summary_{timestamp}.md"
            diff_file = self.output_dir / f"diff_{timestamp}.md"
            notion_file = self.output_dir / f"notion_commands_{timestamp}.txt"
            
            for f in [file, summary_file, diff_file, notion_file]:
                if f.exists():
                    f.unlink()
                    print(f"🗑️  Removed: {f.name}")
        
        print(f"✅ Cleanup complete, kept last {keep_last_n} runs")
    
    def run_full_workflow(self, cleanup: bool = True, keep_last_n: int = 10):
        """Execute complete workflow"""
        
        print("\n" + "="*80)
        print("🚀 AUTOMATED BACKLOG MANAGEMENT")
        print("="*80)
        print(f"Repository: {self.github_repo}")
        print(f"Output directory: {self.output_dir}")
        print(f"Run timestamp: {self.run_timestamp}")
        print("="*80 + "\n")
        
        # Step 1: Discovery
        if not self.run_discovery():
            print("❌ Workflow failed at discovery step")
            return False
        
        # Step 2: Notion sync generation
        if not self.generate_notion_sync():
            print("⚠️  Notion sync generation failed, but continuing...")
        
        # Step 3: Diff analysis
        self.compare_with_previous()
        
        # Step 4: Cleanup
        if cleanup:
            self.cleanup_old_files(keep_last_n=keep_last_n)
        
        # Final summary
        print("\n" + "="*80)
        print("✅ WORKFLOW COMPLETE")
        print("="*80)
        print(f"\n📁 Output files in: {self.output_dir}")
        print(f"  - Backlog JSON: {self.backlog_json.name}")
        print(f"  - Summary: {self.summary_report.name}")
        print(f"  - Notion commands: {self.notion_commands.name}")
        if self.diff_report.exists():
            print(f"  - Diff report: {self.diff_report.name}")
        
        print(f"\n📋 Next steps:")
        print(f"1. Review summary report: {self.summary_report}")
        print(f"2. Sync to Notion using: {self.notion_commands}")
        print(f"3. View changes: {self.diff_report if self.diff_report.exists() else 'N/A'}")
        print("")
        
        return True


def setup_cron_job():
    """Helper to setup cron job for automated runs"""
    
    script_path = Path(__file__).absolute()
    
    cron_entry = f"""
# Automated feature backlog management - runs daily at 2 AM
0 2 * * * cd {script_path.parent} && python3 {script_path.name} --auto >> /var/log/backlog_automation.log 2>&1
"""
    
    print("="*80)
    print("⏰ CRON JOB SETUP")
    print("="*80)
    print("\nTo setup automated daily runs, add this to your crontab:")
    print(cron_entry)
    print("\nTo edit crontab: crontab -e")
    print("="*80)


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Automated Feature Discovery and Backlog Management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full workflow
  python3 backlog_automation.py
  
  # Run with custom repo path
  python3 backlog_automation.py --repo-path /path/to/odoo
  
  # Disable cleanup
  python3 backlog_automation.py --no-cleanup
  
  # Show cron setup instructions
  python3 backlog_automation.py --setup-cron
        """
    )
    
    parser.add_argument('--repo-path', default='.',
                       help='Path to Odoo repository (default: current directory)')
    parser.add_argument('--github-repo', default='jgtolentino/insightpulse-odoo',
                       help='GitHub repository name')
    parser.add_argument('--output-dir', default='backlog_output',
                       help='Output directory for backlog files')
    parser.add_argument('--no-cleanup', action='store_true',
                       help='Disable automatic cleanup of old files')
    parser.add_argument('--keep-last', type=int, default=10,
                       help='Number of old backlog runs to keep (default: 10)')
    parser.add_argument('--setup-cron', action='store_true',
                       help='Show instructions for setting up cron job')
    parser.add_argument('--auto', action='store_true',
                       help='Automated mode (for cron jobs)')
    
    args = parser.parse_args()
    
    if args.setup_cron:
        setup_cron_job()
        return
    
    # Run workflow
    automation = BacklogAutomation(
        repo_path=args.repo_path,
        github_repo=args.github_repo,
        output_dir=args.output_dir
    )
    
    success = automation.run_full_workflow(
        cleanup=not args.no_cleanup,
        keep_last_n=args.keep_last
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
