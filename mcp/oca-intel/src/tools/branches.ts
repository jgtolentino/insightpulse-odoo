/**
 * Branch Status Checker
 * Monitors OCA repository branch availability for Odoo 18.0
 */

import axios from 'axios';

interface BranchArgs {
  repo_name: string;
  branch?: string;
}

export async function checkBranchStatus(args: BranchArgs) {
  const { repo_name, branch = '18.0' } = args;

  try {
    const url = `https://api.github.com/repos/OCA/${repo_name}/branches/${branch}`;

    const response = await axios.get(url, {
      headers: {
        Accept: 'application/vnd.github.v3+json',
      },
      timeout: 10000,
      validateStatus: (status) => status < 500, // Don't throw on 404
    });

    const available = response.status === 200;

    const result = {
      repo: `OCA/${repo_name}`,
      branch,
      available,
      checked_at: new Date().toISOString(),
      details: available
        ? {
            sha: response.data.commit.sha,
            protected: response.data.protected,
            last_commit: response.data.commit.commit.author.date,
          }
        : {
            status_code: response.status,
            message: `Branch ${branch} not found`,
          },
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  } catch (error) {
    throw new Error(`Branch check failed: ${error instanceof Error ? error.message : String(error)}`);
  }
}
