---
name: ai-analytics-genie
description: Tableau Next + Databricks Genie AI/BI features - Agentic analytics with conversational insights
version: 1.0.0
tags: [ai, analytics, tableau, databricks, genie, nl2sql, dashboards]
---

# AI Analytics Genie Skill

## Purpose

Combine features from **Tableau Next (Salesforce Agentforce)** and **Databricks AI/BI Genie** into a unified agentic analytics system:

- 🤖 **Conversational Analytics**: Natural language → SQL → Insights
- 📊 **Auto-Dashboards**: Generate dashboards from descriptions
- 🔍 **Data Discovery**: Automatic schema understanding and recommendations
- 💡 **Proactive Insights**: AI-driven anomaly detection and suggestions
- 🔄 **Self-Service BI**: No-code analytics for business users

## Tableau Next Features

### 1. Agentforce Analytics

**Conversational Interface**:

```
User: "Show me revenue trends by region"
AI: "I found revenue data across 5 regions. Here's a trend analysis..."
[Generates line chart with regional breakdowns]

User: "Which region is growing fastest?"
AI: "APAC shows 45% YoY growth, highest among all regions..."
[Highlights APAC trend line]

User: "Create a dashboard for executive review"
AI: "Created 'Executive Revenue Dashboard' with:
- Revenue trend by region
- Top 10 customers
- YoY growth comparison
Would you like to add more widgets?"
```

### 2. Trusted Data Foundation

**Automatic Data Governance**:

```typescript
interface DataGovernance {
  certified_sources: string[]; // Verified data sources
  access_controls: RoleBasedAccess; // Who can see what
  lineage_tracking: DataLineage; // Where data comes from
  quality_scores: QualityMetrics; // Data reliability ratings
}
```

### 3. Augmented Analytics

**AI-Powered Insights**:

```typescript
interface AugmentedInsights {
  anomalies: Array<{
    metric: string;
    expected_value: number;
    actual_value: number;
    deviation_pct: number;
    explanation: string;
    suggested_actions: string[];
  }>;

  correlations: Array<{
    var1: string;
    var2: string;
    correlation: number;
    strength: 'weak' | 'moderate' | 'strong';
    insight: string;
  }>;

  predictions: Array<{
    metric: string;
    next_period: number;
    confidence_interval: [number, number];
    model_accuracy: number;
  }>;
}
```

## Databricks Genie Features

### 1. Natural Language to SQL

**Advanced SQL Generation**:

```typescript
async function nl_to_sql_genie(
  question: string,
  context: AnalyticsContext
): Promise<{
  sql: string;
  execution_plan: string;
  confidence: number;
  alternative_queries?: string[];
}> {
  // 1. Understand intent
  const intent = await parse_intent(question);

  // 2. Generate multiple SQL candidates
  const candidates = await generate_sql_candidates(intent, context);

  // 3. Rank by quality and confidence
  const ranked = rank_sql_queries(candidates, context);

  // 4. Optimize best query
  const optimized = optimize_sql(ranked[0], context);

  return {
    sql: optimized.sql,
    execution_plan: optimized.plan,
    confidence: optimized.confidence,
    alternative_queries: ranked.slice(1, 3).map((q) => q.sql),
  };
}
```

**Example**:

```
User: "Compare Q3 revenue to last year, broken down by product category"

SQL Generated:
SELECT
  pc.category_name,
  SUM(CASE WHEN DATE_TRUNC('quarter', o.order_date) = DATE_TRUNC('quarter', CURRENT_DATE)
       THEN o.total_amount ELSE 0 END) as q3_current,
  SUM(CASE WHEN DATE_TRUNC('quarter', o.order_date) = DATE_TRUNC('quarter', CURRENT_DATE - INTERVAL '1 year')
       THEN o.total_amount ELSE 0 END) as q3_last_year,
  ROUND(
    (SUM(CASE WHEN DATE_TRUNC('quarter', o.order_date) = DATE_TRUNC('quarter', CURRENT_DATE)
         THEN o.total_amount ELSE 0 END) /
     NULLIF(SUM(CASE WHEN DATE_TRUNC('quarter', o.order_date) = DATE_TRUNC('quarter', CURRENT_DATE - INTERVAL '1 year')
         THEN o.total_amount ELSE 0 END), 0) - 1) * 100, 2
  ) as yoy_growth_pct
FROM orders o
JOIN products p ON o.product_id = p.id
JOIN product_categories pc ON p.category_id = pc.id
WHERE o.order_date >= DATE_TRUNC('quarter', CURRENT_DATE - INTERVAL '1 year')
GROUP BY pc.category_name
ORDER BY yoy_growth_pct DESC;
```

### 2. Context-Aware Intelligence

**Schema Understanding**:

```typescript
interface SchemaContext {
  tables: Array<{
    name: string;
    description: string;
    business_meaning: string;
    sample_questions: string[];
    common_joins: string[];
  }>;

  relationships: Array<{
    from_table: string;
    to_table: string;
    join_type: 'one_to_many' | 'many_to_one' | 'many_to_many';
    join_column: string;
  }>;

  metrics: Array<{
    name: string;
    definition: string;
    calculation: string;
    business_logic: string;
  }>;

  business_glossary: Map<string, string>;
}
```

### 3. Self-Service Data Discovery

**Auto-Recommendations**:

```typescript
interface DataRecommendations {
  similar_questions: string[];
  suggested_visualizations: ChartConfig[];
  related_datasets: string[];
  data_quality_alerts: Alert[];
  optimization_suggestions: string[];
}
```

## Combined Feature Set

### 1. Conversational Analytics Engine

```typescript
interface ConversationalAnalytics {
  // Session management
  session_id: string;
  conversation_history: Message[];

  // Context retention
  current_dataset: string;
  active_filters: Filter[];
  previous_queries: Query[];

  // Proactive assistance
  suggestions: string[];
  follow_up_questions: string[];
}

async function chat_analytics(
  message: string,
  session: ConversationalAnalytics
): Promise<{
  response: string;
  data?: any[];
  visualization?: ChartConfig;
  insights?: Insight[];
  next_questions?: string[];
}> {
  // 1. Understand message in context
  const intent = await understand_with_context(message, session);

  // 2. Generate response (SQL, insights, or clarification)
  if (intent.type === 'query') {
    const { sql, data } = await execute_query(intent);
    const viz = infer_visualization(data, message);
    const insights = generate_insights(data);
    const next = suggest_follow_ups(data, session);

    return { response, data, visualization: viz, insights, next_questions: next };
  }

  // 3. Handle clarifications
  if (intent.type === 'clarification_needed') {
    return {
      response: 'I need more info: ' + intent.clarifying_questions.join(', '),
    };
  }

  // 4. Provide explanations
  if (intent.type === 'explain') {
    return {
      response: explain_previous_result(session),
    };
  }
}
```

### 2. Dashboard Generation

```typescript
async function generate_dashboard(
  description: string,
  data_sources: string[]
): Promise<{
  dashboard_id: string;
  layout: DashboardLayout;
  widgets: Widget[];
  filters: GlobalFilter[];
}> {
  // 1. Parse dashboard requirements
  const requirements = await parse_dashboard_description(description);

  // 2. Identify required metrics
  const metrics = identify_metrics(requirements, data_sources);

  // 3. Generate SQL for each metric
  const queries = await Promise.all(metrics.map((m) => nl_to_sql_genie(m.question, context)));

  // 4. Choose optimal visualizations
  const widgets = queries.map((q, i) => ({
    type: infer_chart_type(metrics[i], q.data),
    query: q.sql,
    title: metrics[i].title,
    position: calculate_layout_position(i, metrics.length),
  }));

  // 5. Create dashboard
  const dashboard = await create_dashboard({
    title: requirements.title,
    widgets: widgets,
    filters: requirements.filters || [],
  });

  return dashboard;
}
```

**Example**:

```
User: "Create an executive dashboard showing:
- Revenue trends
- Top performing products
- Regional sales map
- Customer acquisition metrics"

AI generates:
Dashboard: "Executive Overview"
├─ Widget 1 (Line Chart): Revenue trend (last 12 months)
├─ Widget 2 (Bar Chart): Top 10 products by revenue
├─ Widget 3 (Geo Map): Sales by region (color-coded)
└─ Widget 4 (KPI Cards): New customers, CAC, LTV

Global Filters: Date range, Region, Product category
```

### 3. Proactive Insights

```typescript
interface ProactiveInsights {
  anomalies: AnomalyDetection;
  trends: TrendAnalysis;
  predictions: Forecast;
  recommendations: ActionableInsights;
}

async function detect_anomalies(metric: string, data: TimeSeriesData): Promise<Anomaly[]> {
  // 1. Calculate baseline statistics
  const baseline = calculate_baseline(data);

  // 2. Identify outliers
  const outliers = detect_outliers(data, baseline);

  // 3. Explain anomalies
  const explanations = await explain_anomalies(outliers);

  return outliers.map((o, i) => ({
    date: o.date,
    expected_value: baseline.mean,
    actual_value: o.value,
    deviation_std: (o.value - baseline.mean) / baseline.std,
    severity: calculate_severity(o, baseline),
    explanation: explanations[i],
    suggested_actions: generate_actions(o, explanations[i]),
  }));
}
```

### 4. Multi-Database Support

```typescript
interface DatabaseAdapter {
  type: 'postgres' | 'mysql' | 'bigquery' | 'snowflake' | 'databricks';
  connection: DatabaseConnection;
  capabilities: {
    window_functions: boolean;
    cte_support: boolean;
    array_agg: boolean;
    json_functions: boolean;
  };
}

function adapt_sql_syntax(sql: string, source_db: DatabaseType, target_db: DatabaseType): string {
  // Convert between database dialects
  const transformations = {
    date_functions: adapt_date_functions(sql, source_db, target_db),
    string_functions: adapt_string_functions(sql, source_db, target_db),
    aggregations: adapt_aggregations(sql, source_db, target_db),
  };

  return apply_transformations(sql, transformations);
}
```

## Implementation Architecture

### Stack

```yaml
Frontend:
  - Next.js 14 (App Router)
  - React Query (data fetching)
  - Recharts / Chart.js (visualizations)
  - Tailwind CSS + shadcn/ui (styling)

Backend:
  - Supabase Edge Functions (API)
  - PostgreSQL (primary database)
  - Redis (caching, session management)

AI Layer:
  - OpenAI GPT-4 (SQL generation, insights)
  - LangChain (agent orchestration)
  - Anthropic Claude (complex reasoning)

Analytics:
  - Cube.js (semantic layer)
  - dbt (data transformation)
  - Apache Arrow (in-memory analytics)
```

### API Endpoints

```typescript
// Natural language query
POST /api/analytics/query
{
  "question": "Show me revenue trends",
  "session_id": "abc123",
  "context": {...}
}

// Generate dashboard
POST /api/analytics/dashboard
{
  "description": "Executive dashboard...",
  "data_sources": ["orders", "customers"]
}

// Get proactive insights
GET /api/analytics/insights?dataset=orders&period=last_30_days

// Execute SQL
POST /api/analytics/sql
{
  "sql": "SELECT...",
  "database_id": "prod_db"
}

// Generate visualization
POST /api/analytics/visualize
{
  "data": [...],
  "chart_type": "auto"  // or specify: line, bar, pie, etc.
}
```

## Example Workflows

### Workflow 1: Conversational Analysis

```
User: "How is our revenue doing?"

AI: "Q4 2024 revenue is $2.5M, up 15% from Q3.
    [Line chart showing quarterly revenue trend]
    Would you like to see this broken down by product category?"

User: "Yes, and compare to last year"

AI: "Here's Q4 revenue by category vs Q4 2023:
    [Grouped bar chart]
    - Software: +25% ($1.2M vs $960K)
    - Services: +8% ($1.1M vs $1.0M)
    - Hardware: -5% ($200K vs $210K)

    Notable: Software growth accelerating (was +18% in Q3)"

User: "What's driving software growth?"

AI: "Analyzing software revenue...
    Top 3 drivers:
    1. Enterprise license upsells (+40%)
    2. New logo acquisitions (+35 customers)
    3. Reduced churn (12% → 8%)

    Recommendation: Focus on enterprise segment - highest growth + margins"
```

### Workflow 2: Dashboard Creation

```
User: "Create a sales performance dashboard"

AI: "I'll create a dashboard with key sales metrics. What should I include?
    Suggestions:
    - Revenue trends
    - Sales rep performance
    - Pipeline health
    - Win/loss analysis
    - Deal velocity"

User: "All of those, plus regional breakdown"

AI: "Creating 'Sales Performance Dashboard' with 6 widgets...
    [Generates dashboard]

    Dashboard ready! Contains:
    1. Revenue trend (last 12 months)
    2. Top 10 sales reps (by revenue)
    3. Pipeline by stage (funnel chart)
    4. Win rate by product (%)
    5. Average deal cycle (days)
    6. Regional performance (map + table)

    Global filters: Date range, Sales rep, Region, Product"
```

### Workflow 3: Proactive Insights

```
System: "🔔 Anomaly detected in user signups

    Yesterday's signups: 150 (expected: 420, -64%)
    Severity: HIGH
    Likely cause: Marketing campaign paused

    Suggested actions:
    1. Check marketing automation status
    2. Review landing page performance
    3. Verify payment gateway uptime

    Would you like me to investigate further?"

User: "Yes, check marketing campaigns"

AI: "Analyzing marketing campaigns...
    Found issue: Email campaign scheduled for yesterday did not send.
    Status: 'Paused' (likely accidental)

    Impact: ~270 missed signups (~$13,500 potential revenue)

    Recommendation: Resume campaign + send makeup email today"
```

## Success Metrics

Track these KPIs:

- **Query Success Rate**: ≥ 95% of natural language queries generate valid SQL
- **Query Accuracy**: ≥ 90% of generated SQL returns expected results
- **Visualization Relevance**: ≥ 85% of auto-generated charts are appropriate
- **Insight Actionability**: ≥ 80% of AI insights lead to user action
- **Time to Insight**: ≤ 30 seconds from question to visualization
- **User Satisfaction**: ≥ 4.5/5 rating for conversational experience

## References

- [Tableau Next](https://www.tableau.com/products/tableau-next)
- [Databricks AI/BI Genie](https://www.databricks.com/product/ai-bi)
- [Salesforce Agentforce](https://www.salesforce.com/agentforce/)
- [LangChain SQL Agent](https://python.langchain.com/docs/use_cases/sql/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
