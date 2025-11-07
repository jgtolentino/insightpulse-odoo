"""
WrenAI-Style Semantic Layer (MDL - Modeling Definition Language)
Defines business logic, metrics, and relationships for LLM-powered analytics

Philosophy (from WrenAI):
- Don't expose raw schemas to LLMs
- Encode schema, metrics, joins in semantic models
- Maintain data governance while generating SQL
- Enable natural language → governed SQL transformation

Use Cases:
- Finance SSC: "Show me total expenses by agency for Q4 2024"
- BIR Compliance: "What's our total withholding tax liability this month?"
- Multi-Agency: "Compare procurement spending across RIM, CKVC, and BOM"

Architecture:
1. MDL Schema → defines tables, columns, relationships
2. Semantic Layer → exposes governed metrics and dimensions
3. Text-to-SQL Agent → SmolLM2 generates SQL from MDL
4. Superset Integration → renders charts/dashboards

References:
- WrenAI: https://github.com/Canner/WrenAI
- Tableau LangChain: https://github.com/tableau/tableau_langchain
- Cube.js semantic layer: https://cube.dev/docs/schema/fundamentals
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import yaml


class DataType(Enum):
    """MDL data types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DECIMAL = "decimal"
    DATE = "date"
    DATETIME = "datetime"
    BOOLEAN = "boolean"


class AggregationType(Enum):
    """SQL aggregation functions"""
    SUM = "sum"
    COUNT = "count"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT_DISTINCT = "count_distinct"


@dataclass
class Column:
    """MDL Column definition"""
    name: str
    description: str
    data_type: DataType
    primary_key: bool = False
    nullable: bool = True

    # Business metadata
    display_name: Optional[str] = None
    business_definition: Optional[str] = None

    # Governance
    pii: bool = False  # Personally Identifiable Information
    restricted: bool = False  # Requires special permissions


@dataclass
class Relationship:
    """MDL Relationship (join) definition"""
    name: str
    type: str  # one_to_one, one_to_many, many_to_many
    from_table: str
    from_column: str
    to_table: str
    to_column: str


@dataclass
class Metric:
    """MDL Metric definition (calculated field)"""
    name: str
    description: str
    sql: str  # SQL expression
    aggregation: AggregationType
    format: str  # e.g., "currency", "percentage", "number"

    # Business metadata
    display_name: Optional[str] = None
    business_definition: Optional[str] = None


@dataclass
class Model:
    """MDL Model (table/view) definition"""
    name: str
    description: str
    table_name: str  # Physical table name in database
    schema: str  # Database schema (e.g., "public", "finance")

    columns: List[Column]
    relationships: List[Relationship]
    metrics: List[Metric]

    # Business metadata
    display_name: Optional[str] = None
    business_definition: Optional[str] = None
    owner: Optional[str] = None  # Team/person responsible

    # Governance
    row_level_security: Optional[str] = None  # SQL WHERE clause for RLS


class SemanticLayer:
    """
    Semantic Layer Manager
    Loads MDL definitions and exposes them for LLM consumption
    """
    def __init__(self, models_dir: Path):
        self.models_dir = models_dir
        self.models: Dict[str, Model] = {}
        self._load_models()

    def _load_models(self):
        """Load all MDL YAML files from models directory"""
        for yaml_file in self.models_dir.glob("*.yaml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                model = self._parse_model(data)
                self.models[model.name] = model

    def _parse_model(self, data: Dict) -> Model:
        """Parse MDL YAML into Model object"""
        columns = [
            Column(
                name=col['name'],
                description=col.get('description', ''),
                data_type=DataType(col['data_type']),
                primary_key=col.get('primary_key', False),
                nullable=col.get('nullable', True),
                display_name=col.get('display_name'),
                business_definition=col.get('business_definition'),
                pii=col.get('pii', False),
                restricted=col.get('restricted', False)
            )
            for col in data.get('columns', [])
        ]

        relationships = [
            Relationship(
                name=rel['name'],
                type=rel['type'],
                from_table=rel['from_table'],
                from_column=rel['from_column'],
                to_table=rel['to_table'],
                to_column=rel['to_column']
            )
            for rel in data.get('relationships', [])
        ]

        metrics = [
            Metric(
                name=metric['name'],
                description=metric.get('description', ''),
                sql=metric['sql'],
                aggregation=AggregationType(metric['aggregation']),
                format=metric.get('format', 'number'),
                display_name=metric.get('display_name'),
                business_definition=metric.get('business_definition')
            )
            for metric in data.get('metrics', [])
        ]

        return Model(
            name=data['name'],
            description=data.get('description', ''),
            table_name=data['table_name'],
            schema=data.get('schema', 'public'),
            columns=columns,
            relationships=relationships,
            metrics=metrics,
            display_name=data.get('display_name'),
            business_definition=data.get('business_definition'),
            owner=data.get('owner'),
            row_level_security=data.get('row_level_security')
        )

    def get_model(self, name: str) -> Optional[Model]:
        """Get model by name"""
        return self.models.get(name)

    def get_llm_context(self, model_names: Optional[List[str]] = None) -> str:
        """
        Generate LLM context for text-to-SQL
        Returns formatted schema description for prompt engineering
        """
        if model_names is None:
            models_to_include = self.models.values()
        else:
            models_to_include = [self.models[name] for name in model_names if name in self.models]

        context = "# Database Schema\n\n"

        for model in models_to_include:
            context += f"## {model.display_name or model.name}\n"
            context += f"{model.business_definition or model.description}\n\n"
            context += f"**Table**: `{model.schema}.{model.table_name}`\n\n"

            # Columns
            context += "**Columns**:\n"
            for col in model.columns:
                pk_marker = " (PRIMARY KEY)" if col.primary_key else ""
                context += f"- `{col.name}` ({col.data_type.value}){pk_marker}: {col.business_definition or col.description}\n"

            context += "\n"

            # Relationships
            if model.relationships:
                context += "**Relationships**:\n"
                for rel in model.relationships:
                    context += f"- {rel.name}: `{rel.from_table}.{rel.from_column}` → `{rel.to_table}.{rel.to_column}` ({rel.type})\n"
                context += "\n"

            # Metrics
            if model.metrics:
                context += "**Metrics**:\n"
                for metric in model.metrics:
                    context += f"- {metric.display_name or metric.name}: {metric.business_definition or metric.description}\n"
                    context += f"  ```sql\n  {metric.sql}\n  ```\n"
                context += "\n"

            context += "---\n\n"

        return context

    def validate_query(self, sql: str) -> Dict[str, Any]:
        """
        Validate generated SQL against MDL
        Checks for:
        - Only uses tables/columns defined in MDL
        - Respects row-level security
        - No PII access without proper permissions
        """
        # Placeholder: implement SQL parsing and validation
        return {"valid": True, "warnings": [], "errors": []}

    def export_dbt_models(self, output_dir: Path):
        """
        Export MDL as dbt models
        Enables integration with dbt semantic layer
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        for model in self.models.values():
            dbt_model = {
                "version": 2,
                "models": [{
                    "name": model.name,
                    "description": model.description,
                    "columns": [
                        {
                            "name": col.name,
                            "description": col.description,
                            "data_type": col.data_type.value,
                            "meta": {
                                "pii": col.pii,
                                "restricted": col.restricted
                            }
                        }
                        for col in model.columns
                    ],
                    "meta": {
                        "owner": model.owner,
                        "business_definition": model.business_definition
                    }
                }]
            }

            output_path = output_dir / f"{model.name}.yaml"
            with open(output_path, 'w') as f:
                yaml.dump(dbt_model, f, default_flow_style=False)


# ============================================================================
# Example MDL Definitions
# ============================================================================

def create_example_mdl_files(output_dir: Path):
    """Create example MDL files for Finance SSC and BIR compliance"""

    output_dir.mkdir(parents=True, exist_ok=True)

    # Finance SSC - Accounting Entries
    accounting_entries = {
        "name": "accounting_entries",
        "display_name": "Accounting Journal Entries",
        "description": "General ledger journal entries for multi-agency accounting",
        "business_definition": "All accounting transactions recorded in the system, supporting RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB agencies",
        "table_name": "account_move",
        "schema": "public",
        "owner": "Finance SSC Team",
        "row_level_security": "agency_id IN (SELECT agency_id FROM user_agency_access WHERE user_id = current_user_id())",
        "columns": [
            {
                "name": "id",
                "description": "Unique identifier for journal entry",
                "data_type": "integer",
                "primary_key": True
            },
            {
                "name": "name",
                "display_name": "Entry Number",
                "description": "Journal entry reference number",
                "business_definition": "Sequential reference number for tracking entries",
                "data_type": "string"
            },
            {
                "name": "date",
                "display_name": "Entry Date",
                "description": "Date of journal entry",
                "data_type": "date"
            },
            {
                "name": "journal_id",
                "display_name": "Journal",
                "description": "Reference to journal type (Sales, Purchase, Bank, etc.)",
                "data_type": "integer"
            },
            {
                "name": "state",
                "display_name": "Status",
                "description": "Entry state: draft, posted, cancel",
                "data_type": "string"
            },
            {
                "name": "amount_total",
                "display_name": "Total Amount",
                "description": "Total amount of journal entry",
                "business_definition": "Sum of all debit or credit lines",
                "data_type": "decimal"
            },
            {
                "name": "agency_id",
                "display_name": "Agency",
                "description": "Multi-agency identifier (RIM, CKVC, BOM, etc.)",
                "data_type": "integer",
                "restricted": True
            }
        ],
        "relationships": [
            {
                "name": "journal",
                "type": "many_to_one",
                "from_table": "accounting_entries",
                "from_column": "journal_id",
                "to_table": "account_journal",
                "to_column": "id"
            },
            {
                "name": "agency",
                "type": "many_to_one",
                "from_table": "accounting_entries",
                "from_column": "agency_id",
                "to_table": "agencies",
                "to_column": "id"
            }
        ],
        "metrics": [
            {
                "name": "total_entries",
                "display_name": "Total Journal Entries",
                "description": "Count of all journal entries",
                "business_definition": "Number of journal entries recorded in the period",
                "sql": "COUNT(DISTINCT id)",
                "aggregation": "count",
                "format": "number"
            },
            {
                "name": "total_amount",
                "display_name": "Total Amount",
                "description": "Sum of all journal entry amounts",
                "business_definition": "Total monetary value of all entries",
                "sql": "SUM(amount_total)",
                "aggregation": "sum",
                "format": "currency"
            },
            {
                "name": "avg_entry_amount",
                "display_name": "Average Entry Amount",
                "description": "Average amount per journal entry",
                "sql": "AVG(amount_total)",
                "aggregation": "avg",
                "format": "currency"
            }
        ]
    }

    with open(output_dir / "accounting_entries.yaml", 'w') as f:
        yaml.dump(accounting_entries, f, default_flow_style=False)

    # BIR Form 2307 - Withholding Tax Certificates
    bir_2307 = {
        "name": "bir_2307",
        "display_name": "BIR Form 2307 (Withholding Tax Certificates)",
        "description": "Certificate of Creditable Tax Withheld at Source",
        "business_definition": "Philippine BIR Form 2307 for withholding tax compliance",
        "table_name": "bir_form_2307",
        "schema": "bir",
        "owner": "Compliance Team",
        "columns": [
            {
                "name": "id",
                "description": "Unique identifier",
                "data_type": "integer",
                "primary_key": True
            },
            {
                "name": "certificate_number",
                "display_name": "Certificate Number",
                "description": "BIR 2307 certificate number",
                "data_type": "string"
            },
            {
                "name": "payor_tin",
                "display_name": "Payor TIN",
                "description": "Tax Identification Number of payor",
                "business_definition": "Philippine TIN format XXX-XXX-XXX-XXX",
                "data_type": "string",
                "pii": True
            },
            {
                "name": "payee_tin",
                "display_name": "Payee TIN",
                "description": "Tax Identification Number of payee",
                "data_type": "string",
                "pii": True
            },
            {
                "name": "income_payment",
                "display_name": "Income Payment",
                "description": "Total income payment subject to withholding",
                "data_type": "decimal"
            },
            {
                "name": "tax_withheld",
                "display_name": "Tax Withheld",
                "description": "Amount of tax withheld",
                "business_definition": "Withholding tax amount (typically 1-2% for services)",
                "data_type": "decimal"
            },
            {
                "name": "period_from",
                "display_name": "Period From",
                "description": "Start date of withholding period",
                "data_type": "date"
            },
            {
                "name": "period_to",
                "display_name": "Period To",
                "description": "End date of withholding period",
                "data_type": "date"
            }
        ],
        "metrics": [
            {
                "name": "total_tax_withheld",
                "display_name": "Total Tax Withheld",
                "description": "Sum of all withholding tax",
                "business_definition": "Total withholding tax liability for the period",
                "sql": "SUM(tax_withheld)",
                "aggregation": "sum",
                "format": "currency"
            },
            {
                "name": "total_income_payments",
                "display_name": "Total Income Payments",
                "description": "Sum of all income payments subject to withholding",
                "sql": "SUM(income_payment)",
                "aggregation": "sum",
                "format": "currency"
            },
            {
                "name": "effective_withholding_rate",
                "display_name": "Effective Withholding Rate",
                "description": "Average withholding tax rate",
                "business_definition": "Tax withheld as percentage of income payments",
                "sql": "SUM(tax_withheld) / NULLIF(SUM(income_payment), 0) * 100",
                "aggregation": "avg",
                "format": "percentage"
            }
        ]
    }

    with open(output_dir / "bir_2307.yaml", 'w') as f:
        yaml.dump(bir_2307, f, default_flow_style=False)

    print(f"✅ Created example MDL files in {output_dir}")


if __name__ == "__main__":
    # Create example MDL files
    mdl_dir = Path("./mdl/models")
    create_example_mdl_files(mdl_dir)

    # Load semantic layer
    semantic_layer = SemanticLayer(mdl_dir)

    # Generate LLM context for text-to-SQL
    llm_context = semantic_layer.get_llm_context()
    print("\n" + "=" * 80)
    print("LLM Context for Text-to-SQL")
    print("=" * 80)
    print(llm_context)

    # Export as dbt models
    dbt_dir = Path("./mdl/dbt")
    semantic_layer.export_dbt_models(dbt_dir)
    print(f"\n✅ Exported dbt models to {dbt_dir}")
