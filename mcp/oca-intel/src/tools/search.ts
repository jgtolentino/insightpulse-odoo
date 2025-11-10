/**
 * OCA Module Search Tool
 * Uses gitsearchai.com for advanced GitHub repository search
 */

import axios from 'axios';

interface SearchArgs {
  query: string;
  version?: string;
  limit?: number;
}

interface SearchResult {
  repo: string;
  module: string;
  description: string;
  stars: number;
  branch_status: '18.0' | 'unavailable';
  url: string;
}

export async function searchOCAModules(args: SearchArgs) {
  const { query, version = '18.0', limit = 10 } = args;

  try {
    // Primary: gitsearchai.com API
    const gitsearchResults = await searchViaGitSearchAI(query, version, limit);

    // Fallback: Direct GitHub API search
    const githubResults = gitsearchResults.length === 0
      ? await searchViaGitHub API(query, version, limit)
      : [];

    const results = [...gitsearchResults, ...githubResults].slice(0, limit);

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            query,
            version,
            results_count: results.length,
            results: results.map(r => ({
              ...r,
              install_command: `odoo-bin -d database -i ${r.module} --stop-after-init`,
            })),
            search_tips: [
              'Use specific terms: "accounting reports" not "reports"',
              'Add domain keywords: "warehouse management", "quality control"',
              'Try OCA repository names: "account-financial-reporting"',
            ],
          }, null, 2),
        },
      ],
    };
  } catch (error) {
    throw new Error(`Search failed: ${error instanceof Error ? error.message : String(error)}`);
  }
}

/**
 * Search using gitsearchai.com
 */
async function searchViaGitSearchAI(
  query: string,
  version: string,
  limit: number
): Promise<SearchResult[]> {
  try {
    // gitsearchai.com search (example - adjust based on actual API)
    const searchQuery = `${query} org:OCA language:Python ${version}`;

    const response = await axios.get('https://api.gitsearchai.com/search', {
      params: {
        q: searchQuery,
        type: 'repositories',
        per_page: limit,
      },
      timeout: 10000,
    });

    // Parse results (adjust based on actual API response format)
    return (response.data.items || []).map((item: any) => ({
      repo: item.full_name || '',
      module: item.name || '',
      description: item.description || '',
      stars: item.stargazers_count || 0,
      branch_status: '18.0' as const,
      url: item.html_url || '',
    }));
  } catch (error) {
    console.error('gitsearchai.com search failed, using fallback');
    return [];
  }
}

/**
 * Fallback: GitHub API search
 */
async function searchViaGitHubAPI(
  query: string,
  version: string,
  limit: number
): Promise<SearchResult[]> {
  const OCA_REPOS = [
    'account-financial-reporting',
    'account-financial-tools',
    'server-tools',
    'web',
    'reporting-engine',
    'dms',
    'helpdesk',
    'purchase-workflow',
    'sale-workflow',
    'hr-payroll',
    'hr-attendance',
    'manufacture',
    'stock-logistics-workflow',
    'project',
  ];

  const results: SearchResult[] = [];

  // Search within known OCA repos
  for (const repo of OCA_REPOS) {
    try {
      const response = await axios.get(
        `https://api.github.com/repos/OCA/${repo}`,
        {
          headers: {
            Accept: 'application/vnd.github.v3+json',
          },
          timeout: 5000,
        }
      );

      const description = response.data.description || '';

      // Simple keyword matching
      if (
        description.toLowerCase().includes(query.toLowerCase()) ||
        repo.toLowerCase().includes(query.toLowerCase())
      ) {
        // Check if 18.0 branch exists
        const branchResponse = await axios.get(
          `https://api.github.com/repos/OCA/${repo}/branches/${version}`,
          { headers: { Accept: 'application/vnd.github.v3+json' } }
        );

        const hasBranch = branchResponse.status === 200;

        results.push({
          repo: `OCA/${repo}`,
          module: repo,
          description,
          stars: response.data.stargazers_count || 0,
          branch_status: hasBranch ? '18.0' : 'unavailable',
          url: response.data.html_url,
        });
      }
    } catch (error) {
      // Skip repos that don't match or error
      continue;
    }

    if (results.length >= limit) break;
  }

  return results.sort((a, b) => b.stars - a.stars);
}
