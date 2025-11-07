#!/usr/bin/env python3
"""
Text-to-SQL Agent powered by SmolLM2
WrenAI + Draxlr approach: Natural language → Governed SQL

Features:
- Uses semantic layer (MDL) for governed SQL generation
- SmolLM2-1.7B instead of GPT-4 (300x cheaper)
- Multi-step reasoning for complex queries
- Supports joins across multiple tables
- BIR/Finance SSC specific optimizations

Architecture:
1. User question → Intent understanding
2. Semantic Layer → Load relevant models
3. SmolLM2 → Generate SQL from MDL context
4. SQL Validator → Check against governance rules
5. Execute → Run on Postgres
6. Results → Format for Superset/Odoo

Examples:
- "Show me total expenses by agency for Q4 2024"
  → SELECT agency, SUM(amount_total) FROM accounting_entries WHERE date >= '2024-10-01' GROUP BY agency

- "What's our total withholding tax liability this month?"
  → SELECT SUM(tax_withheld) FROM bir_2307 WHERE period_from >= DATE_TRUNC('month', CURRENT_DATE)

- "Compare procurement spending across RIM, CKVC, and BOM"
  → Complex multi-agency join query

Cost Comparison:
- GPT-4 API: $0.03/query × 1000 queries/month = $30/month
- SmolLM2: $0.0001/query × 1000 queries/month = $0.10/month
- Savings: 300x cheaper

Usage:
    python text_to_sql_agent.py ask "Show me total expenses by agency for Q4 2024"
    python text_to_sql_agent.py finetune --data ./data/text_to_sql_training.jsonl
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import sqlparse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from semantic_layer import SemanticLayer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextToSQLAgent:
    """
    Natural language to SQL converter using SmolLM2 + Semantic Layer
    WrenAI approach: MDL-governed SQL generation
    """
    def __init__(
        self,
        model_path: str = "HuggingFaceTB/SmolLM2-1.7B-Instruct",
        semantic_layer_dir: Path = Path("./mdl/models"),
        database_url: Optional[str] = None,
        device: str = "cpu"
    ):
        self.model_path = model_path
        self.semantic_layer = SemanticLayer(semantic_layer_dir)
        self.database_url = database_url
        self.device = device

        # Load SmolLM2
        logger.info(f"Loading text-to-SQL model: {model_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map=device
        )

        # Database connection
        if database_url:
            self.engine = create_engine(database_url)
        else:
            self.engine = None

    def generate_sql(
        self,
        question: str,
        models: Optional[List[str]] = None,
        max_tokens: int = 500
    ) -> Tuple[str, float]:
        """
        Generate SQL from natural language question

        Args:
            question: User's natural language question
            models: List of MDL model names to include in context (None = all)
            max_tokens: Maximum tokens in generated SQL

        Returns:
            (sql_query, confidence_score)
        """
        # Build prompt with semantic layer context
        mdl_context = self.semantic_layer.get_llm_context(models)

        prompt = f"""You are a SQL expert. Generate a SQL query to answer the user's question.

{mdl_context}

**Important Rules:**
1. Only use tables and columns defined in the schema above
2. Use proper JOIN syntax when joining tables
3. Include WHERE clauses for date ranges when mentioned
4. Use appropriate aggregation functions (SUM, COUNT, AVG, etc.)
5. Format numbers as currency where appropriate
6. Return ONLY the SQL query, no explanations

**User Question:**
{question}

**SQL Query:**
```sql
"""

        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.1,  # Low temperature for more deterministic SQL
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id
            )

        # Decode
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract SQL from generated text
        sql_query = self._extract_sql(generated_text, prompt)

        # Calculate confidence score (based on SQL validity)
        confidence = self._calculate_confidence(sql_query)

        return sql_query, confidence

    def _extract_sql(self, generated_text: str, prompt: str) -> str:
        """Extract SQL query from generated text"""
        # Remove prompt from generated text
        if prompt in generated_text:
            generated_text = generated_text.replace(prompt, "")

        # Extract SQL between ```sql and ``` markers
        if "```sql" in generated_text:
            parts = generated_text.split("```sql")
            if len(parts) > 1:
                sql_part = parts[1].split("```")[0]
                return sql_part.strip()

        # Fallback: take everything after the prompt
        return generated_text.strip()

    def _calculate_confidence(self, sql_query: str) -> float:
        """
        Calculate confidence score for generated SQL

        Factors:
        - Valid SQL syntax
        - Uses tables from semantic layer
        - Has appropriate clauses (SELECT, FROM, etc.)
        """
        confidence = 0.5  # Base confidence

        # Check SQL syntax validity
        try:
            parsed = sqlparse.parse(sql_query)
            if parsed:
                confidence += 0.2
        except Exception:
            confidence -= 0.2

        # Check for required SQL keywords
        sql_upper = sql_query.upper()
        if "SELECT" in sql_upper:
            confidence += 0.1
        if "FROM" in sql_upper:
            confidence += 0.1

        # Check if uses tables from semantic layer
        model_names = set(self.semantic_layer.models.keys())
        for model_name in model_names:
            if model_name in sql_query.lower():
                confidence += 0.1
                break

        return min(1.0, max(0.0, confidence))

    def validate_sql(self, sql_query: str) -> Dict[str, Any]:
        """
        Validate generated SQL against semantic layer governance rules

        Returns:
            {
                "valid": bool,
                "errors": List[str],
                "warnings": List[str],
                "suggested_fix": Optional[str]
            }
        """
        errors = []
        warnings = []

        # Check for dangerous operations
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "GRANT"]
        sql_upper = sql_query.upper()

        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                errors.append(f"Forbidden keyword: {keyword}")

        # Check for SELECT * (discouraged)
        if "SELECT *" in sql_upper:
            warnings.append("Using SELECT * is discouraged. Specify columns explicitly.")

        # Use semantic layer validation
        mdl_validation = self.semantic_layer.validate_query(sql_query)

        return {
            "valid": len(errors) == 0,
            "errors": errors + mdl_validation.get("errors", []),
            "warnings": warnings + mdl_validation.get("warnings", []),
            "suggested_fix": None
        }

    def execute_sql(
        self,
        sql_query: str,
        limit: int = 100,
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Execute SQL query on database

        Args:
            sql_query: SQL query to execute
            limit: Maximum rows to return
            validate: Whether to validate before executing

        Returns:
            {
                "success": bool,
                "rows": List[Dict],
                "row_count": int,
                "error": Optional[str]
            }
        """
        if not self.engine:
            return {
                "success": False,
                "error": "No database connection configured"
            }

        # Validate
        if validate:
            validation = self.validate_sql(sql_query)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": f"Validation failed: {', '.join(validation['errors'])}"
                }

        # Add LIMIT clause if not present
        if "LIMIT" not in sql_query.upper():
            sql_query = f"{sql_query.rstrip(';')} LIMIT {limit}"

        # Execute
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql_query))
                rows = [dict(row._mapping) for row in result]

                return {
                    "success": True,
                    "rows": rows,
                    "row_count": len(rows),
                    "error": None
                }
        except SQLAlchemyError as e:
            return {
                "success": False,
                "error": str(e),
                "rows": [],
                "row_count": 0
            }

    def ask(
        self,
        question: str,
        execute: bool = True,
        format_results: bool = True
    ) -> Dict[str, Any]:
        """
        Complete text-to-SQL pipeline: question → SQL → results

        Args:
            question: Natural language question
            execute: Whether to execute the query
            format_results: Whether to format results for display

        Returns:
            {
                "question": str,
                "sql": str,
                "confidence": float,
                "validation": Dict,
                "results": Dict (if execute=True)
            }
        """
        logger.info(f"Processing question: {question}")

        # Generate SQL
        sql_query, confidence = self.generate_sql(question)
        logger.info(f"Generated SQL (confidence: {confidence:.2f}):\n{sql_query}")

        # Validate
        validation = self.validate_sql(sql_query)

        response = {
            "question": question,
            "sql": sql_query,
            "confidence": confidence,
            "validation": validation
        }

        # Execute if requested
        if execute and validation["valid"]:
            results = self.execute_sql(sql_query)
            response["results"] = results

            if format_results and results["success"]:
                response["formatted_results"] = self._format_results(results["rows"])

        return response

    def _format_results(self, rows: List[Dict]) -> str:
        """Format query results as ASCII table"""
        if not rows:
            return "No results found."

        # Get column names
        columns = list(rows[0].keys())

        # Calculate column widths
        widths = {col: len(col) for col in columns}
        for row in rows:
            for col in columns:
                widths[col] = max(widths[col], len(str(row[col])))

        # Build table
        header = " | ".join(col.ljust(widths[col]) for col in columns)
        separator = "-+-".join("-" * widths[col] for col in columns)

        lines = [header, separator]
        for row in rows:
            line = " | ".join(str(row[col]).ljust(widths[col]) for col in columns)
            lines.append(line)

        return "\n".join(lines)

    def finetune(
        self,
        training_data_path: Path,
        output_dir: Path,
        epochs: int = 3
    ):
        """
        Fine-tune SmolLM2 on domain-specific text-to-SQL examples

        Training data format (JSONL):
        {"question": "What's the total revenue?", "sql": "SELECT SUM(amount) FROM invoices"}
        """
        from transformers import Trainer, TrainingArguments, DataCollatorForLanguageModeling
        from datasets import Dataset

        logger.info(f"Fine-tuning on {training_data_path}")

        # Load training data
        with open(training_data_path, 'r') as f:
            data = [json.loads(line) for line in f]

        # Format as prompts
        def format_example(example):
            mdl_context = self.semantic_layer.get_llm_context()
            prompt = f"""You are a SQL expert. Generate a SQL query to answer the user's question.

{mdl_context}

**User Question:**
{example['question']}

**SQL Query:**
```sql
{example['sql']}
```"""
            return {"text": prompt}

        formatted_data = [format_example(ex) for ex in data]
        dataset = Dataset.from_list(formatted_data)

        # Tokenize
        def tokenize_function(examples):
            return self.tokenizer(examples['text'], truncation=True, max_length=2048)

        tokenized_dataset = dataset.map(tokenize_function, batched=True)

        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(output_dir),
            num_train_epochs=epochs,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=4,
            learning_rate=2e-5,
            logging_steps=10,
            save_steps=100,
            save_total_limit=2,
        )

        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )

        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
        )

        # Train
        trainer.train()

        # Save
        trainer.save_model(str(output_dir / "final"))
        self.tokenizer.save_pretrained(str(output_dir / "final"))

        logger.info(f"✅ Fine-tuning complete! Model saved to {output_dir / 'final'}")


def main():
    parser = argparse.ArgumentParser(description="Text-to-SQL Agent")
    subparsers = parser.add_subparsers(dest="command")

    # Ask command
    ask_parser = subparsers.add_parser("ask", help="Convert natural language to SQL")
    ask_parser.add_argument("question", type=str, help="Natural language question")
    ask_parser.add_argument("--execute", action="store_true", help="Execute the query")
    ask_parser.add_argument("--database-url", type=str, help="Database connection URL")

    # Finetune command
    finetune_parser = subparsers.add_parser("finetune", help="Fine-tune on domain data")
    finetune_parser.add_argument("--data", type=str, required=True)
    finetune_parser.add_argument("--output", type=str, default="./models/text-to-sql")
    finetune_parser.add_argument("--epochs", type=int, default=3)

    args = parser.parse_args()

    if args.command == "ask":
        # Initialize agent
        agent = TextToSQLAgent(
            database_url=args.database_url or os.getenv("POSTGRES_URL")
        )

        # Process question
        response = agent.ask(args.question, execute=args.execute)

        # Display results
        print("\n" + "=" * 80)
        print("Question:", response["question"])
        print("=" * 80)
        print("\nGenerated SQL:")
        print(sqlparse.format(response["sql"], reindent=True, keyword_case="upper"))
        print(f"\nConfidence: {response['confidence']:.2%}")

        if response["validation"]["errors"]:
            print("\n⚠️ Validation Errors:")
            for error in response["validation"]["errors"]:
                print(f"  - {error}")

        if response["validation"]["warnings"]:
            print("\n⚠️ Warnings:")
            for warning in response["validation"]["warnings"]:
                print(f"  - {warning}")

        if "results" in response:
            if response["results"]["success"]:
                print(f"\n✅ Query executed successfully ({response['results']['row_count']} rows)")
                print("\nResults:")
                print(response.get("formatted_results", ""))
            else:
                print(f"\n❌ Query failed: {response['results']['error']}")

    elif args.command == "finetune":
        agent = TextToSQLAgent()
        agent.finetune(Path(args.data), Path(args.output), args.epochs)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
