# RAG Chat Interface Implementation Plan

**Goal**: Build chat interfaces to expose the existing RAG knowledge pipeline

**Status**: Backend 90% complete, need frontend interfaces

---

## 🎯 What We're Building

### Option 1: MCP Server (Priority 1)
**Purpose**: Allow Claude Desktop/CLI to query InsightPulse docs
**Use Case**: Internal development, debugging, quick knowledge lookup
**Timeline**: 2-3 hours
**Effort**: Low
**Value**: Immediate productivity boost for developers

### Option 2: Web Chat Widget (Priority 2)
**Purpose**: Public documentation assistant (like Supabase/Docker screenshots)
**Use Case**: User-facing help, onboarding, support deflection
**Timeline**: 4-6 hours
**Effort**: Medium
**Value**: Reduces support burden, improves UX

---

## 📦 Implementation: MCP Server

### Architecture
```
┌─────────────────┐
│  Claude Desktop │
│   (or Claude    │
│      CLI)       │
└────────┬────────┘
         │ MCP Protocol
         ▼
┌─────────────────┐
│   MCP Server    │
│  (rag-search)   │
└────────┬────────┘
         │ Supabase Client
         ▼
┌─────────────────┐
│    Supabase     │
│   (pgvector)    │
└─────────────────┘
```

### File Structure
```
mcp/rag-server/
├── src/
│   ├── index.ts           # MCP server implementation
│   ├── supabase.ts        # Supabase client
│   └── tools.ts           # Tool definitions
├── package.json
├── tsconfig.json
└── README.md
```

### MCP Tools to Expose

1. **search_knowledge**
   - Input: `query` (string), `source_filter` (optional), `limit` (optional)
   - Output: Relevant documentation chunks with source URLs
   - Uses: `search_knowledge()` RPC function

2. **search_odoo_forum**
   - Input: `query` (string), `limit` (optional)
   - Output: Solved forum threads with solutions
   - Uses: `search_knowledge()` with `source_filter='forum'`

3. **search_finance_ssc**
   - Input: `query` (string), `category` (optional)
   - Output: Finance SSC examples and code
   - Uses: `search_knowledge()` with `source_filter='finance_ssc'`

4. **get_knowledge_stats**
   - Input: None
   - Output: Knowledge base statistics (total docs, quality scores)
   - Uses: `get_knowledge_stats()` RPC function

### Implementation Steps

#### Step 1: Initialize MCP Server (30 min)
```bash
cd mcp
mkdir -p rag-server/src
cd rag-server

npm init -y
npm install @modelcontextprotocol/sdk @supabase/supabase-js dotenv
npm install -D typescript @types/node tsx

# Create tsconfig.json
npx tsc --init
```

#### Step 2: Implement Supabase Client (30 min)
```typescript
// src/supabase.ts
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL!;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY!;

export const supabase = createClient(supabaseUrl, supabaseKey);

export async function searchKnowledge(
  query: string,
  limitCount: number = 5,
  sourceFilter?: string
) {
  const { data, error } = await supabase.rpc('search_knowledge', {
    query_text: query,
    limit_count: limitCount,
    source_filter: sourceFilter || null
  });

  if (error) throw error;
  return data;
}

export async function getKnowledgeStats() {
  const { data, error } = await supabase.rpc('get_knowledge_stats');
  if (error) throw error;
  return data;
}
```

#### Step 3: Define MCP Tools (45 min)
```typescript
// src/tools.ts
import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { searchKnowledge, getKnowledgeStats } from './supabase.js';

export const tools: Tool[] = [
  {
    name: 'search_knowledge',
    description: 'Search InsightPulse knowledge base (Odoo docs, forum, OCA, Finance SSC)',
    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Search query'
        },
        source_filter: {
          type: 'string',
          enum: ['forum', 'docs', 'oca', 'finance_ssc'],
          description: 'Filter by knowledge source (optional)'
        },
        limit: {
          type: 'number',
          default: 5,
          description: 'Number of results to return'
        }
      },
      required: ['query']
    }
  },
  {
    name: 'get_knowledge_stats',
    description: 'Get statistics about the knowledge base',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  }
];

export async function callTool(name: string, args: any) {
  switch (name) {
    case 'search_knowledge':
      return await searchKnowledge(
        args.query,
        args.limit || 5,
        args.source_filter
      );

    case 'get_knowledge_stats':
      return await getKnowledgeStats();

    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}
```

#### Step 4: Implement MCP Server (45 min)
```typescript
// src/index.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { tools, callTool } from './tools.js';
import 'dotenv/config';

const server = new Server(
  {
    name: 'insightpulse-rag',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    const result = await callTool(name, args || {});

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  } catch (error: any) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`
        }
      ],
      isError: true
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('InsightPulse RAG MCP server running on stdio');
}

main();
```

#### Step 5: Package & Configure (15 min)
```json
// package.json
{
  "name": "insightpulse-rag-mcp",
  "version": "1.0.0",
  "type": "module",
  "bin": {
    "insightpulse-rag": "./build/index.js"
  },
  "scripts": {
    "build": "tsc",
    "prepare": "npm run build",
    "dev": "tsx src/index.ts"
  }
}
```

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./build",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  }
}
```

```
# .env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key-here
```

#### Step 6: Install in Claude Desktop (15 min)
```json
// ~/.config/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "insightpulse-rag": {
      "command": "node",
      "args": [
        "/path/to/insightpulse-odoo/mcp/rag-server/build/index.js"
      ],
      "env": {
        "SUPABASE_URL": "https://your-project.supabase.co",
        "SUPABASE_SERVICE_KEY": "your-service-key-here"
      }
    }
  }
}
```

---

## 🌐 Implementation: Web Chat Widget

### Architecture
```
┌─────────────────┐
│   User Browser  │
│  (landing page) │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  Vercel Edge    │
│  (Next.js API)  │
└────────┬────────┘
         │ Vercel AI SDK
         ▼
┌─────────────────┐
│   OpenAI API    │
│  (GPT-4o-mini)  │
└─────────────────┘
         │
         ▼ RAG retrieval
┌─────────────────┐
│    Supabase     │
│   (pgvector)    │
└─────────────────┘
```

### File Structure
```
web-chat/
├── app/
│   ├── api/
│   │   └── chat/
│   │       └── route.ts      # Edge function for RAG
│   ├── page.tsx              # Chat UI demo
│   └── layout.tsx
├── components/
│   ├── ChatWidget.tsx        # Embeddable widget
│   └── ChatMessage.tsx
├── lib/
│   ├── supabase.ts          # Supabase client
│   └── rag.ts               # RAG retrieval logic
├── public/
│   └── embed.js             # Standalone widget embed script
├── package.json
└── README.md
```

### Implementation Steps

#### Step 1: Initialize Next.js Project (15 min)
```bash
npx create-next-app@latest web-chat \
  --typescript \
  --tailwind \
  --app \
  --no-src-dir

cd web-chat
npm install ai @supabase/supabase-js
```

#### Step 2: Create RAG Retrieval Logic (45 min)
```typescript
// lib/rag.ts
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_KEY!
);

export async function retrieveContext(query: string, limit = 5) {
  const { data, error } = await supabase.rpc('search_knowledge', {
    query_text: query,
    limit_count: limit
  });

  if (error) {
    console.error('RAG retrieval error:', error);
    return [];
  }

  return data.map((doc: any) => ({
    source: doc.source,
    title: doc.title,
    content: doc.content,
    url: doc.url,
    relevance: doc.relevance
  }));
}

export function formatContextForPrompt(contexts: any[]) {
  if (contexts.length === 0) {
    return 'No relevant documentation found.';
  }

  return contexts.map((ctx, idx) => `
[Source ${idx + 1}: ${ctx.source}]
Title: ${ctx.title}
${ctx.url ? `URL: ${ctx.url}` : ''}

${ctx.content}
---
  `).join('\n');
}
```

#### Step 3: Create Chat API Endpoint (60 min)
```typescript
// app/api/chat/route.ts
import { OpenAIStream, StreamingTextResponse } from 'ai';
import OpenAI from 'openai';
import { retrieveContext, formatContextForPrompt } from '@/lib/rag';

export const runtime = 'edge';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY!
});

const SYSTEM_PROMPT = `You are the InsightPulse AI documentation assistant.

Your purpose is to help users understand and use the InsightPulse Odoo platform.

Guidelines:
1. Answer based ONLY on the provided documentation context
2. If the answer isn't in the context, say "I don't have information about that"
3. Include source URLs when referencing specific docs
4. Be concise but helpful
5. Suggest related topics when relevant

Context will be provided with each user message.`;

export async function POST(req: Request) {
  const { messages } = await req.json();

  // Get the last user message
  const lastMessage = messages[messages.length - 1];
  const userQuery = lastMessage.content;

  // Retrieve relevant documentation
  const contexts = await retrieveContext(userQuery, 5);
  const contextText = formatContextForPrompt(contexts);

  // Augment the message with context
  const augmentedMessages = [
    { role: 'system', content: SYSTEM_PROMPT },
    ...messages.slice(0, -1),
    {
      role: 'user',
      content: `${userQuery}

<documentation_context>
${contextText}
</documentation_context>`
    }
  ];

  // Stream the response
  const response = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    stream: true,
    messages: augmentedMessages as any,
    temperature: 0.7,
    max_tokens: 1000
  });

  const stream = OpenAIStream(response);
  return new StreamingTextResponse(stream);
}
```

#### Step 4: Build Chat UI Component (90 min)
```typescript
// components/ChatWidget.tsx
'use client';

import { useChat } from 'ai/react';
import { useState } from 'react';

export default function ChatWidget() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat'
  });

  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Toggle button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="bg-blue-600 text-white rounded-full p-4 shadow-lg hover:bg-blue-700"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </button>
      )}

      {/* Chat window */}
      {isOpen && (
        <div className="bg-white rounded-lg shadow-2xl w-96 h-[600px] flex flex-col">
          {/* Header */}
          <div className="bg-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
            <h3 className="font-semibold">InsightPulse Assistant</h3>
            <button onClick={() => setIsOpen(false)} className="hover:bg-blue-700 rounded p-1">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-gray-500 text-sm">
                <p className="mb-2">👋 Hi! I can help you with:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Odoo module development</li>
                  <li>Finance SSC operations</li>
                  <li>BIR compliance</li>
                  <li>Deployment guides</li>
                </ul>
              </div>
            )}

            {messages.map(m => (
              <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-lg p-3 ${
                  m.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}>
                  <p className="text-sm whitespace-pre-wrap">{m.content}</p>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg p-3">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <form onSubmit={handleSubmit} className="p-4 border-t">
            <div className="flex space-x-2">
              <input
                value={input}
                onChange={handleInputChange}
                placeholder="Ask a question..."
                className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
              <button
                type="submit"
                disabled={isLoading}
                className="bg-blue-600 text-white rounded-lg px-4 py-2 hover:bg-blue-700 disabled:opacity-50"
              >
                Send
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
```

#### Step 5: Create Embeddable Widget Script (60 min)
```javascript
// public/embed.js
(function() {
  const WIDGET_URL = 'https://chat.insightpulseai.net';

  // Create iframe
  const iframe = document.createElement('iframe');
  iframe.src = `${WIDGET_URL}/embed`;
  iframe.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 400px;
    height: 600px;
    border: none;
    z-index: 9999;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  `;

  document.body.appendChild(iframe);
})();
```

#### Step 6: Deploy to Vercel (30 min)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Set environment variables
vercel env add SUPABASE_URL
vercel env add SUPABASE_SERVICE_KEY
vercel env add OPENAI_API_KEY
```

#### Step 7: Embed in Landing Page (15 min)
```html
<!-- landing-page/index.html -->
<body>
  <!-- Your existing content -->

  <!-- Add chat widget -->
  <script src="https://chat.insightpulseai.net/embed.js"></script>
</body>
```

---

## 📊 Comparison: MCP vs Web Widget

| Feature | MCP Server | Web Widget |
|---------|-----------|------------|
| **Target Users** | Developers | End users |
| **Use Case** | Development workflows | Support, onboarding |
| **Complexity** | Low | Medium |
| **Timeline** | 2-3 hours | 4-6 hours |
| **Hosting** | Local/CLI | Vercel Edge |
| **Cost** | $0 | ~$5/month (Vercel hobby) |
| **Maintenance** | Low | Medium |
| **Value** | High (dev productivity) | Very high (user experience) |

---

## 🎯 Recommended Implementation Order

### Phase 1: MCP Server (Week 1)
**Why First**:
- Quick win (2-3 hours)
- Immediate productivity boost
- Test RAG system in production
- Gather feedback on search quality

**Deliverables**:
- ✅ MCP server running on stdio
- ✅ 4 tools (search_knowledge, search_forum, search_finance, get_stats)
- ✅ Installed in Claude Desktop
- ✅ Documentation + usage examples

### Phase 2: Web Widget (Week 2)
**Why Second**:
- Proven RAG backend from Phase 1
- User-facing value
- Support deflection
- Marketing asset

**Deliverables**:
- ✅ Next.js chat API with RAG
- ✅ Embeddable chat widget
- ✅ Deployed to Vercel
- ✅ Embedded in landing page

### Phase 3: Improvements (Ongoing)
- Add conversation memory
- Support file uploads (OCR)
- Multi-language support
- Analytics dashboard
- A/B testing for prompts

---

## 📝 Next Actions

1. **Verify Supabase Schema** (5 min)
   ```bash
   psql $POSTGRES_URL -c "SELECT * FROM get_knowledge_stats();"
   ```

2. **Run Initial Scrape** (30-60 min)
   ```bash
   python odoo-spark-subagents/scripts/knowledge/odoo_scraper.py --initial-scrape
   ```

3. **Test Search Function** (5 min)
   ```bash
   psql $POSTGRES_URL -c "SELECT * FROM search_knowledge('create odoo module', 5);"
   ```

4. **Build MCP Server** (2-3 hours)
   - Follow steps above
   - Install in Claude Desktop
   - Test search_knowledge tool

5. **Build Web Widget** (4-6 hours)
   - Follow steps above
   - Deploy to Vercel
   - Embed in landing page

---

## 🚀 Ready to Build?

Which should I start with?
- **Option A**: MCP Server (quick win, 2-3 hours)
- **Option B**: Web Widget (user-facing, 4-6 hours)
- **Option C**: Both (full RAG system, 6-9 hours)

Let me know and I'll start implementing! 🎯
