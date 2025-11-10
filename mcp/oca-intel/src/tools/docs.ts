/**
 * Documentation Generation Tool
 * Uses gittodoc.com for automated repository documentation
 */

import axios from 'axios';
import * as cheerio from 'cheerio';

interface DocsArgs {
  repo_url: string;
  branch?: string;
  module?: string;
}

export async function generateModuleDocs(args: DocsArgs) {
  const { repo_url, branch = '18.0', module } = args;

  try {
    // Try gittodoc.com first
    const gittodocDocs = await generateViaGitToDoc(repo_url, branch);

    // Fallback: Scrape README directly from GitHub
    const fallbackDocs = gittodocDocs.length === 0
      ? await scrapeGitHubREADME(repo_url, branch, module)
      : '';

    const documentation = gittodocDocs || fallbackDocs;

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            repo_url,
            branch,
            module,
            documentation_length: documentation.length,
            documentation,
            generated_at: new Date().toISOString(),
            source: gittodocDocs ? 'gittodoc.com' : 'github_direct',
          }, null, 2),
        },
      ],
    };
  } catch (error) {
    throw new Error(`Documentation generation failed: ${error instanceof Error ? error.message : String(error)}`);
  }
}

/**
 * Generate docs using gittodoc.com
 */
async function generateViaGitToDoc(
  repoUrl: string,
  branch: string
): Promise<string> {
  try {
    // gittodoc.com API (example - adjust based on actual API)
    const response = await axios.post(
      'https://api.gittodoc.com/generate',
      {
        url: repoUrl,
        branch,
        format: 'markdown',
      },
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 30000, // 30 seconds for doc generation
      }
    );

    return response.data.documentation || response.data.content || '';
  } catch (error) {
    console.error('gittodoc.com failed, using fallback');
    return '';
  }
}

/**
 * Fallback: Scrape README from GitHub
 */
async function scrapeGitHubREADME(
  repoUrl: string,
  branch: string,
  module?: string
): Promise<string> {
  try {
    // Extract org and repo from URL
    const match = repoUrl.match(/github\.com\/([^/]+)\/([^/]+)/);
    if (!match) {
      throw new Error('Invalid GitHub URL');
    }

    const [, org, repo] = match;

    // Build README URL
    const readmePath = module
      ? `${module}/README.md`
      : 'README.md';

    const rawUrl = `https://raw.githubusercontent.com/${org}/${repo}/${branch}/${readmePath}`;

    const response = await axios.get(rawUrl, { timeout: 10000 });

    return `# ${module || repo} Documentation\n\n${response.data}`;
  } catch (error) {
    return `Documentation not available for ${repoUrl}${module ? `/${module}` : ''}`;
  }
}

/**
 * Parse module manifest for metadata
 */
async function parseModuleManifest(
  org: string,
  repo: string,
  branch: string,
  module: string
): Promise<any> {
  try {
    const manifestUrl = `https://raw.githubusercontent.com/${org}/${repo}/${branch}/${module}/__manifest__.py`;

    const response = await axios.get(manifestUrl, { timeout: 5000 });

    // Basic Python dict parsing (simplified)
    const content = response.data;

    // Extract key fields using regex
    const name = content.match(/'name'\s*:\s*'([^']+)'/)?.[1];
    const version = content.match(/'version'\s*:\s*'([^']+)'/)?.[1];
    const author = content.match(/'author'\s*:\s*'([^']+)'/)?.[1];
    const license = content.match(/'license'\s*:\s*'([^']+)'/)?.[1];
    const summary = content.match(/'summary'\s*:\s*'([^']+)'/)?.[1];
    const depends = content.match(/'depends'\s*:\s*\[([^\]]+)\]/)?.[1];

    return {
      name,
      version,
      author,
      license,
      summary,
      depends: depends
        ? depends.split(',').map(d => d.trim().replace(/['"]/g, ''))
        : [],
    };
  } catch (error) {
    return null;
  }
}
