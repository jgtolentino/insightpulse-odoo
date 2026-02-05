"""
Celery Tasks for Visual Compliance Agent RAG/CAG Pipeline
Tasks for knowledge graph ingestion, embedding generation, and validation
"""

from celery import shared_task, group, chain
from typing import Dict, List, Any
import os
import hashlib
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import dependencies (will be installed in Dockerfile.celery)
try:
    import openai
    from supabase import create_client, Client
    import git
    from bs4 import BeautifulSoup
    import markdown
    import requests
except ImportError as e:
    logger.warning(f"Import error: {e}. Some tasks may not work until dependencies are installed.")

# Configuration from environment
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize clients
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
else:
    logger.warning("Supabase credentials not configured")
    supabase = None

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
else:
    logger.warning("OpenAI API key not configured")

# ===========================================================================
# 1. INGESTION TASKS (Queue: ingestion)
# ===========================================================================

@shared_task(bind=True, name='visual_compliance.tasks.ingest_oca_repository')
def ingest_oca_repository(self, repository: str, paths: List[str] = None) -> Dict[str, Any]:
    """
    Ingest OCA repository documentation into knowledge graph

    Args:
        repository: GitHub repository (e.g., 'OCA/maintainer-tools')
        paths: Optional list of specific paths to ingest (e.g., ['docs/', 'template/'])

    Returns:
        Dict with ingestion stats (total_files, total_chunks, errors)
    """
    logger.info(f"Starting ingestion for repository: {repository}")

    try:
        # Clone repository to temp directory
        repo_dir = f"/tmp/oca_repos/{repository.replace('/', '_')}"
        if not Path(repo_dir).exists():
            logger.info(f"Cloning repository: {repository}")
            git.Repo.clone_from(
                f"https://github.com/{repository}.git",
                repo_dir,
                depth=1  # Shallow clone for speed
            )

        # Find all markdown/rst files
        extensions = ['.md', '.rst', '.txt']
        files_to_process = []

        search_paths = paths if paths else ['.']
        for search_path in search_paths:
            full_path = Path(repo_dir) / search_path
            if full_path.is_dir():
                for ext in extensions:
                    files_to_process.extend(full_path.rglob(f'*{ext}'))

        logger.info(f"Found {len(files_to_process)} files to process")

        # Process files in parallel using Celery group
        tasks = []
        for file_path in files_to_process:
            relative_path = str(file_path.relative_to(repo_dir))
            tasks.append(
                process_oca_document.s(repository, relative_path, str(file_path))
            )

        # Execute all tasks in parallel
        job = group(tasks)
        result = job.apply_async()

        # Wait for all tasks to complete
        results = result.get(timeout=600)  # 10 minute timeout

        total_chunks = sum(r['chunks_created'] for r in results if r['success'])
        total_errors = sum(1 for r in results if not r['success'])

        return {
            'repository': repository,
            'total_files': len(files_to_process),
            'total_chunks': total_chunks,
            'errors': total_errors,
            'status': 'completed'
        }

    except Exception as e:
        logger.error(f"Error ingesting repository {repository}: {e}")
        self.retry(exc=e, countdown=300, max_retries=3)


@shared_task(bind=True, name='visual_compliance.tasks.process_oca_document')
def process_oca_document(self, repository: str, doc_path: str, file_path: str) -> Dict[str, Any]:
    """
    Process a single OCA document and create chunks in knowledge graph

    Args:
        repository: GitHub repository
        doc_path: Path within repository
        file_path: Absolute file path on disk

    Returns:
        Dict with processing stats
    """
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Generate content hash for deduplication
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Determine content type
        content_type = Path(file_path).suffix[1:]  # Remove leading dot

        # Parse sections (hierarchical chunking)
        chunks = chunk_markdown_document(content, max_chunk_size=1500)

        # Determine compliance category from doc path
        compliance_category = infer_compliance_category(doc_path)

        # Determine severity
        severity = infer_severity(doc_path, content)

        # Insert chunks into Supabase
        chunks_created = 0
        for idx, chunk in enumerate(chunks):
            chunk_hash = hashlib.sha256(chunk.encode()).hexdigest()

            # Check if chunk already exists
            existing = supabase.table('oca_guidelines').select('id').eq('content_hash', chunk_hash).execute()
            if existing.data:
                logger.debug(f"Chunk already exists: {chunk_hash[:8]}")
                continue

            # Insert new chunk
            supabase.table('oca_guidelines').insert({
                'repository': repository,
                'doc_path': doc_path,
                'section': f"Section {idx + 1}",
                'url': f"https://github.com/{repository}/blob/main/{doc_path}",
                'content_type': content_type,
                'raw_content': chunk,
                'content_hash': chunk_hash,
                'chunk_index': idx,
                'chunk_total': len(chunks),
                'compliance_category': compliance_category,
                'severity': severity,
                'auto_fixable': False,  # Will be determined later by LLM
            }).execute()

            chunks_created += 1

        return {
            'success': True,
            'doc_path': doc_path,
            'chunks_created': chunks_created
        }

    except Exception as e:
        logger.error(f"Error processing document {doc_path}: {e}")
        return {'success': False, 'doc_path': doc_path, 'error': str(e)}


@shared_task(bind=True, name='visual_compliance.tasks.ingest_odoo_docs')
def ingest_odoo_docs(self, doc_urls: List[str] = None) -> Dict[str, Any]:
    """
    Ingest Odoo 18.0 official documentation

    Args:
        doc_urls: Optional list of specific doc URLs (otherwise scrapes all)

    Returns:
        Dict with ingestion stats
    """
    logger.info("Starting Odoo docs ingestion")

    # Default URLs if none provided
    if not doc_urls:
        base_url = "https://www.odoo.com/documentation/18.0"
        doc_urls = [
            f"{base_url}/developer/",
            f"{base_url}/applications/",
            f"{base_url}/administration/",
        ]

    tasks = []
    for url in doc_urls:
        tasks.append(scrape_odoo_doc_page.s(url))

    # Execute all tasks in parallel
    job = group(tasks)
    result = job.apply_async()
    results = result.get(timeout=600)

    total_chunks = sum(r['chunks_created'] for r in results if r['success'])
    total_errors = sum(1 for r in results if not r['success'])

    return {
        'total_urls': len(doc_urls),
        'total_chunks': total_chunks,
        'errors': total_errors,
        'status': 'completed'
    }


@shared_task(bind=True, name='visual_compliance.tasks.scrape_odoo_doc_page')
def scrape_odoo_doc_page(self, url: str) -> Dict[str, Any]:
    """Scrape a single Odoo documentation page"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract main content
        main_content = soup.find('main') or soup.find('article')
        if not main_content:
            return {'success': False, 'url': url, 'error': 'No main content found'}

        # Convert to markdown
        content = main_content.get_text(strip=True)
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Chunk content
        chunks = chunk_markdown_document(content, max_chunk_size=1500)

        # Determine doc section and category from URL
        doc_section, doc_category = infer_odoo_doc_category(url)

        # Insert chunks
        chunks_created = 0
        for idx, chunk in enumerate(chunks):
            chunk_hash = hashlib.sha256(chunk.encode()).hexdigest()

            existing = supabase.table('odoo_official_docs').select('id').eq('content_hash', chunk_hash).execute()
            if existing.data:
                continue

            supabase.table('odoo_official_docs').insert({
                'doc_section': doc_section,
                'doc_category': doc_category,
                'title': soup.find('h1').get_text(strip=True) if soup.find('h1') else 'Untitled',
                'url': url,
                'content_type': 'html',
                'raw_content': chunk,
                'content_hash': chunk_hash,
                'chunk_index': idx,
                'chunk_total': len(chunks),
                'odoo_version': '18.0',
                'applies_to_ce': True,
                'applies_to_enterprise': False,
            }).execute()

            chunks_created += 1

        return {'success': True, 'url': url, 'chunks_created': chunks_created}

    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return {'success': False, 'url': url, 'error': str(e)}


# ===========================================================================
# 2. EMBEDDING GENERATION TASKS (Queue: embedding)
# ===========================================================================

@shared_task(bind=True, name='visual_compliance.tasks.generate_embeddings')
def generate_embeddings(self, table_name: str, batch_size: int = 100) -> Dict[str, Any]:
    """
    Generate embeddings for all rows in a table that don't have embeddings yet

    Args:
        table_name: 'oca_guidelines', 'odoo_official_docs', or 'oca_module_examples'
        batch_size: Number of rows to process at once

    Returns:
        Dict with embedding stats
    """
    logger.info(f"Generating embeddings for table: {table_name}")

    try:
        # Get all rows without embeddings
        response = supabase.table(table_name).select('id', 'raw_content').is_('embedding', 'null').limit(batch_size).execute()
        rows = response.data

        if not rows:
            logger.info(f"No rows to process in {table_name}")
            return {'status': 'completed', 'embeddings_generated': 0}

        logger.info(f"Processing {len(rows)} rows from {table_name}")

        # Generate embeddings in batch
        texts = [row['raw_content'] for row in rows]
        embeddings_response = openai.embeddings.create(
            model="text-embedding-3-large",
            input=texts,
            dimensions=3072
        )

        # Update rows with embeddings
        embeddings_generated = 0
        for row, embedding_data in zip(rows, embeddings_response.data):
            embedding = embedding_data.embedding

            supabase.table(table_name).update({
                'embedding': embedding
            }).eq('id', row['id']).execute()

            embeddings_generated += 1

        return {
            'status': 'completed',
            'table_name': table_name,
            'embeddings_generated': embeddings_generated
        }

    except Exception as e:
        logger.error(f"Error generating embeddings for {table_name}: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True, name='visual_compliance.tasks.deduplicate_guidelines')
def deduplicate_guidelines(self) -> Dict[str, Any]:
    """
    Find and mark duplicate guidelines using semantic similarity
    Uses the mark_duplicate_guidelines() Postgres function
    """
    logger.info("Starting deduplication process")

    try:
        result = supabase.rpc('mark_duplicate_guidelines', {'similarity_threshold': 0.95}).execute()

        duplicates_marked = len(result.data)
        logger.info(f"Marked {duplicates_marked} duplicates")

        return {
            'status': 'completed',
            'duplicates_marked': duplicates_marked
        }

    except Exception as e:
        logger.error(f"Error deduplicating guidelines: {e}")
        return {'status': 'error', 'error': str(e)}


# ===========================================================================
# 3. VALIDATION TASKS (Queue: validation)
# ===========================================================================

@shared_task(bind=True, name='visual_compliance.tasks.validate_module')
def validate_module(self, module_path: str, session_id: str) -> Dict[str, Any]:
    """
    Validate a single Odoo module using RAG-enhanced validation

    Args:
        module_path: Absolute path to module directory
        session_id: Compliance session UUID

    Returns:
        Dict with validation results
    """
    logger.info(f"Validating module: {module_path}")

    # This will integrate with existing validators in visual_compliance.validators
    # For now, return placeholder
    return {
        'module_path': module_path,
        'session_id': session_id,
        'status': 'not_implemented_yet'
    }


# ===========================================================================
# 4. SCHEDULED TASKS (Celery Beat)
# ===========================================================================

@shared_task(name='visual_compliance.tasks.refresh_knowledge_graph')
def refresh_knowledge_graph():
    """
    Daily refresh of knowledge graph (called by Celery Beat)
    Re-ingests all 7 repositories to catch updates
    """
    logger.info("Starting knowledge graph refresh")

    repositories = [
        ('OCA/OpenUpgrade', ['docs/', 'scripts/']),
        ('OCA/oca-github-bot', ['docs/']),
        ('OCA/maintainer-tools', ['docs/', 'template/']),
        ('OCA/OCB', ['README.md']),
        ('OCA/odoo-community.org', ['website/Contribution/']),
        ('odoo/odoo', ['doc/developer/', 'doc/administration/']),
        ('odoo/documentation', ['content/developer/', 'content/applications/']),
    ]

    tasks = []
    for repo, paths in repositories:
        tasks.append(ingest_oca_repository.s(repo, paths))

    # Chain tasks: ingest -> generate embeddings -> deduplicate
    workflow = chain(
        group(tasks),
        generate_embeddings.s('oca_guidelines'),
        generate_embeddings.s('odoo_official_docs'),
        deduplicate_guidelines.s()
    )

    result = workflow.apply_async()
    return {'status': 'refresh_started', 'job_id': result.id}


@shared_task(name='visual_compliance.tasks.update_quality_scores')
def update_quality_scores():
    """
    Update quality scores for knowledge graph entries
    Uses update_quality_scores() Postgres function
    """
    logger.info("Updating quality scores")

    try:
        # Call the Postgres function from 010_knowledge_pipeline.sql
        supabase.rpc('update_quality_scores').execute()

        return {'status': 'completed'}

    except Exception as e:
        logger.error(f"Error updating quality scores: {e}")
        return {'status': 'error', 'error': str(e)}


# ===========================================================================
# UTILITY FUNCTIONS
# ===========================================================================

def chunk_markdown_document(content: str, max_chunk_size: int = 1500) -> List[str]:
    """
    Chunk markdown document while preserving structure
    Splits on headings, paragraphs, code blocks
    """
    # Simple chunking by splitting on double newlines
    # TODO: Implement smarter hierarchical chunking that respects markdown structure
    paragraphs = content.split('\n\n')

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) > max_chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            current_chunk += "\n\n" + para

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def infer_compliance_category(doc_path: str) -> str:
    """Infer compliance category from document path"""
    doc_path_lower = doc_path.lower()

    if 'manifest' in doc_path_lower or '__manifest__' in doc_path_lower:
        return 'manifest'
    elif 'python' in doc_path_lower or 'coding' in doc_path_lower or 'guidelines' in doc_path_lower:
        return 'python'
    elif 'xml' in doc_path_lower or 'view' in doc_path_lower:
        return 'xml'
    elif 'security' in doc_path_lower or 'access' in doc_path_lower:
        return 'security'
    elif 'structure' in doc_path_lower or 'organization' in doc_path_lower:
        return 'structure'
    elif 'depend' in doc_path_lower or 'requirements' in doc_path_lower:
        return 'dependencies'
    elif 'test' in doc_path_lower or 'ci' in doc_path_lower or 'pre-commit' in doc_path_lower:
        return 'tools'
    else:
        return 'structure'  # Default


def infer_severity(doc_path: str, content: str) -> str:
    """Infer severity from document path and content"""
    content_lower = content.lower()
    doc_path_lower = doc_path.lower()

    # CRITICAL keywords
    if any(word in content_lower for word in ['must', 'required', 'critical', 'security']):
        return 'CRITICAL'

    # HIGH keywords
    elif any(word in content_lower for word in ['should', 'important', 'recommended']):
        return 'HIGH'

    # MEDIUM keywords
    elif any(word in content_lower for word in ['could', 'optional', 'consider']):
        return 'MEDIUM'

    # Default to LOW
    else:
        return 'LOW'


def infer_odoo_doc_category(url: str) -> tuple:
    """Infer Odoo doc section and category from URL"""
    if '/developer/' in url:
        doc_section = 'developer'

        if '/manifests' in url:
            doc_category = 'manifests'
        elif '/orm' in url:
            doc_category = 'orm'
        elif '/views' in url:
            doc_category = 'views'
        elif '/security' in url:
            doc_category = 'security'
        elif '/testing' in url:
            doc_category = 'testing'
        else:
            doc_category = 'general'

    elif '/applications/' in url:
        doc_section = 'applications'
        doc_category = 'apps'

    elif '/administration/' in url:
        doc_section = 'administration'
        doc_category = 'admin'

    else:
        doc_section = 'general'
        doc_category = 'general'

    return doc_section, doc_category
