# MCP Deep Research Pattern

## Overview

Multi-hop RAG over InsightPulse codebase, logs, and documentation. Implements the "deep research" pattern from OpenAI Cookbook adapted for our stack.

## Target Repo

`pulser-copilot` (MCP server)

## Pattern

```
User Query
    ↓
Plan Research (identify what to gather)
    ↓
Parallel Gather (search code, logs, docs)
    ↓
Cluster by Theme (group related sources)
    ↓
Summarize Each Cluster
    ↓
Synthesize Final Answer (with citations)
```

## Implementation

### Tool Structure

```python
# pulser-copilot/src/tools/deep_research_repo.py

class DeepResearchRepoTool:
    """Multi-hop RAG over InsightPulse repos"""

    async def research(self, query: str) -> ResearchResult:
        # Step 1: Plan
        plan = await self.create_research_plan(query)

        # Step 2: Parallel gather
        sources = await asyncio.gather(
            self.search_odoo_modules(plan.keywords),
            self.search_ipai_bot_logs(plan.keywords),
            self.search_workspace_docs(plan.keywords),
            self.search_github_issues(plan.keywords),
        )

        # Step 3: Cluster
        clusters = self.cluster_by_theme(sources)

        # Step 4: Synthesize
        return self.synthesize_answer(clusters, query)

    async def create_research_plan(self, query: str) -> ResearchPlan:
        """Use LLM to create research plan"""
        prompt = f"""
        Create a research plan for this query: {query}

        Return JSON:
        {{
          "keywords": ["keyword1", "keyword2"],
          "search_areas": ["odoo_modules", "logs", "docs"],
          "depth": "shallow|medium|deep"
        }}
        """
        ...

    def cluster_by_theme(self, sources: List[Source]) -> List[Cluster]:
        """Group sources by theme using embeddings"""
        # Generate embeddings for each source
        embeddings = self.embed_sources(sources)

        # Cluster using k-means or hierarchical
        clusters = self.kmeans_cluster(embeddings, n_clusters=5)

        return clusters
```

### MCP Tool Registration

```json
{
  "mcpServers": {
    "pulser-copilot": {
      "command": "python",
      "args": ["-m", "pulser_copilot.mcp_server"],
      "tools": [
        "deep_research_repo",
        "deep_research_ocr",
        "deep_research_finance"
      ]
    }
  }
}
```

### Usage Example

```python
# From Claude Desktop or CLI
result = await mcp_client.call_tool(
    "deep_research_repo",
    {
        "query": "How does multi-agency consolidation work?"
    }
)

# Returns:
{
  "answer": "Multi-agency consolidation...",
  "sources": [
    {
      "file": "odoo/addons/multi_agency_consolidation/models/consolidation.py",
      "line": 145,
      "excerpt": "..."
    }
  ],
  "confidence": 0.92
}
```

## Behavior Contract

1. **Always cite sources** with file paths and line numbers
2. **Confidence scoring** for each claim (0-1 scale)
3. **Multi-hop**: Follow references up to 3 levels deep
4. **Graceful degradation** when sources are sparse
5. **No hallucinations**: If uncertain, say "I don't have enough information"

## Eval Criteria

```yaml
# pulser-copilot/evals/deep_research.yaml

test_cases:
  - query: "How does 1601-C validation work?"
    expected_sources:
      - path_contains: "bir_forms"
      - path_contains: "validation"
    expected_answer_contains:
      - "ATC codes"
      - "withholding tax"
    confidence_threshold: 0.8

  - query: "What's the month-end closing procedure?"
    expected_sources:
      - path_contains: "account_closing"
    behavioral:
      - "Must cite PLANS.md if it contains relevant info"
      - "Should mention Finance SSC if applicable"
```

## Directory Structure

```
pulser-copilot/
├── src/
│   └── tools/
│       ├── deep_research_repo.py       (main implementation)
│       ├── deep_research_ocr.py        (BIR PDFs)
│       └── deep_research_finance.py    (SSC procedures)
├── prompts/
│   └── deep_research_template.jinja2
└── evals/
    └── deep_research.yaml
```

## Cost Estimate

- Planning: ~500 tokens ($0.0005)
- Clustering: ~2000 tokens ($0.002)
- Synthesis: ~3000 tokens ($0.003)
- **Total per query**: ~$0.006

## Next Steps

1. Implement `create_research_plan()`
2. Add Supabase pgvector integration for ODoo code
3. Create clustering logic
4. Build synthesis prompt
5. Add evals with 10+ test cases
