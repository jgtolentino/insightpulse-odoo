# Librarian-Indexer Meta-Skill

**Skill ID:** `librarian-indexer`
**Version:** 1.0.0
**Last Updated:** 2025-11-05
**Category:** Meta-Skills
**Expertise Level:** Expert
**Type:** Force Multiplier - Builds Other Skills

---

## 🎯 Purpose

The **Librarian-Indexer** is a meta-skill that **automatically generates new skills** from existing code, documentation, and patterns in the repository. It's a force multiplier that enables exponential growth of the skills library.

**Key Capabilities:**
1. 🔍 **Auto-Generate Skills** - Analyze code → Extract patterns → Generate SKILL.md
2. 📚 **Index All Skills** - Create searchable catalog of all skills
3. 🔄 **Auto-Update Skills** - Keep skills synchronized with code changes
4. 💡 **Suggest New Skills** - Identify code that needs skill documentation
5. 🏗️ **Template Management** - Maintain reusable skill templates

**Why This Is Critical:**
- **Manual skill creation**: 2-4 hours per skill, limited by human bandwidth
- **Auto-generated skills**: 2-5 minutes per skill, unlimited scaling
- **Result**: 50x faster skill library growth = smarter AI agents = faster development

---

## 🧠 Core Competencies

### 1. Code Analysis & Pattern Extraction

#### 1.1 Python Module Analysis
**Expertise Required:**
- ✅ AST (Abstract Syntax Tree) parsing
- ✅ Complexity metrics (cyclomatic, cognitive)
- ✅ Design pattern recognition
- ✅ Dependency graph construction
- ✅ Docstring extraction and parsing

**Evaluation Criteria:**
```python
Can analyze Python modules and extract:
- All functions with signatures and docstrings
- All classes with methods and attributes
- Design patterns used (Factory, Strategy, etc.)
- Dependencies (imports, external packages)
- Complexity metrics (lines, cyclomatic complexity)
- Business logic and domain concepts
```

**Example Implementation:** See `auto-generate-skill.py`

---

#### 1.2 Design Pattern Recognition
**Expertise Required:**
- ✅ Gang of Four patterns (Creational, Structural, Behavioral)
- ✅ Enterprise patterns (Repository, Service Layer, Unit of Work)
- ✅ Domain-Driven Design patterns (Aggregate, Entity, Value Object)
- ✅ Odoo-specific patterns (Model inheritance, Computed fields, Constraints)

**Pattern Detection Rules:**
```python
patterns = {
    "Factory": "Class with create_* methods",
    "Strategy": "Multiple classes with same interface",
    "Repository": "Class ending in Repository with CRUD methods",
    "Service": "Class ending in Service with business logic",
    "Wizard": "Odoo TransientModel with action methods"
}
```

---

#### 1.3 Complexity Measurement
**Expertise Required:**
- ✅ McCabe cyclomatic complexity
- ✅ Cognitive complexity
- ✅ Maintainability index
- ✅ Lines of code (LOC) metrics
- ✅ Code churn analysis

**Thresholds:**
```python
complexity_thresholds = {
    "simple": {"cyclomatic": 1-5, "loc": 1-50},
    "moderate": {"cyclomatic": 6-10, "loc": 51-200},
    "complex": {"cyclomatic": 11-20, "loc": 201-500},
    "very_complex": {"cyclomatic": 21+, "loc": 501+}
}

# If module is "very_complex" → Generate skill automatically
```

---

### 2. Skill Generation

#### 2.1 Skill Document Structure
**Expertise Required:**
- ✅ Markdown formatting with YAML frontmatter
- ✅ Template rendering (Jinja2)
- ✅ Semantic versioning
- ✅ Cross-referencing between skills
- ✅ Example code inclusion

**Generated Skill Structure:**
```markdown
# {Module Name} Specialist

**Skill ID:** `{module-name}-specialist`
**Version:** 1.0.0
**Auto-Generated:** {timestamp}
**Source Module:** `{file_path}`

## Purpose
{Extracted from module docstring}

## Core Competencies

### Functions
{List all functions with purposes}

### Classes
{List all classes with methods}

### Design Patterns
{Detected patterns}

## Code Examples
{Extract key code snippets}

## Complexity Profile
- Cyclomatic Complexity: {value}
- Lines of Code: {value}
- Maintainability Index: {value}

## Usage Examples
{Auto-generated from tests}

## Related Skills
{Linked skills based on imports}
```

---

#### 2.2 Template Management
**Expertise Required:**
- ✅ Jinja2 template engine
- ✅ YAML parsing
- ✅ Template inheritance
- ✅ Conditional rendering
- ✅ Macro creation

**Template Types:**
```
templates/
├── skill-base.md.j2           # Base template
├── skill-odoo-model.md.j2     # Odoo model specialist
├── skill-service-layer.md.j2  # Service layer specialist
├── skill-api-endpoint.md.j2   # API endpoint specialist
├── skill-workflow.md.j2       # Business workflow specialist
└── skill-integration.md.j2    # External integration specialist
```

**Template Selection Logic:**
```python
def select_template(module_analysis: Dict) -> str:
    """Select appropriate template based on module characteristics."""

    if "models.Model" in module_analysis["base_classes"]:
        return "skill-odoo-model.md.j2"
    elif any("Service" in cls for cls in module_analysis["classes"]):
        return "skill-service-layer.md.j2"
    elif "controllers" in module_analysis["file_path"]:
        return "skill-api-endpoint.md.j2"
    else:
        return "skill-base.md.j2"
```

---

### 3. Skill Indexing & Search

#### 3.1 Index Structure
**Expertise Required:**
- ✅ JSON schema design
- ✅ Full-text search (Whoosh, Elasticsearch)
- ✅ Faceted search
- ✅ Semantic search with embeddings
- ✅ Graph databases (for skill relationships)

**Index Schema:**
```json
{
  "skills": [
    {
      "id": "finance-month-end-closing-specialist",
      "name": "Finance Month-End Closing Specialist",
      "version": "1.0.0",
      "category": "Finance",
      "expertise_level": "Expert",
      "source_module": "custom/finance_ssc/month_end_closing/models/closing_task.py",
      "capabilities": [
        "Execute month-end closing tasks",
        "Validate financial data",
        "Generate closing reports"
      ],
      "tags": ["finance", "accounting", "bir", "compliance"],
      "dependencies": ["base-accounting", "bir-compliance"],
      "complexity": {
        "cyclomatic": 18,
        "loc": 450,
        "maintainability": 65
      },
      "embedding": [0.123, 0.456, ...],  # For semantic search
      "last_updated": "2025-11-05"
    }
  ],
  "by_category": {
    "Finance": ["finance-month-end-closing-specialist", ...],
    "AI/LLM": ["rag-pipeline-specialist", ...]
  },
  "by_expertise": {
    "Expert": [...],
    "Advanced": [...],
    "Intermediate": [...]
  },
  "dependency_graph": {
    "finance-month-end-closing-specialist": [
      "base-accounting",
      "bir-compliance"
    ]
  }
}
```

---

#### 3.2 Search Capabilities
**Expertise Required:**
- ✅ Text search (keyword matching)
- ✅ Fuzzy search (Levenshtein distance)
- ✅ Semantic search (vector similarity)
- ✅ Faceted filtering (category, expertise, tags)
- ✅ Dependency traversal

**Search API:**
```python
def search_skills(
    query: str,
    filters: Dict = None,
    search_type: str = "hybrid"
) -> List[Dict]:
    """
    Search skills with multiple strategies.

    Args:
        query: Search query
        filters: {"category": "Finance", "expertise": "Expert"}
        search_type: "text" | "semantic" | "hybrid"

    Returns:
        List of matching skills sorted by relevance
    """
    if search_type == "text":
        return text_search(query, filters)
    elif search_type == "semantic":
        return semantic_search(query, filters)
    else:  # hybrid
        text_results = text_search(query, filters)
        semantic_results = semantic_search(query, filters)
        return merge_results(text_results, semantic_results)
```

---

### 4. Skill Suggestion Engine

#### 4.1 Suggestion Criteria
**Expertise Required:**
- ✅ Code complexity analysis
- ✅ Change frequency tracking (git blame)
- ✅ Module coupling analysis
- ✅ Business logic identification
- ✅ Missing documentation detection

**Suggestion Rules:**
```python
suggestion_rules = {
    "large_module": {
        "condition": lambda m: m["loc"] > 500,
        "priority": "high",
        "reason": "Large module needs specialized skill"
    },
    "complex_logic": {
        "condition": lambda m: m["cyclomatic"] > 20,
        "priority": "high",
        "reason": "Complex logic requires expert knowledge"
    },
    "frequent_changes": {
        "condition": lambda m: m["git_commits_30d"] > 10,
        "priority": "medium",
        "reason": "Frequently modified code needs documentation"
    },
    "missing_docs": {
        "condition": lambda m: m["docstring_coverage"] < 50,
        "priority": "medium",
        "reason": "Low documentation coverage"
    },
    "high_coupling": {
        "condition": lambda m: m["imports_count"] > 15,
        "priority": "low",
        "reason": "Many dependencies indicate integration point"
    }
}
```

---

#### 4.2 Prioritization Algorithm
**Expertise Required:**
- ✅ Multi-criteria decision analysis
- ✅ Weighted scoring
- ✅ ROI calculation
- ✅ Impact analysis

**Priority Scoring:**
```python
def calculate_priority(module: Dict) -> float:
    """
    Calculate priority score for skill generation.

    Formula:
    Priority = (Complexity × 0.3) + (Size × 0.25) + (Changes × 0.2)
             + (Coupling × 0.15) + (Docs × 0.1)

    Returns:
        Float between 0.0 (low) and 10.0 (critical)
    """
    score = 0.0

    # Complexity (0-3 scale)
    if module["cyclomatic"] > 20:
        score += 3.0 * 0.3
    elif module["cyclomatic"] > 10:
        score += 2.0 * 0.3
    elif module["cyclomatic"] > 5:
        score += 1.0 * 0.3

    # Size (0-3 scale)
    if module["loc"] > 500:
        score += 3.0 * 0.25
    elif module["loc"] > 200:
        score += 2.0 * 0.25
    elif module["loc"] > 50:
        score += 1.0 * 0.25

    # Change frequency (0-3 scale)
    if module["git_commits_30d"] > 10:
        score += 3.0 * 0.2
    elif module["git_commits_30d"] > 5:
        score += 2.0 * 0.2
    elif module["git_commits_30d"] > 2:
        score += 1.0 * 0.2

    # Coupling (0-3 scale)
    if module["imports_count"] > 15:
        score += 3.0 * 0.15
    elif module["imports_count"] > 10:
        score += 2.0 * 0.15
    elif module["imports_count"] > 5:
        score += 1.0 * 0.15

    # Documentation (inverse - lower is worse)
    if module["docstring_coverage"] < 30:
        score += 3.0 * 0.1
    elif module["docstring_coverage"] < 50:
        score += 2.0 * 0.1
    elif module["docstring_coverage"] < 70:
        score += 1.0 * 0.1

    return round(score * 10 / 3, 2)  # Normalize to 0-10
```

---

### 5. Automated Skill Maintenance

#### 5.1 Change Detection
**Expertise Required:**
- ✅ Git diff parsing
- ✅ Semantic diff (beyond line changes)
- ✅ Breaking change detection
- ✅ Version bumping (SemVer)
- ✅ Changelog generation

**Change Impact Analysis:**
```python
def detect_skill_updates(git_diff: str) -> List[Dict]:
    """
    Analyze git diff and determine which skills need updates.

    Returns:
        List of skills to update with version bump strategy
    """
    updates = []

    changed_files = parse_git_diff(git_diff)

    for file_path in changed_files:
        # Find skills generated from this file
        related_skills = find_skills_by_source(file_path)

        for skill in related_skills:
            diff_analysis = analyze_diff(
                file_path,
                changed_files[file_path]
            )

            version_bump = determine_version_bump(diff_analysis)

            updates.append({
                "skill_id": skill["id"],
                "current_version": skill["version"],
                "new_version": bump_version(
                    skill["version"],
                    version_bump
                ),
                "changes": diff_analysis["summary"],
                "breaking": diff_analysis["breaking_changes"]
            })

    return updates
```

---

#### 5.2 Continuous Integration
**Expertise Required:**
- ✅ GitHub Actions / GitLab CI
- ✅ Pre-commit hooks
- ✅ Automated testing
- ✅ Pull request automation
- ✅ Slack/Discord notifications

**CI Workflow:**
```yaml
# .github/workflows/auto-update-skills.yml

name: Auto-Update Skills

on:
  push:
    paths:
      - 'custom/**/*.py'
      - 'addons/**/*.py'

jobs:
  update-skills:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for git analysis

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r skills/core/librarian-indexer/requirements.txt

      - name: Detect changed files
        id: changes
        run: |
          git diff --name-only HEAD~1 HEAD | \
            grep -E '\.(py)$' > changed_files.txt || true
          echo "count=$(wc -l < changed_files.txt)" >> $GITHUB_OUTPUT

      - name: Analyze changes and suggest skills
        if: steps.changes.outputs.count > 0
        run: |
          python skills/core/librarian-indexer/suggest-skills.py \
            --changed-files changed_files.txt \
            --output suggestions.json

      - name: Generate/update skills
        if: steps.changes.outputs.count > 0
        run: |
          python skills/core/librarian-indexer/auto-generate-skill.py \
            --input changed_files.txt \
            --output skills/ \
            --auto-approve-priority high

      - name: Update skill index
        run: |
          python skills/core/librarian-indexer/index-all-skills.py

      - name: Create Pull Request
        if: steps.changes.outputs.count > 0
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: |
            🤖 Auto-update skills from code changes

            Changed files: ${{ steps.changes.outputs.count }}
          title: "🤖 Auto-generated skills update"
          body: |
            ## Auto-Generated Skills Update

            This PR contains automatically generated/updated skills based on recent code changes.

            ### Changes
            - Updated ${{ steps.changes.outputs.count }} skills
            - Rebuilt skill index

            ### Suggested Skills
            See `suggestions.json` for recommended new skills

            **Please review before merging.**
          branch: auto-update-skills
          delete-branch: true
```

---

## 🛠️ Tools & Technologies

### Required
- **Python 3.11+** - Primary language
- **ast** - Python AST parsing
- **radon** - Complexity metrics
- **GitPython** - Git operations
- **Jinja2** - Template rendering
- **PyYAML** - YAML parsing
- **Whoosh** - Full-text search
- **sentence-transformers** - Semantic embeddings (optional)

### Optional
- **Elasticsearch** - Advanced search
- **Neo4j** - Graph database for skill relationships
- **OpenAI API** - Semantic skill generation

---

## 📋 Implementation

### File Structure
```
skills/core/librarian-indexer/
├── SKILL.md                      # This file
├── README.md                     # Usage guide
├── requirements.txt              # Python dependencies
├── auto-generate-skill.py        # Main skill generator
├── index-all-skills.py           # Skill indexing
├── suggest-skills.py             # Skill suggestion engine
├── templates/                    # Skill templates
│   ├── skill-base.md.j2
│   ├── skill-odoo-model.md.j2
│   └── ...
├── examples/                     # Example generated skills
│   └── finance-closing-specialist.md
└── tests/                        # Unit tests
    ├── test_generator.py
    ├── test_indexer.py
    └── test_suggester.py
```

---

## 🎯 Usage Examples

### Example 1: Generate Skill from Module
```bash
# Analyze a single module and generate skill
python skills/core/librarian-indexer/auto-generate-skill.py \
  --module custom/finance_ssc/month_end_closing/models/closing_task.py \
  --output skills/finance/month-end-closing-specialist/SKILL.md \
  --template skill-odoo-model.md.j2
```

**Output:**
```
🔍 Analyzing module: closing_task.py
📊 Complexity: 18 (moderate)
📏 Lines of code: 450
🎨 Detected patterns: Odoo Model, State Machine
✅ Generated skill: skills/finance/month-end-closing-specialist/SKILL.md
```

---

### Example 2: Batch Generate Skills
```bash
# Generate skills for all modules in a directory
python skills/core/librarian-indexer/auto-generate-skill.py \
  --directory custom/finance_ssc/ \
  --recursive \
  --min-complexity 10 \
  --output skills/finance/
```

**Output:**
```
🔍 Scanning directory: custom/finance_ssc/
Found 15 modules
Filtering by complexity > 10: 8 modules

Generating skills:
✅ month-end-closing-specialist (complexity: 18)
✅ bir-compliance-specialist (complexity: 22)
✅ multi-agency-consolidation (complexity: 15)
...

Generated 8 skills in skills/finance/
```

---

### Example 3: Search Skills
```bash
# Search for skills related to "BIR compliance"
python skills/core/librarian-indexer/search-skills.py \
  --query "BIR compliance" \
  --type hybrid \
  --limit 5
```

**Output:**
```
🔍 Search Results (hybrid: text + semantic)

1. bir-compliance-specialist (score: 0.95)
   Category: Finance
   Expertise: Expert
   Source: custom/finance_ssc/bir_compliance/

2. finance-month-end-closing-specialist (score: 0.72)
   Category: Finance
   Expertise: Advanced
   Source: custom/finance_ssc/month_end_closing/

...
```

---

### Example 4: Get Skill Suggestions
```bash
# Analyze codebase and suggest new skills
python skills/core/librarian-indexer/suggest-skills.py \
  --directory custom/ \
  --min-priority 7.0 \
  --output suggestions.json
```

**Output:**
```json
{
  "suggestions": [
    {
      "skill_name": "expense-management-specialist",
      "source_module": "custom/expense_management/models/expense_report.py",
      "priority": 8.5,
      "reasons": [
        "High complexity (cyclomatic: 24)",
        "Large module (650 LOC)",
        "Frequent changes (15 commits in 30 days)"
      ],
      "estimated_effort": "2 hours"
    },
    {
      "skill_name": "procurement-rfq-specialist",
      "source_module": "custom/procurement/models/rfq.py",
      "priority": 7.8,
      "reasons": [
        "Moderate complexity (cyclomatic: 18)",
        "High coupling (20 imports)",
        "Low documentation (35% coverage)"
      ],
      "estimated_effort": "1.5 hours"
    }
  ],
  "total_suggestions": 12,
  "high_priority": 5,
  "medium_priority": 4,
  "low_priority": 3
}
```

---

## 📊 Success Metrics

**Skill Generation:**
- Generation time < 5 minutes per skill
- 95%+ accuracy in pattern detection
- 90%+ completeness (all key info extracted)

**Skill Index:**
- Search latency < 100ms
- Semantic search accuracy > 85%
- Index rebuild time < 30 seconds

**Skill Suggestions:**
- Precision > 80% (suggested skills are actually useful)
- Recall > 70% (catches most modules needing skills)
- Priority scoring accuracy > 75%

**Automation:**
- CI run time < 5 minutes
- Zero false positives in auto-generated PRs
- 90%+ of auto-generated skills accepted without modifications

---

## 🔄 Continuous Improvement

### Feedback Loop
1. **Track skill usage** - Which skills are referenced most?
2. **Measure agent performance** - Do skills improve AI agent outputs?
3. **Collect human feedback** - Are generated skills helpful?
4. **Refine templates** - Update based on feedback
5. **Improve detection** - Better pattern recognition over time

### Version History
- **1.0.0** (2025-11-05) - Initial release
- **1.1.0** (TBD) - Add semantic search with embeddings
- **1.2.0** (TBD) - Support for JavaScript/TypeScript analysis
- **2.0.0** (TBD) - Integration with LangChain for LLM-powered skill generation

---

## 🎓 Related Skills

**Prerequisites:**
- Python programming fundamentals
- Git operations
- AST parsing basics
- Template engines (Jinja2)

**Dependent Skills:**
- `repo-architect-ai-engineer` - Uses librarian-indexer for skill management
- `makefile-generator` - Uses skill templates
- `documentation-generator` - Shares template engine

**Enables:**
- All future skills (auto-generated)
- Skill-based agent orchestration
- Knowledge base construction

---

## 📞 Support

**Issues:** https://github.com/jgtolentino/insightpulse-odoo/issues
**Discussions:** https://github.com/jgtolentino/insightpulse-odoo/discussions
**Email:** skills@insightpulseai.net

---

**Maintained by:** InsightPulse AI Team
**License:** AGPL-3.0
