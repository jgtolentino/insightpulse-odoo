#!/usr/bin/env python3
"""
Agent Knowledge Base Indexer
Generates embeddings for agent-specific documentation and stores in Supabase
"""
import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
import openai
from supabase import create_client, Client

# ANSI colors
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'

@dataclass
class Document:
    agent_domain: str
    content_type: str
    title: str
    content: str
    metadata: Dict[str, Any]
    source_url: str = ""

class AgentKnowledgeIndexer:
    def __init__(self, supabase_url: str, supabase_key: str, openai_api_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        openai.api_key = openai_api_key
        self.embedding_model = "text-embedding-3-small"

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API"""
        try:
            response = openai.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"{RED}Error generating embedding: {e}{NC}")
            return None

    def index_document(self, doc: Document) -> bool:
        """Index a single document"""
        print(f"{YELLOW}Indexing: {doc.title} ({doc.agent_domain}/{doc.content_type}){NC}")

        # Generate embedding for content
        embedding = self.generate_embedding(doc.content)
        if not embedding:
            return False

        # Insert into Supabase
        try:
            data = {
                "agent_domain": doc.agent_domain,
                "content_type": doc.content_type,
                "title": doc.title,
                "content": doc.content,
                "embedding": embedding,
                "metadata": json.dumps(doc.metadata) if isinstance(doc.metadata, dict) else doc.metadata,
                "source_url": doc.source_url
            }

            result = self.supabase.table("agent_domain_embeddings").insert(data).execute()

            if result.data:
                print(f"{GREEN}✓ Indexed successfully (ID: {result.data[0]['id']}){NC}")
                return True
            else:
                print(f"{RED}✗ Failed to insert document{NC}")
                return False

        except Exception as e:
            print(f"{RED}✗ Error indexing document: {e}{NC}")
            return False

    def index_from_file(self, file_path: Path, agent_domain: str, content_type: str) -> int:
        """Index documents from a JSON file"""
        print(f"{YELLOW}Loading documents from {file_path}{NC}")

        try:
            with open(file_path, 'r') as f:
                docs_data = json.load(f)

            if not isinstance(docs_data, list):
                docs_data = [docs_data]

            indexed_count = 0
            for doc_data in docs_data:
                doc = Document(
                    agent_domain=doc_data.get("agent_domain", agent_domain),
                    content_type=doc_data.get("content_type", content_type),
                    title=doc_data.get("title", "Untitled"),
                    content=doc_data.get("content", ""),
                    metadata=doc_data.get("metadata", {}),
                    source_url=doc_data.get("source_url", "")
                )

                if self.index_document(doc):
                    indexed_count += 1

            return indexed_count

        except Exception as e:
            print(f"{RED}Error loading file {file_path}: {e}{NC}")
            return 0

    def index_directory(self, directory: Path, agent_domain: str, content_type: str) -> int:
        """Index all JSON files in a directory"""
        print(f"{YELLOW}Indexing directory: {directory}{NC}")

        if not directory.exists():
            print(f"{RED}Error: Directory not found: {directory}{NC}")
            return 0

        total_indexed = 0
        for json_file in directory.glob("*.json"):
            total_indexed += self.index_from_file(json_file, agent_domain, content_type)

        return total_indexed

    def get_statistics(self) -> Dict[str, Any]:
        """Get indexing statistics from database"""
        try:
            result = self.supabase.table("agent_knowledge_stats").select("*").execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"{RED}Error fetching statistics: {e}{NC}")
            return []

def main():
    parser = argparse.ArgumentParser(description="Index agent-specific knowledge base")
    parser.add_argument("--source", required=True, help="Source file or directory to index")
    parser.add_argument("--agent", required=True, choices=["odoo_developer", "finance_ssc_expert", "bi_architect", "devops_engineer", "orchestrator"], help="Agent domain")
    parser.add_argument("--content-type", required=True, choices=["odoo_doc", "bir_regulation", "superset_doc", "infra_doc", "oca_guideline", "general"], help="Content type")
    parser.add_argument("--embedding-model", default="text-embedding-3-small", help="OpenAI embedding model")

    args = parser.parse_args()

    # Get credentials from environment
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not all([supabase_url, supabase_key, openai_api_key]):
        print(f"{RED}Error: Missing required environment variables:{NC}")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_SERVICE_ROLE_KEY")
        print("  - OPENAI_API_KEY")
        sys.exit(1)

    # Initialize indexer
    indexer = AgentKnowledgeIndexer(supabase_url, supabase_key, openai_api_key)
    indexer.embedding_model = args.embedding_model

    print(f"{GREEN}=== Agent Knowledge Base Indexer ==={NC}")
    print(f"Agent: {args.agent}")
    print(f"Content Type: {args.content_type}")
    print(f"Embedding Model: {args.embedding_model}")
    print()

    # Index source
    source_path = Path(args.source)
    if source_path.is_file():
        indexed = indexer.index_from_file(source_path, args.agent, args.content_type)
    elif source_path.is_dir():
        indexed = indexer.index_directory(source_path, args.agent, args.content_type)
    else:
        print(f"{RED}Error: Source not found: {args.source}{NC}")
        sys.exit(1)

    # Print statistics
    print(f"\n{GREEN}=== Indexing Complete ==={NC}")
    print(f"Documents indexed: {indexed}")

    stats = indexer.get_statistics()
    if stats:
        print(f"\n{YELLOW}Knowledge Base Statistics:{NC}")
        for stat in stats:
            print(f"  {stat['agent_domain']}/{stat['content_type']}: {stat['document_count']} documents")

if __name__ == "__main__":
    main()
