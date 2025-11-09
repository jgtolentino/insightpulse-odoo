#!/usr/bin/env python3
"""
CI Autofix Helper
Extracts errors from GitHub Actions logs and generates fix suggestions using LLM
"""

import os
import re
import sys
import json
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class Error:
    """Represents a CI error"""
    type: str
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    context: Optional[str] = None


class CIAutofixHelper:
    """Helper for extracting CI errors and generating fixes"""

    # Common error patterns for different test frameworks
    ERROR_PATTERNS = [
        # Python errors
        (r"ERROR:(.+?)(?=\n|$)", "python_error"),
        (r"FAILED (.+?) - (.+)", "test_failure"),
        (r"AssertionError:(.+)", "assertion_error"),
        (r"ModuleNotFoundError:(.+)", "import_error"),
        (r"ImportError:(.+)", "import_error"),
        (r"SyntaxError:(.+)", "syntax_error"),
        (r"IndentationError:(.+)", "indentation_error"),
        (r"TypeError:(.+)", "type_error"),
        (r"ValueError:(.+)", "value_error"),
        (r"KeyError:(.+)", "key_error"),
        (r"AttributeError:(.+)", "attribute_error"),

        # Linting errors
        (r"([A-Z]\d{3,4}):(.+)", "lint_error"),
        (r"pylint:(.+?):\d+:\d+:(.+)", "pylint_error"),
        (r"flake8:(.+?):\d+:\d+:(.+)", "flake8_error"),

        # Odoo specific errors
        (r"odoo\.exceptions\.(.+?):(.+)", "odoo_error"),
        (r"ParseError:(.+)", "odoo_parse_error"),
        (r"ValidationError:(.+)", "odoo_validation_error"),

        # Docker/deployment errors
        (r"Error response from daemon:(.+)", "docker_error"),
        (r"FATAL:(.+)", "fatal_error"),
    ]

    def __init__(self, github_token: Optional[str] = None, openai_api_key: Optional[str] = None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')

    def extract_errors(self, logs: str) -> List[Error]:
        """Extract errors from CI logs"""
        errors = []

        for pattern, error_type in self.ERROR_PATTERNS:
            matches = re.finditer(pattern, logs, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                error = Error(
                    type=error_type,
                    message=match.group(0).strip(),
                    file=self._extract_file_from_error(match.group(0)),
                    line=self._extract_line_from_error(match.group(0)),
                )
                errors.append(error)

        # Deduplicate errors
        unique_errors = []
        seen = set()
        for error in errors:
            key = (error.type, error.message, error.file, error.line)
            if key not in seen:
                seen.add(key)
                unique_errors.append(error)

        return unique_errors

    def _extract_file_from_error(self, error_msg: str) -> Optional[str]:
        """Extract file path from error message"""
        # Common patterns: "File 'path/to/file.py'" or "path/to/file.py:123"
        patterns = [
            r"File ['\"]([^'\"]+)['\"]",
            r"([a-zA-Z0-9_/\-\.]+\.py):\d+",
            r"in ([a-zA-Z0-9_/\-\.]+\.py)",
        ]

        for pattern in patterns:
            match = re.search(pattern, error_msg)
            if match:
                return match.group(1)
        return None

    def _extract_line_from_error(self, error_msg: str) -> Optional[int]:
        """Extract line number from error message"""
        # Pattern: "file.py:123" or "line 123"
        patterns = [
            r":(\d+):",
            r"line (\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, error_msg)
            if match:
                return int(match.group(1))
        return None

    def generate_fix_prompt(self, errors: List[Error], workflow_name: str, repo: str) -> str:
        """Generate prompt for LLM to fix errors"""
        prompt = f"""# CI Failure Autofix Request

**Workflow**: {workflow_name}
**Repository**: {repo}
**Total Errors**: {len(errors)}

## Errors Found

"""
        for idx, error in enumerate(errors, 1):
            prompt += f"""### Error {idx}: {error.type}

```
{error.message}
```

"""
            if error.file:
                prompt += f"**File**: `{error.file}`\n"
            if error.line:
                prompt += f"**Line**: {error.line}\n"
            prompt += "\n"

        prompt += """## Task

Please analyze these CI errors and provide:

1. **Root Cause Analysis**: What is causing each error?
2. **Recommended Fix**: Specific code changes to fix each error
3. **Prevention**: How to prevent similar errors in the future

**Requirements**:
- Fix only the immediate cause of the error
- Don't refactor unrelated code
- Preserve existing functionality
- Add comments explaining the fix
- If multiple errors are related, fix them together

**Output Format**:

For each error, provide:
- Root cause explanation
- Specific file changes (with line numbers)
- Any additional steps needed (e.g., install dependencies)

"""
        return prompt

    def call_openai(self, prompt: str) -> str:
        """Call OpenAI API to generate fix"""
        if not self.openai_api_key:
            return "ERROR: OPENAI_API_KEY not set. Cannot generate fix suggestions."

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert software engineer specializing in debugging CI/CD failures, Python, Odoo, and DevOps. Provide concise, actionable fixes."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000,
                },
                timeout=30,
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"ERROR: OpenAI API returned {response.status_code}: {response.text}"

        except Exception as e:
            return f"ERROR calling OpenAI API: {str(e)}"

    def create_issue_body(self, errors: List[Error], fix_suggestion: str,
                         workflow_name: str, run_id: int, run_url: str) -> str:
        """Create GitHub issue body with error details and fix suggestions"""
        body = f"""## 🤖 CI Autofix Assistant

**Workflow**: {workflow_name}
**Run ID**: {run_id}
**Run URL**: {run_url}

---

## ❌ Errors Detected ({len(errors)})

"""
        for idx, error in enumerate(errors, 1):
            body += f"""### {idx}. {error.type}

```
{error.message}
```

"""
            if error.file:
                body += f"- **File**: `{error.file}`\n"
            if error.line:
                body += f"- **Line**: {error.line}\n"
            body += "\n"

        body += f"""---

## 💡 Suggested Fix

{fix_suggestion}

---

## 🔧 How to Apply

1. Review the suggested fixes above
2. Apply the changes manually or create a PR
3. Re-run the workflow to verify the fix

---

**Labels**: `ci-failure`, `autofix`, `needs-review`

**Created by**: CI Autofix Bot
**Timestamp**: {self._get_timestamp()}
"""
        return body

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


def main():
    """Main entry point for CLI usage"""
    if len(sys.argv) < 2:
        print("Usage: python ci-autofix-helper.py <log_file_or_url>")
        print("Environment variables:")
        print("  GITHUB_TOKEN - GitHub personal access token")
        print("  OPENAI_API_KEY - OpenAI API key")
        sys.exit(1)

    log_source = sys.argv[1]

    # Read logs
    if log_source.startswith('http'):
        # Download from URL
        response = requests.get(log_source)
        logs = response.text
    else:
        # Read from file
        with open(log_source, 'r') as f:
            logs = f.read()

    # Extract errors
    helper = CIAutofixHelper()
    errors = helper.extract_errors(logs)

    print(f"📊 Found {len(errors)} errors")
    print(json.dumps([asdict(e) for e in errors], indent=2))

    # Generate fix
    if os.getenv('GENERATE_FIX') == 'true':
        workflow_name = os.getenv('WORKFLOW_NAME', 'Unknown')
        repo = os.getenv('GITHUB_REPOSITORY', 'unknown/repo')

        prompt = helper.generate_fix_prompt(errors, workflow_name, repo)
        print("\n📝 Generated prompt:")
        print(prompt)

        print("\n🤖 Calling OpenAI to generate fix...")
        fix = helper.call_openai(prompt)
        print("\n💡 Suggested fix:")
        print(fix)


if __name__ == "__main__":
    main()
