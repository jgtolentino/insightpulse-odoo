# Agent Stack Research: High-Leverage Repositories

**Date**: 2025-11-11
**Session**: claude/agent-stack-research-011CV1dAYYS6K4F2jVncJt3Z
**Purpose**: Curated vendor-friendly repo list for InsightPulse agentic infrastructure

---

## 1. Agent Frameworks & Orchestration

### LangGraph
**Start here, not raw LangChain**
- **Repo**: https://github.com/langchain-ai/langgraph
- **Why**: Stateful, checkpointed agents with graph-based execution
- **Use case**: Multi-step agent workflows with state persistence
- **Integration priority**: **HIGH** - Core orchestration layer

### Microsoft AutoGen
- **Repo**: https://github.com/microsoft/autogen
- **Why**: Mature multi-agent patterns, excellent docs, still maintained alongside Agent Framework
- **Use case**: Conversational multi-agent systems, agent-to-agent communication
- **Integration priority**: **MEDIUM** - Alternative orchestration pattern

### Semantic Kernel
- **Repo**: https://github.com/microsoft/semantic-kernel
- **Why**: Model-agnostic agent SDK (.NET/Python/Java) with enterprise samples
- **Use case**: Cross-platform agent development, enterprise integrations
- **Integration priority**: **LOW** - Evaluate if .NET/Java agents needed

### CrewAI
- **Repo**: https://github.com/crewAIInc/crewAI
- **Why**: Lightweight multi-agent execution, independent of LangChain
- **Use case**: Simple multi-agent orchestration without heavy dependencies
- **Integration priority**: **HIGH** - Lightweight alternative to LangGraph

### Model Context Protocol (MCP)
- **Repo**: https://github.com/modelcontextprotocol
- **Why**: Standardize tool/context access across IDEs & apps
- **Use case**: Unified tool discovery for Claude Code, Cursor, other IDEs
- **Integration priority**: **CRITICAL** - Foundation for tool ecosystem

---

## 2. Data/RAG Layer for Agents

### LlamaIndex
- **Repo**: https://github.com/run-llama/llama_index
- **Why**: Composable data connectors and agents over custom corpora
- **Use case**: RAG over Odoo data, financial documents, BIR forms
- **Integration priority**: **HIGH** - Primary RAG framework

### deepset Haystack
- **Repo**: https://github.com/deepset-ai/haystack
- **Why**: Production RAG pipelines with tool nodes
- **Use case**: Alternative to LlamaIndex, strong pipeline abstractions
- **Integration priority**: **LOW** - Track but prefer LlamaIndex initially

---

## 3. Dev-Agent Platforms (Code Execution)

### OpenHands (formerly OpenDevin)
- **Repo**: https://github.com/OpenHands/OpenHands
- **Why**: OSS software dev agent that executes tasks end-to-end
- **Use case**: Autonomous code generation, PR creation, test writing
- **Integration priority**: **MEDIUM** - Gate behind staging, evaluate safety

---

## 4. Visual Builders / Low-Code Agent Ops

### Dify
- **Repo**: https://github.com/langgenius/dify
- **Why**: Agentic workflow builder, plugins, model management; huge velocity
- **Use case**: No-code agent workflows, rapid prototyping
- **Integration priority**: **LOW** - Extract example patterns only

### Flowise
- **Repo**: https://github.com/FlowiseAI/Flowise
- **Why**: Node/graph builder for agents & RAG with SDK + docs
- **Use case**: Visual RAG/agent debugging, flow visualization
- **Integration priority**: **LOW** - Extract example patterns only

---

## 5. Evals, Tracing, Observability

### Arize Phoenix
- **Repo**: https://github.com/Arize-ai/phoenix
- **Why**: Open-source LLM tracing + eval with excellent dashboards & OTEL
- **Use case**: Production agent monitoring, trace debugging
- **Integration priority**: **CRITICAL** - Primary observability platform

### TruLens
- **Repo**: https://github.com/truera/trulens
- **Why**: Evals & feedback functions, integrates with LangChain, great for agents/RAG QA
- **Use case**: RAG quality metrics, agent decision evaluation
- **Integration priority**: **HIGH** - Complement Phoenix with eval metrics

### DeepEval (Confident AI)
- **Repo**: https://github.com/confident-ai/deepeval
- **Why**: pytest-style LLM tests + 40+ metrics (hallucination, RAGAS, etc.)
- **Use case**: CI-based agent testing, regression detection
- **Integration priority**: **HIGH** - CI/CD quality gates

---

## 6. Anthropic Ecosystem

### Anthropic Skills
- **Repo**: https://github.com/anthropics/skills
- **Why**: Public Skills catalog, vendor locally as subtree input
- **Use case**: Pre-built Claude Code skills, integration patterns
- **Integration priority**: **HIGH** - Already using, vendor examples

### Claude Cookbooks
- **Repo**: https://github.com/anthropics/claude-cookbooks
- **Why**: Practical Claude recipes beyond Skills repo
- **Use case**: Advanced prompting patterns, tool use examples
- **Integration priority**: **MEDIUM** - Reference documentation

---

## 7. OpenAI Ecosystem

### OpenAI Cookbook
- **Repo**: https://github.com/openai/openai-cookbook
- **Why**: Definitive example bank for OpenAI API
- **Use case**: Cross-vendor patterns, embedding/RAG examples
- **Integration priority**: **MEDIUM** - Reference documentation

---

## Integration Strategy

### 1. Vendor via `git subtree`
**Target repos** (selective vendoring):
```bash
# Core frameworks
git subtree add --prefix=vendor/langgraph \
  https://github.com/langchain-ai/langgraph.git main --squash

git subtree add --prefix=vendor/autogen \
  https://github.com/microsoft/autogen.git main --squash

git subtree add --prefix=vendor/crewai \
  https://github.com/crewAIInc/crewAI.git main --squash

# Anthropic ecosystem
git subtree add --prefix=vendor/anthropic-skills \
  https://github.com/anthropics/skills.git main --squash

git subtree add --prefix=vendor/claude-cookbooks \
  https://github.com/anthropics/claude-cookbooks.git main --squash

# Evals (selective examples)
git subtree add --prefix=vendor/phoenix-examples \
  https://github.com/Arize-ai/phoenix.git main --squash

git subtree add --prefix=vendor/trulens-examples \
  https://github.com/truera/trulens.git main --squash
```

**Benefits**:
- CI has fixtures without external network calls
- Auditable dependency history in git log
- Selective updates via `git subtree pull`

### 2. Pin evals with Phoenix + TruLens
**GitHub Actions workflow** (`.github/workflows/agent-eval.yml`):
```yaml
name: Agent Evaluation
on: [pull_request]
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Phoenix tracing
        run: |
          python scripts/eval/phoenix_trace.py \
            --pr ${{ github.event.pull_request.number }}
      - name: Run TruLens metrics
        run: |
          python scripts/eval/trulens_score.py \
            --metrics context_relevancy,groundedness,tool_accuracy
      - name: Post eval report
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              body: 'Agent Eval Results:\n' + evalResults
            })
```

**Metrics tracked**:
- Context relevancy (RAG precision)
- Groundedness (hallucination detection)
- Tool-call accuracy (agent decision quality)

### 3. Adopt MCP
**Directory structure**:
```
/mcp/
  servers/
    file/           # Local file system access
    http/           # HTTP API wrapper
    supabase/       # Supabase MCP server
    odoo/           # Odoo XML-RPC → MCP bridge
  discovery.json    # MCP server registry
  README.md         # Setup instructions
```

**discovery.json** (MCP server manifest):
```json
{
  "servers": [
    {
      "name": "insightpulse-supabase",
      "command": "uvx",
      "args": ["mcp-server-supabase"],
      "env": {
        "SUPABASE_URL": "${SUPABASE_URL}",
        "SUPABASE_KEY": "${SUPABASE_KEY}"
      }
    },
    {
      "name": "insightpulse-odoo",
      "command": "python",
      "args": ["-m", "mcp.servers.odoo"],
      "env": {
        "ODOO_URL": "https://erp.insightpulseai.net",
        "ODOO_DB": "odoo19",
        "ODOO_USER": "${ODOO_USER}",
        "ODOO_PASSWORD": "${ODOO_PASSWORD}"
      }
    }
  ]
}
```

**Benefits**:
- Claude Code auto-discovers tools
- Standardized tool interface across IDEs
- Easy to add new tool servers

### 4. Dev-agent sandbox with OpenHands
**Gating strategy**:
- Run OpenHands tasks in isolated Docker containers
- Limit to staging branch PRs only
- Require manual approval for production merges
- Log all agent actions to audit trail

**GitHub Actions workflow** (`.github/workflows/openhands-sandbox.yml`):
```yaml
name: OpenHands Dev Agent
on:
  workflow_dispatch:
    inputs:
      task:
        description: 'Task for OpenHands agent'
        required: true
jobs:
  sandbox:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/staging'
    steps:
      - uses: actions/checkout@v4
      - name: Run OpenHands
        run: |
          docker run --rm \
            -v $(pwd):/workspace \
            openhands/openhands:latest \
            --task "${{ github.event.inputs.task }}" \
            --workspace /workspace
```

---

## Ready-to-Commit Bundle

### What's included:
1. **Vendored subtrees** for core frameworks (LangGraph, CrewAI, Anthropic Skills)
2. **MCP discovery** structure with Supabase + Odoo servers
3. **Phoenix/TruLens eval jobs** in GitHub Actions
4. **Example agents** in `agents/examples/`:
   - `agents/examples/langgraph/finance_workflow.py` - Multi-step finance automation
   - `agents/examples/crewai/bir_filing_crew.py` - BIR filing agent crew
   - `agents/examples/mcp/odoo_bridge.py` - MCP-based Odoo tool use

### Proposed directory structure:
```
/home/user/insightpulse-odoo/
  vendor/
    langgraph/          # Subtree: LangGraph core
    crewai/             # Subtree: CrewAI core
    anthropic-skills/   # Subtree: Anthropic Skills examples
    phoenix-examples/   # Subtree: Phoenix tracing examples
    trulens-examples/   # Subtree: TruLens eval examples
  mcp/
    servers/
      supabase/
      odoo/
      file/
      http/
    discovery.json
    README.md
  agents/
    examples/
      langgraph/
        finance_workflow.py
        README.md
      crewai/
        bir_filing_crew.py
        README.md
      mcp/
        odoo_bridge.py
        README.md
  scripts/
    eval/
      phoenix_trace.py
      trulens_score.py
      eval_config.yaml
  .github/
    workflows/
      agent-eval.yml
      openhands-sandbox.yml
  docs/
    AGENT_STACK_RESEARCH.md  # This file
    MCP_SETUP_GUIDE.md       # MCP server setup instructions
    AGENT_EVAL_GUIDE.md      # Eval metrics and thresholds
```

---

## Next Steps

**Immediate (this session)**:
1. ✅ Document research findings (this file)
2. Create MCP server structure
3. Vendor core frameworks via git subtree
4. Set up GitHub Actions for evals
5. Create example agents

**Short-term (next sprint)**:
1. Integrate Phoenix tracing in dev environment
2. Add TruLens metrics to PR checks
3. Test MCP discovery with Claude Code
4. Deploy Supabase + Odoo MCP servers to staging

**Medium-term (Q1 2026)**:
1. Evaluate OpenHands for safe code generation tasks
2. Extract Dify/Flowise patterns for visual debugging
3. Consider Semantic Kernel if cross-platform agents needed
4. Scale eval suite with DeepEval regression tests

---

## Decision Log

| Decision | Rationale | Date |
|----------|-----------|------|
| Prefer LangGraph over raw LangChain | Stateful graphs + checkpointing = better agent reliability | 2025-11-11 |
| Adopt MCP as tool standard | IDE-agnostic, standardized tool discovery | 2025-11-11 |
| Use Phoenix + TruLens for evals | Open-source, complementary (tracing + metrics) | 2025-11-11 |
| Vendor via git subtree | Auditable, CI-friendly, selective updates | 2025-11-11 |
| Gate OpenHands behind staging | Safety risk mitigation for autonomous code execution | 2025-11-11 |

---

## References

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [MCP Specification](https://modelcontextprotocol.io/introduction)
- [Phoenix Quickstart](https://docs.arize.com/phoenix/)
- [TruLens RAG Triad](https://www.trulens.org/trulens_eval/evaluation/feedback_functions/)
- [OpenAI Cookbook - Agents](https://cookbook.openai.com/examples/how_to_call_functions_with_chat_models)
