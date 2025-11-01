#!/usr/bin/env python3
"""
Generate OCA-compliant Odoo 19.0 modules using DeepSeek API.

DeepSeek is significantly cheaper than Anthropic:
- Input: $0.14 per 1M tokens (vs Claude $3)
- Output: $0.28 per 1M tokens (vs Claude $15)
- Cost per module: ~$0.001 (vs $0.03)
- 100x cheaper than Claude!
"""

import os
import json
import logging
import argparse
from typing import Dict, Any, List
from pathlib import Path

from openai import OpenAI  # DeepSeek uses OpenAI SDK
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Odoo Expert System Prompt
ODOO_EXPERT_PROMPT = """You are an expert Odoo 19.0 module developer with deep knowledge of:
- OCA (Odoo Community Association) coding guidelines
- Philippine BIR compliance (Forms 2550M, 2550Q, 2551M, 2307)
- Multi-agency patterns (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
- Odoo ORM, Security (RLS, ir.model.access, ir.rule), and UI best practices

You MUST follow these principles:
1. OCA Compliance: All code follows OCA guidelines
2. Complete Implementation: No TODO comments, no placeholders
3. BIR Standards: Follow official BIR requirements
4. Security First: Implement proper RLS policies, access rights
5. Testable: Include pytest tests for all business logic
6. Documentation: Complete README.rst with usage examples

CRITICAL: Generate COMPLETE, working code. No shortcuts, no TODOs."""


class DeepSeekOdooGenerator:
    """Generate Odoo modules using DeepSeek API."""

    def __init__(self, api_key: str = None):
        """Initialize DeepSeek client."""
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable required")

        # DeepSeek uses OpenAI SDK with custom base URL
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )

        logger.info("DeepSeek Odoo Generator initialized")

    def generate_module_from_spec(
        self,
        spec: Dict[str, Any],
        odoo_version: str = "19.0",
        model: str = "deepseek-chat"
    ) -> Dict[str, str]:
        """
        Generate complete Odoo module from specification.

        Args:
            spec: Notion page specification with title, content, technical_specs
            odoo_version: Target Odoo version (default: 19.0)
            model: DeepSeek model (deepseek-chat or deepseek-coder)

        Returns:
            Dict mapping file paths to contents
        """
        logger.info(f"Generating module from spec: {spec.get('title', 'Unknown')}")

        # Build generation prompt
        prompt = self._build_generation_prompt(spec, odoo_version)

        # Call DeepSeek API
        logger.info(f"Calling DeepSeek API with model: {model}")
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": ODOO_EXPERT_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=8000,
            temperature=0.0,  # Deterministic for code generation
            stream=False
        )

        # Extract generated code
        response_text = response.choices[0].message.content
        logger.info(f"Received response: {len(response_text)} characters")

        # Log token usage and cost
        usage = response.usage
        cost = self._calculate_cost(usage.prompt_tokens, usage.completion_tokens)
        logger.info(f"Token usage: {usage.prompt_tokens} input + {usage.completion_tokens} output = ${cost:.4f}")

        # Parse generated code into file structure
        files = self._parse_generated_code(response_text)

        logger.info(f"Generated {len(files)} files")
        return files

    def _build_generation_prompt(self, spec: Dict[str, Any], odoo_version: str) -> str:
        """Build prompt for module generation."""
        title = spec.get("title", "Unknown Module")
        content = spec.get("content", "")
        technical_specs = spec.get("technical_specs", "")
        module_type = spec.get("module_type", "custom")
        tags = spec.get("tags", [])

        prompt = f"""Generate a complete, production-ready Odoo {odoo_version} module based on this specification:

**Module Title**: {title}
**Type**: {module_type}
**Tags**: {', '.join(tags)}

**Description**:
{content}

**Technical Specifications**:
{technical_specs}

**Requirements**:
1. Follow OCA coding guidelines strictly
2. Include complete __manifest__.py with proper metadata
3. Implement all models with fields, compute methods, constraints
4. Create XML views (list, form, search)
5. Define security (ir.model.access.csv, RLS rules)
6. Add pytest tests for business logic
7. Include README.rst with usage examples
8. No TODO comments or placeholders - everything must be complete

**Module Structure**:
```
addons/<module_name>/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── <model_files>.py
├── views/
│   └── <view_files>.xml
├── security/
│   ├── ir.model.access.csv
│   └── <security_rules>.xml
├── data/
│   └── <data_files>.xml
├── tests/
│   ├── __init__.py
│   └── test_<features>.py
├── static/description/
│   └── icon.png
└── README.rst
```

Output each file with clear delimiters:

```
===FILE: path/to/file.py===
<file contents>
===END FILE===
```

Generate the complete module now."""

        return prompt

    def _parse_generated_code(self, response_text: str) -> Dict[str, str]:
        """Parse generated code into file structure."""
        files = {}
        current_file = None
        current_content = []

        for line in response_text.split('\n'):
            # Check for file delimiter
            if line.startswith('===FILE:'):
                # Save previous file
                if current_file:
                    files[current_file] = '\n'.join(current_content)

                # Start new file
                current_file = line.replace('===FILE:', '').replace('===', '').strip()
                current_content = []
                logger.debug(f"Found file: {current_file}")

            elif line.startswith('===END FILE==='):
                # Save current file
                if current_file:
                    files[current_file] = '\n'.join(current_content)
                    current_file = None
                    current_content = []

            else:
                # Accumulate file content
                if current_file:
                    current_content.append(line)

        # Save last file if exists
        if current_file:
            files[current_file] = '\n'.join(current_content)

        return files

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate DeepSeek API cost.

        DeepSeek pricing (as of 2025):
        - Input: $0.14 per 1M tokens
        - Output: $0.28 per 1M tokens
        """
        input_cost = (input_tokens / 1_000_000) * 0.14
        output_cost = (output_tokens / 1_000_000) * 0.28
        return input_cost + output_cost

    def save_module(self, files: Dict[str, str], output_dir: Path):
        """Save generated module to disk."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for file_path, content in files.items():
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, 'w') as f:
                f.write(content)

            logger.info(f"Saved: {full_path}")

        logger.info(f"Module saved to: {output_dir}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate OCA-compliant Odoo modules using DeepSeek API"
    )
    parser.add_argument(
        "--spec",
        required=True,
        help="Path to specification JSON file (from fetch_notion_specs.py)"
    )
    parser.add_argument(
        "--output-dir",
        default="addons",
        help="Output directory for generated modules (default: addons)"
    )
    parser.add_argument(
        "--odoo-version",
        default="19.0",
        help="Target Odoo version (default: 19.0)"
    )
    parser.add_argument(
        "--model",
        default="deepseek-chat",
        choices=["deepseek-chat", "deepseek-coder"],
        help="DeepSeek model to use (default: deepseek-chat)"
    )

    args = parser.parse_args()

    # Load specification
    with open(args.spec) as f:
        specs = json.load(f)

    if not isinstance(specs, list):
        specs = [specs]

    # Initialize generator
    generator = DeepSeekOdooGenerator()

    # Generate modules
    total_cost = 0.0
    for spec in specs:
        logger.info(f"Processing: {spec.get('title', 'Unknown')}")

        # Generate module
        files = generator.generate_module_from_spec(
            spec,
            odoo_version=args.odoo_version,
            model=args.model
        )

        # Derive module name from title
        module_name = spec.get("title", "custom_module")
        module_name = module_name.lower().replace(" ", "_")
        module_name = "".join(c for c in module_name if c.isalnum() or c == "_")

        # Save module
        output_path = Path(args.output_dir) / module_name
        generator.save_module(files, output_path)

    logger.info("Module generation complete!")
    logger.info(f"Estimated total cost: ${total_cost:.4f}")


if __name__ == "__main__":
    main()
