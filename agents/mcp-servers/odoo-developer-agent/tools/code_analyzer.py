"""
Odoo Code Analyzer & Debugger
Analyzes errors, suggests fixes, and auto-applies corrections
"""

import os
import re
import ast
from typing import Dict, List, Optional
from pathlib import Path
from anthropic import Anthropic
import structlog

from knowledge.rag_client import OdooKnowledgeBase, RAGContextBuilder

logger = structlog.get_logger()


class OdooCodeAnalyzer:
    """
    Analyzes and debugs Odoo code issues
    """
    
    def __init__(self):
        self.claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.kb = OdooKnowledgeBase()
        self.rag = RAGContextBuilder(self.kb)
    
    async def analyze_error(
        self,
        error_log: str,
        module_name: str,
        tenant_id: Optional[str] = None,
        auto_fix: bool = True
    ) -> Dict:
        """
        Analyze Odoo error and suggest/apply fixes
        
        Args:
            error_log: Full error traceback
            module_name: Module where error occurred
            tenant_id: Tenant identifier (for context)
            auto_fix: Whether to automatically apply fix if confidence > 90%
        
        Returns:
            Dict with analysis, fix, and application status
        """
        logger.info("analyzing_error", module=module_name, tenant=tenant_id)
        
        # Extract error details
        error_details = self._parse_error_log(error_log)
        
        # Build context from RAG
        context = await self.rag.build_debugging_context(
            error=error_log,
            module=module_name,
            tenant_id=tenant_id
        )
        
        # Analyze with Claude
        analysis = await self._perform_analysis(
            error_details=error_details,
            module_name=module_name,
            context=context
        )
        
        # Determine if auto-fix is safe
        should_auto_fix = (
            auto_fix and
            analysis['confidence'] > 0.90 and
            analysis['risk_level'] == 'low'
        )
        
        result = {
            "error_type": error_details['type'],
            "root_cause": analysis['root_cause'],
            "affected_components": analysis['affected_components'],
            "fix_steps": analysis['fix_steps'],
            "code_changes": analysis['code_changes'],
            "confidence": analysis['confidence'],
            "risk_level": analysis['risk_level'],
            "prevention_tips": analysis['prevention_tips']
        }
        
        if should_auto_fix:
            # Apply fixes
            fix_result = await self._apply_fixes(
                module_name=module_name,
                code_changes=analysis['code_changes'],
                tenant_id=tenant_id
            )
            
            result['auto_fix_applied'] = True
            result['fix_result'] = fix_result
            
            # Store solution in knowledge base
            await self.kb.store_error_solution(
                error_message=error_log,
                error_context=error_details,
                solution=analysis['root_cause'],
                tenant_id=tenant_id
            )
        else:
            result['auto_fix_applied'] = False
            result['manual_review_required'] = True
            result['reason'] = (
                f"Confidence {analysis['confidence']:.0%} below threshold or "
                f"risk level {analysis['risk_level']} too high"
            )
        
        return result
    
    def _parse_error_log(self, error_log: str) -> Dict:
        """
        Extract structured information from error traceback
        """
        lines = error_log.split('\n')
        
        # Extract error type
        error_type = "Unknown"
        error_message = ""
        for line in reversed(lines):
            if line.strip():
                if ':' in line:
                    parts = line.split(':', 1)
                    error_type = parts[0].strip()
                    error_message = parts[1].strip() if len(parts) > 1 else ""
                break
        
        # Extract file and line number
        file_pattern = r'File "([^"]+)", line (\d+)'
        matches = re.findall(file_pattern, error_log)
        
        files_involved = []
        if matches:
            for file_path, line_num in matches:
                files_involved.append({
                    'file': file_path,
                    'line': int(line_num)
                })
        
        # Extract function/method names
        function_pattern = r'in (\w+)'
        functions = re.findall(function_pattern, error_log)
        
        return {
            'type': error_type,
            'message': error_message,
            'files_involved': files_involved,
            'functions': list(set(functions)),
            'full_traceback': error_log
        }
    
    async def _perform_analysis(
        self,
        error_details: Dict,
        module_name: str,
        context: str
    ) -> Dict:
        """
        Perform deep analysis using Claude
        """
        
        prompt = f"""Analyze this Odoo error and provide a comprehensive solution.

Error Details:
- Type: {error_details['type']}
- Message: {error_details['message']}
- Files: {error_details['files_involved']}
- Functions: {error_details['functions']}
- Module: {module_name}

Full Traceback:
```
{error_details['full_traceback']}
```

Context from similar errors and solutions:
{context}

Provide analysis in JSON format:
{{
    "root_cause": "Clear explanation of what caused the error",
    "affected_components": ["list", "of", "components"],
    "fix_steps": [
        "Step 1: ...",
        "Step 2: ..."
    ],
    "code_changes": [
        {{
            "file": "path/to/file.py",
            "function": "function_name",
            "line_number": 123,
            "old_code": "code to replace",
            "new_code": "corrected code",
            "explanation": "why this change fixes the issue"
        }}
    ],
    "confidence": 0.95,
    "risk_level": "low|medium|high",
    "prevention_tips": [
        "How to prevent this error in the future"
    ]
}}

Important:
1. Be specific with code changes (exact line numbers and code)
2. Consider Odoo API best practices
3. Account for OCA coding standards
4. Assess risk carefully (low = safe to auto-apply)
5. Set confidence based on how clear the solution is"""

        response = await self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse JSON response
        import json
        response_text = response.content[0].text
        
        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        
        return json.loads(response_text)
    
    async def _apply_fixes(
        self,
        module_name: str,
        code_changes: List[Dict],
        tenant_id: Optional[str]
    ) -> Dict:
        """
        Apply code fixes to module files
        """
        logger.info("applying_fixes", module=module_name, changes=len(code_changes))
        
        applied_changes = []
        failed_changes = []
        
        for change in code_changes:
            try:
                file_path = Path(change['file'])
                
                # Read file
                if not file_path.exists():
                    logger.warning("file_not_found", file=str(file_path))
                    failed_changes.append({
                        'change': change,
                        'error': 'File not found'
                    })
                    continue
                
                content = file_path.read_text()
                
                # Apply change
                if change['old_code'] in content:
                    new_content = content.replace(
                        change['old_code'],
                        change['new_code']
                    )
                    
                    # Backup original
                    backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                    file_path.write_text(content)  # Save to backup
                    backup_path.write_text(content)
                    
                    # Write new content
                    file_path.write_text(new_content)
                    
                    applied_changes.append({
                        'file': str(file_path),
                        'backup': str(backup_path),
                        'explanation': change['explanation']
                    })
                    
                    logger.info("fix_applied", file=str(file_path))
                else:
                    logger.warning("code_not_found", file=str(file_path))
                    failed_changes.append({
                        'change': change,
                        'error': 'Old code not found in file'
                    })
            
            except Exception as e:
                logger.error("fix_failed", change=change, error=str(e))
                failed_changes.append({
                    'change': change,
                    'error': str(e)
                })
        
        return {
            'applied': applied_changes,
            'failed': failed_changes,
            'success_rate': len(applied_changes) / len(code_changes) if code_changes else 0
        }
    
    async def optimize_code(
        self,
        file_path: str,
        optimization_goals: List[str] = None
    ) -> Dict:
        """
        Optimize Odoo code for performance, readability, or maintainability
        
        Args:
            file_path: Path to Python file to optimize
            optimization_goals: ['performance', 'readability', 'memory', 'sql']
        
        Returns:
            Optimized code and improvement analysis
        """
        logger.info("optimizing_code", file=file_path)
        
        optimization_goals = optimization_goals or ['performance', 'readability']
        
        # Read current code
        with open(file_path, 'r') as f:
            current_code = f.read()
        
        # Get OCA best practices
        practices = await self.kb.get_oca_best_practices("performance")
        
        prompt = f"""Optimize this Odoo module code.

Current Code:
```python
{current_code}
```

Optimization Goals: {optimization_goals}

OCA Best Practices:
{practices}

Provide:
1. Optimized version of the code
2. List of specific improvements made
3. Performance impact estimate
4. Any trade-offs to consider

Focus on:
- Efficient database queries (avoid N+1 queries)
- Proper use of @api.depends for computed fields
- Batch operations instead of loops
- Appropriate indexes (_sql_constraints)
- Memory-efficient data structures
- Readable, maintainable code structure

Output format:
```json
{{
    "optimized_code": "...",
    "improvements": [
        {{
            "type": "performance|readability|memory",
            "description": "...",
            "impact": "high|medium|low"
        }}
    ],
    "estimated_speedup": "2x faster",
    "tradeoffs": ["any downsides to optimization"]
}}
```"""

        response = await self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=6000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        import json
        response_text = response.content[0].text
        json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        
        result = json.loads(response_text)
        
        return {
            "original_file": file_path,
            "optimized_code": result['optimized_code'],
            "improvements": result['improvements'],
            "estimated_speedup": result.get('estimated_speedup', 'Unknown'),
            "tradeoffs": result.get('tradeoffs', [])
        }
    
    async def review_pull_request(
        self,
        changed_files: List[str],
        diff_content: str
    ) -> Dict:
        """
        Review code changes for quality and potential issues
        
        Args:
            changed_files: List of file paths that changed
            diff_content: Git diff content
        
        Returns:
            Review comments and approval status
        """
        logger.info("reviewing_pr", files_count=len(changed_files))
        
        # Get OCA standards
        standards = await self.kb.get_oca_best_practices("code_review")
        
        prompt = f"""Review this Odoo module code change.

Changed Files: {changed_files}

Diff:
```diff
{diff_content}
```

OCA Review Standards:
{standards}

Check for:
1. Follows OCA naming conventions
2. Proper use of Odoo ORM
3. Security issues (SQL injection, XSS)
4. Performance concerns
5. Missing translations (_() wrapper)
6. Incomplete docstrings
7. Missing tests
8. Breaking changes
9. Database migration needs

Output JSON:
{{
    "approval_status": "approved|needs_changes|rejected",
    "comments": [
        {{
            "file": "path/to/file.py",
            "line": 123,
            "severity": "critical|warning|suggestion",
            "message": "Detailed feedback",
            "suggestion": "Proposed fix if applicable"
        }}
    ],
    "summary": "Overall assessment",
    "checklist": {{
        "oca_compliant": true,
        "security_safe": true,
        "performance_ok": true,
        "tests_included": false
    }}
}}"""

        response = await self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )
        
        import json
        response_text = response.content[0].text
        json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        
        return json.loads(response_text)
