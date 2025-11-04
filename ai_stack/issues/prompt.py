"""Prompt templates and schemas for LLM-backed issue classification."""

ISSUE_CLASSIFICATION_SYSTEM_PROMPT = (
    "You are an InsightPulse automation architect. "
    "Classify GitHub issues into delivery domains and generate structured implementation "
    "details following Odoo best practices."
)

ISSUE_CLASSIFICATION_USER_PROMPT = (
    "Analyse the provided GitHub issue information and respond strictly with JSON that "
    "matches the supplied schema.\n\n"
    "<issue>\n"
    "{issue_body}\n"
    "</issue>\n"
)

ISSUE_CLASSIFICATION_JSON_SCHEMA = {
    "name": "issue_analysis",
    "schema": {
        "type": "object",
        "properties": {
            "domain": {"type": "string"},
            "capabilities": {
                "type": "array",
                "items": {"type": "string"},
                "default": [],
            },
            "dependencies": {
                "type": "array",
                "items": {"type": "string"},
                "default": [],
            },
            "decision": {
                "type": "string",
                "enum": ["odoo_sa", "oca", "ipai"],
                "default": "ipai",
            },
            "area": {
                "type": "string",
                "enum": [
                    "procurement",
                    "expense",
                    "subscriptions",
                    "bi",
                    "ml",
                    "agent",
                    "connector",
                ],
                "default": "connector",
            },
            "acceptance_criteria": {
                "type": "array",
                "items": {"type": "string"},
                "default": [],
            },
        },
        "required": ["domain", "decision", "area"],
        "additionalProperties": False,
    },
}
