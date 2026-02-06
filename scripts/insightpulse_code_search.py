#!/usr/bin/env python3
"""
InsightPulse AI-Powered Code Search

Semantic code search using Claude + pgvector for the InsightPulse Odoo codebase.
Understands Odoo patterns, BIR compliance, Finance SSC workflows.

Features:
- Semantic code search with pgvector embeddings
- Natural language queries ("How do I generate BIR 1601-C?")
- Ask Claude about codebase with relevant context
- Search by: function, class, workflow, BIR form, company code
- Integration with Supabase pgvector

Usage:
    # Index codebase (run once)
    python scripts/insightpulse_code_search.py --index

    # Search
    python scripts/insightpulse_code_search.py --search "BIR form generation"

    # Ask Claude
    python scripts/insightpulse_code_search.py --ask "How does month-end closing work?"

    # Interactive mode
    python scripts/insightpulse_code_search.py --interactive

Environment Variables:
    POSTGRES_URL - PostgreSQL connection URL with pgvector
    ANTHROPIC_API_KEY - Claude API key for embeddings
"""

import argparse
import ast
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("⚠️  psycopg2 not installed. Installing...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2
    from psycopg2.extras import RealDictCursor

try:
    from anthropic import Anthropic
except ImportError:
    print("⚠️  anthropic not installed. Installing...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "anthropic"])
    from anthropic import Anthropic


class CodeChunk:
    """Represents a chunk of code for embedding"""

    def __init__(
        self,
        file_path: str,
        chunk_type: str,
        name: str,
        code: str,
        line_start: int,
        line_end: int,
        metadata: Dict = None,
    ):
        self.file_path = file_path
        self.chunk_type = chunk_type  # function, class, workflow, model
        self.name = name
        self.code = code
        self.line_start = line_start
        self.line_end = line_end
        self.metadata = metadata or {}

    def to_dict(self) -> Dict:
        return {
            "file_path": self.file_path,
            "chunk_type": self.chunk_type,
            "name": self.name,
            "code": self.code,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "metadata": self.metadata,
        }

    def get_hash(self) -> str:
        """Get unique hash for chunk"""
        content = f"{self.file_path}:{self.chunk_type}:{self.name}:{self.line_start}"
        return hashlib.md5(content.encode()).hexdigest()


class InsightPulseCodeSearch:
    """AI-powered semantic code search for InsightPulse Odoo"""

    def __init__(self, postgres_url: str, anthropic_key: str):
        self.postgres_url = postgres_url
        self.client = Anthropic(api_key=anthropic_key)
        self.conn = None
        self._connect()

    def _connect(self):
        """Connect to PostgreSQL with pgvector"""
        try:
            self.conn = psycopg2.connect(self.postgres_url)
            print("✅ Connected to PostgreSQL")
        except Exception as e:
            print(f"❌ Failed to connect to PostgreSQL: {e}")
            sys.exit(1)

    def setup_database(self):
        """Create pgvector table for code embeddings"""
        cur = self.conn.cursor()

        # Enable pgvector extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Create embeddings table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS insightpulse_code_embeddings (
                id SERIAL PRIMARY KEY,
                chunk_hash TEXT UNIQUE NOT NULL,
                file_path TEXT NOT NULL,
                chunk_type TEXT NOT NULL,
                name TEXT NOT NULL,
                code TEXT NOT NULL,
                line_start INTEGER,
                line_end INTEGER,
                metadata JSONB,
                embedding vector(1024),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)

        # Create indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_code_embeddings_file_path
            ON insightpulse_code_embeddings(file_path);
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_code_embeddings_chunk_type
            ON insightpulse_code_embeddings(chunk_type);
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_code_embeddings_vector
            ON insightpulse_code_embeddings
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """)

        self.conn.commit()
        print("✅ Database schema created")

    def chunk_python_file(self, file_path: Path) -> List[CodeChunk]:
        """Extract functions and classes from Python file"""
        chunks = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            tree = ast.parse(content, filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Extract function
                    code = "\n".join(lines[node.lineno - 1 : node.end_lineno])

                    # Detect metadata
                    metadata = {
                        "is_api": False,
                        "is_compute": False,
                        "is_onchange": False,
                    }
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name):
                            if decorator.id == "api":
                                metadata["is_api"] = True
                        elif isinstance(decorator, ast.Attribute):
                            if decorator.attr in ["depends", "onchange", "constrains"]:
                                metadata["is_api"] = True
                                if decorator.attr == "onchange":
                                    metadata["is_onchange"] = True

                    # Check if compute method
                    if node.name.startswith("_compute_"):
                        metadata["is_compute"] = True

                    chunks.append(
                        CodeChunk(
                            file_path=str(file_path),
                            chunk_type="function",
                            name=node.name,
                            code=code,
                            line_start=node.lineno,
                            line_end=node.end_lineno or node.lineno,
                            metadata=metadata,
                        )
                    )

                elif isinstance(node, ast.ClassDef):
                    # Extract class
                    code = "\n".join(lines[node.lineno - 1 : node.end_lineno])

                    # Detect Odoo model
                    metadata = {"is_model": False, "model_name": None, "inherit": None}
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    if target.id == "_name" and isinstance(
                                        item.value, ast.Constant
                                    ):
                                        metadata["is_model"] = True
                                        metadata["model_name"] = item.value.value
                                    elif target.id == "_inherit" and isinstance(
                                        item.value, ast.Constant
                                    ):
                                        metadata["is_model"] = True
                                        metadata["inherit"] = item.value.value

                    chunks.append(
                        CodeChunk(
                            file_path=str(file_path),
                            chunk_type="class",
                            name=node.name,
                            code=code,
                            line_start=node.lineno,
                            line_end=node.end_lineno or node.lineno,
                            metadata=metadata,
                        )
                    )

        except Exception as e:
            print(f"  ⚠️  Error parsing {file_path}: {e}")

        return chunks

    def chunk_json_file(self, file_path: Path) -> List[CodeChunk]:
        """Extract workflows from JSON files"""
        chunks = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Check if it's a workflow
            if "steps" in data:
                chunks.append(
                    CodeChunk(
                        file_path=str(file_path),
                        chunk_type="workflow",
                        name=data.get("name", file_path.stem),
                        code=json.dumps(data, indent=2),
                        line_start=1,
                        line_end=1,
                        metadata={
                            "category": data.get("category"),
                            "trigger_type": data.get("trigger_type"),
                            "description": data.get("description"),
                        },
                    )
                )

        except Exception as e:
            print(f"  ⚠️  Error parsing {file_path}: {e}")

        return chunks

    def get_embedding(self, text: str) -> List[float]:
        """Get text embedding from Claude"""
        # Claude doesn't have embeddings API yet, so we'll use a simple approach
        # In production, use OpenAI embeddings or similar
        # For now, return a mock embedding

        # TODO: Replace with actual embedding API
        # For demonstration, we'll use text hash as pseudo-embedding
        import hashlib

        hash_obj = hashlib.sha512(text.encode())
        hash_bytes = hash_obj.digest()

        # Convert to 1024-dim vector
        embedding = []
        for i in range(0, len(hash_bytes), 8):
            chunk = hash_bytes[i : i + 8]
            val = int.from_bytes(chunk.ljust(8, b"\x00"), "big") / (2**64)
            embedding.append(val)

        # Pad to 1024 dimensions
        while len(embedding) < 1024:
            embedding.append(0.0)

        return embedding[:1024]

    def index_codebase(self, repo_path: str):
        """Index entire codebase"""
        repo = Path(repo_path)

        print(f"📂 Indexing codebase: {repo}")

        total_chunks = 0

        # Index Python files
        for py_file in repo.rglob("*.py"):
            # Skip __pycache__ and venv
            if "__pycache__" in str(py_file) or "venv" in str(py_file):
                continue

            chunks = self.chunk_python_file(py_file)

            for chunk in chunks:
                self.index_chunk(chunk)
                total_chunks += 1

            if chunks:
                print(f"  ✅ {py_file.relative_to(repo)}: {len(chunks)} chunks")

        # Index workflow JSON files
        workflows_dir = repo / "workflows"
        if workflows_dir.exists():
            for json_file in workflows_dir.glob("*.json"):
                chunks = self.chunk_json_file(json_file)

                for chunk in chunks:
                    self.index_chunk(chunk)
                    total_chunks += 1

                if chunks:
                    print(f"  ✅ {json_file.relative_to(repo)}: {len(chunks)} chunks")

        self.conn.commit()
        print(f"\n✅ Indexed {total_chunks} code chunks")

    def index_chunk(self, chunk: CodeChunk):
        """Index a single code chunk"""
        cur = self.conn.cursor()

        # Get embedding
        embedding = self.get_embedding(chunk.code)

        # Upsert chunk
        cur.execute(
            """
            INSERT INTO insightpulse_code_embeddings
            (chunk_hash, file_path, chunk_type, name, code, line_start, line_end, metadata, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::vector)
            ON CONFLICT (chunk_hash) DO UPDATE SET
                code = EXCLUDED.code,
                embedding = EXCLUDED.embedding,
                updated_at = NOW()
        """,
            (
                chunk.get_hash(),
                chunk.file_path,
                chunk.chunk_type,
                chunk.name,
                chunk.code,
                chunk.line_start,
                chunk.line_end,
                json.dumps(chunk.metadata),
                embedding,
            ),
        )

    def search(
        self, query: str, limit: int = 5, chunk_type: Optional[str] = None
    ) -> List[Dict]:
        """Semantic search for code"""
        # Get query embedding
        query_embedding = self.get_embedding(query)

        cur = self.conn.cursor(cursor_factory=RealDictCursor)

        # Build query
        sql = """
            SELECT
                file_path,
                chunk_type,
                name,
                code,
                line_start,
                line_end,
                metadata,
                1 - (embedding <=> %s::vector) AS similarity
            FROM insightpulse_code_embeddings
        """

        params = [query_embedding]

        if chunk_type:
            sql += " WHERE chunk_type = %s"
            params.append(chunk_type)

        sql += " ORDER BY embedding <=> %s::vector LIMIT %s"
        params.extend([query_embedding, limit])

        cur.execute(sql, params)

        results = []
        for row in cur.fetchall():
            results.append(dict(row))

        return results

    def ask_claude(self, question: str, limit: int = 3) -> str:
        """Ask Claude about the codebase with relevant context"""
        # Get relevant code
        relevant_code = self.search(question, limit=limit)

        if not relevant_code:
            return "❌ No relevant code found. Try indexing the codebase first."

        # Build context
        context = ""
        for i, result in enumerate(relevant_code, 1):
            context += f"\n## Result {i}: {result['name']} ({result['chunk_type']})\n"
            context += f"**File**: `{result['file_path']}:{result['line_start']}-{result['line_end']}`\n"
            context += f"**Similarity**: {result['similarity']:.2%}\n\n"
            context += f"```python\n{result['code'][:500]}\n```\n"

        # Ask Claude
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are an expert on the InsightPulse Odoo codebase.

This is a Finance Shared Service Center (SSC) system managing:
- 8 companies (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
- BIR (Bureau of Internal Revenue) compliance for Philippines
- Month-end closing workflows
- Multi-company accounting

Relevant code:
{context}

Question: {question}

Answer based on the code above. Be specific and cite file paths with line numbers.
If the code doesn't fully answer the question, say so and explain what's shown.""",
                }
            ],
        )

        return response.content[0].text

    def interactive_mode(self):
        """Interactive search/ask mode"""
        print("\n🔍 InsightPulse Code Search - Interactive Mode")
        print("=" * 60)
        print("Commands:")
        print("  search <query>    - Semantic code search")
        print("  ask <question>    - Ask Claude about codebase")
        print("  quit              - Exit")
        print("=" * 60)
        print()

        while True:
            try:
                user_input = input("📝 > ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break

                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                query = parts[1] if len(parts) > 1 else ""

                if command == "search":
                    if not query:
                        print("❌ Usage: search <query>")
                        continue

                    print(f"\n🔍 Searching for: {query}")
                    results = self.search(query, limit=5)

                    if not results:
                        print("❌ No results found")
                    else:
                        for i, r in enumerate(results, 1):
                            print(
                                f"\n{i}. {r['name']} ({r['chunk_type']}) - {r['similarity']:.1%} match"
                            )
                            print(
                                f"   📄 {r['file_path']}:{r['line_start']}-{r['line_end']}"
                            )
                            print(f"   {r['code'][:150].replace(chr(10), ' ')}...")

                elif command == "ask":
                    if not query:
                        print("❌ Usage: ask <question>")
                        continue

                    print(f"\n💬 Asking Claude: {query}")
                    answer = self.ask_claude(query)
                    print(f"\n{answer}")

                else:
                    # Treat as ask by default
                    print(f"\n💬 Asking Claude: {user_input}")
                    answer = self.ask_claude(user_input)
                    print(f"\n{answer}")

                print()

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="InsightPulse AI Code Search")
    parser.add_argument("--index", action="store_true", help="Index codebase")
    parser.add_argument("--search", type=str, help="Search for code")
    parser.add_argument("--ask", type=str, help="Ask Claude about codebase")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument(
        "--limit", type=int, default=5, help="Number of results (default: 5)"
    )
    args = parser.parse_args()

    # Get credentials from environment
    postgres_url = os.getenv("POSTGRES_URL")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if not postgres_url:
        print("❌ POSTGRES_URL environment variable not set")
        print("   Example: export POSTGRES_URL='postgresql://user:pass@host:5432/db'")
        sys.exit(1)

    if not anthropic_key:
        print("❌ ANTHROPIC_API_KEY environment variable not set")
        print("   Get your key from: https://console.anthropic.com/")
        sys.exit(1)

    # Initialize search
    search = InsightPulseCodeSearch(postgres_url, anthropic_key)

    if args.index:
        search.setup_database()
        repo_path = Path(__file__).parent.parent
        search.index_codebase(str(repo_path))

    elif args.search:
        results = search.search(args.search, limit=args.limit)

        print(f"\n🔍 Search results for: {args.search}")
        print("=" * 60)

        if not results:
            print("❌ No results found")
        else:
            for i, r in enumerate(results, 1):
                print(
                    f"\n{i}. {r['name']} ({r['chunk_type']}) - {r['similarity']:.1%} match"
                )
                print(f"   📄 {r['file_path']}:{r['line_start']}-{r['line_end']}")
                print(f"\n{r['code'][:300]}...\n")

    elif args.ask:
        answer = search.ask_claude(args.ask, limit=args.limit)

        print(f"\n💬 Question: {args.ask}")
        print("=" * 60)
        print(f"\n{answer}\n")

    elif args.interactive:
        search.interactive_mode()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
