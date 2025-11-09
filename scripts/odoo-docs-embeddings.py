#!/usr/bin/env python3
"""
Odoo Documentation Embeddings Generator
Fetches Odoo 19.0 documentation and creates embeddings for semantic search

Requirements:
- PostgreSQL with pgvector extension (Supabase)
- OpenAI API key (for embeddings)
- BeautifulSoup4 (for HTML parsing)
- requests (for fetching docs)
"""

import os
import sys
import json
import hashlib
from typing import List, Dict, Tuple
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import execute_values

# Configuration
ODOO_DOCS_BASE = "https://www.odoo.com/documentation/19.0/developer/reference.html"
ODOO_VERSION = "19.0"
CHUNK_SIZE = 500  # words per chunk
CHUNK_OVERLAP = 50  # word overlap between chunks

# Database configuration (Supabase)
DB_CONFIG = {
    'host': 'aws-1-us-east-1.pooler.supabase.com',
    'port': 6543,
    'database': 'postgres',
    'user': 'postgres.spdtwktxdalcfigzeqrz',
    'password': os.getenv('SUPABASE_PASSWORD'),
    'sslmode': 'require'
}

# OpenAI configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dimensions, $0.02/1M tokens


class OdooDocsEmbedder:
    """Main class for Odoo documentation embedding pipeline"""
    
    def __init__(self):
        self.base_url = ODOO_DOCS_BASE
        self.visited_urls = set()
        self.docs_content = []
        self.conn = None
        
    def connect_db(self):
        """Connect to PostgreSQL with pgvector"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            print("✅ Connected to database")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def setup_schema(self):
        """Create tables for storing embeddings"""
        schema_sql = """
        -- Enable pgvector extension
        CREATE EXTENSION IF NOT EXISTS vector;
        
        -- Odoo documentation embeddings table
        CREATE TABLE IF NOT EXISTS odoo_docs_embeddings (
            id SERIAL PRIMARY KEY,
            url TEXT NOT NULL,
            section_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            content_hash TEXT UNIQUE NOT NULL,
            embedding vector(1536),
            metadata JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        -- Create indexes for efficient search
        CREATE INDEX IF NOT EXISTS idx_odoo_docs_url ON odoo_docs_embeddings(url);
        CREATE INDEX IF NOT EXISTS idx_odoo_docs_hash ON odoo_docs_embeddings(content_hash);
        CREATE INDEX IF NOT EXISTS idx_odoo_docs_embedding ON odoo_docs_embeddings 
            USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
        
        -- Metadata index for filtering
        CREATE INDEX IF NOT EXISTS idx_odoo_docs_metadata ON odoo_docs_embeddings USING gin(metadata);
        """
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(schema_sql)
                self.conn.commit()
            print("✅ Database schema created")
            return True
        except Exception as e:
            print(f"❌ Schema creation failed: {e}")
            return False
    
    def fetch_documentation(self, url: str, max_depth: int = 3, current_depth: int = 0) -> List[Dict]:
        """
        Recursively fetch Odoo documentation pages
        
        Args:
            url: Starting URL
            max_depth: Maximum recursion depth
            current_depth: Current recursion level
            
        Returns:
            List of documentation sections
        """
        if current_depth > max_depth or url in self.visited_urls:
            return []
        
        self.visited_urls.add(url)
        print(f"📄 Fetching: {url} (depth: {current_depth})")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            print(f"❌ Failed to fetch {url}: {e}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        sections = []
        
        # Extract main content
        main_content = soup.find('div', class_='document') or soup.find('main')
        if not main_content:
            print(f"⚠️  No main content found at {url}")
            return []
        
        # Extract sections with headings
        for heading in main_content.find_all(['h1', 'h2', 'h3', 'h4']):
            section_id = heading.get('id', '')
            title = heading.get_text(strip=True)
            
            # Get content until next heading
            content_parts = []
            for sibling in heading.find_next_siblings():
                if sibling.name in ['h1', 'h2', 'h3', 'h4']:
                    break
                content_parts.append(sibling.get_text(strip=True))
            
            content = ' '.join(content_parts)
            
            if content.strip():
                sections.append({
                    'url': url,
                    'section_id': section_id,
                    'title': title,
                    'content': content,
                    'metadata': {
                        'odoo_version': ODOO_VERSION,
                        'heading_level': heading.name,
                        'doc_type': 'developer_reference'
                    }
                })
        
        # Find links to other documentation pages (same domain only)
        if current_depth < max_depth:
            for link in main_content.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                # Only follow Odoo documentation links
                if 'odoo.com/documentation' in full_url and full_url not in self.visited_urls:
                    sections.extend(self.fetch_documentation(full_url, max_depth, current_depth + 1))
        
        return sections
    
    def chunk_content(self, content: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
        """
        Split content into overlapping chunks
        
        Args:
            content: Text to chunk
            chunk_size: Target words per chunk
            overlap: Overlapping words between chunks
            
        Returns:
            List of text chunks
        """
        words = content.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using OpenAI API
        
        Args:
            text: Text to embed
            
        Returns:
            1536-dimensional embedding vector
        """
        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "input": text,
            "model": EMBEDDING_MODEL
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result['data'][0]['embedding']
        except Exception as e:
            print(f"❌ Embedding generation failed: {e}")
            return None
    
    def store_embeddings(self, sections: List[Dict]):
        """
        Store documentation sections with embeddings in database
        
        Args:
            sections: List of documentation sections
        """
        if not self.conn:
            print("❌ No database connection")
            return
        
        insert_sql = """
        INSERT INTO odoo_docs_embeddings (url, section_id, title, content, content_hash, embedding, metadata)
        VALUES %s
        ON CONFLICT (content_hash) DO UPDATE SET
            updated_at = NOW(),
            embedding = EXCLUDED.embedding
        """
        
        values = []
        for section in sections:
            # Chunk large content
            chunks = self.chunk_content(section['content'])
            
            for i, chunk in enumerate(chunks):
                # Generate content hash for deduplication
                content_hash = hashlib.sha256(chunk.encode()).hexdigest()
                
                # Generate embedding
                embedding = self.generate_embedding(chunk)
                if not embedding:
                    continue
                
                # Prepare metadata
                metadata = section['metadata'].copy()
                metadata['chunk_index'] = i
                metadata['total_chunks'] = len(chunks)
                
                values.append((
                    section['url'],
                    section['section_id'],
                    section['title'],
                    chunk,
                    content_hash,
                    embedding,
                    json.dumps(metadata)
                ))
        
        try:
            with self.conn.cursor() as cur:
                execute_values(cur, insert_sql, values)
                self.conn.commit()
            print(f"✅ Stored {len(values)} embeddings")
        except Exception as e:
            print(f"❌ Storage failed: {e}")
            self.conn.rollback()
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Perform semantic search on Odoo documentation
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of relevant documentation sections
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        if not query_embedding:
            return []
        
        search_sql = """
        SELECT url, section_id, title, content, metadata,
               1 - (embedding <=> %s::vector) AS similarity
        FROM odoo_docs_embeddings
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(search_sql, (query_embedding, query_embedding, top_k))
                results = []
                for row in cur.fetchall():
                    results.append({
                        'url': row[0],
                        'section_id': row[1],
                        'title': row[2],
                        'content': row[3],
                        'metadata': row[4],
                        'similarity': float(row[5])
                    })
                return results
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def run_pipeline(self):
        """Execute complete embedding pipeline"""
        print("🚀 Odoo Documentation Embeddings Pipeline")
        print("=" * 50)
        
        # Step 1: Connect to database
        if not self.connect_db():
            return False
        
        # Step 2: Setup schema
        if not self.setup_schema():
            return False
        
        # Step 3: Fetch documentation
        print("\n📚 Fetching Odoo documentation...")
        sections = self.fetch_documentation(self.base_url, max_depth=2)
        print(f"✅ Fetched {len(sections)} documentation sections")
        
        if not sections:
            print("❌ No documentation sections found")
            return False
        
        # Step 4: Generate and store embeddings
        print("\n🧠 Generating embeddings...")
        self.store_embeddings(sections)
        
        # Step 5: Test semantic search
        print("\n🔍 Testing semantic search...")
        test_query = "How do I create a custom Odoo model?"
        results = self.semantic_search(test_query, top_k=3)
        
        print(f"\nQuery: {test_query}")
        print(f"Results: {len(results)}")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']} (similarity: {result['similarity']:.2%})")
            print(f"   URL: {result['url']}")
            print(f"   Content: {result['content'][:200]}...")
        
        print("\n✅ Pipeline complete!")
        return True


def main():
    """Main entry point"""
    # Validate environment
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    if not DB_CONFIG['password']:
        print("❌ SUPABASE_PASSWORD environment variable not set")
        sys.exit(1)
    
    # Run pipeline
    embedder = OdooDocsEmbedder()
    success = embedder.run_pipeline()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
