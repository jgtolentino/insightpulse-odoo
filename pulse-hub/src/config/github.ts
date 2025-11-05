// GitHub App Configuration (Installation Flow)
// Uses GitHub App instead of OAuth for better security and permissions

export const GITHUB_APP_NAME = import.meta.env.VITE_GITHUB_APP_NAME || 'pulser-hub';
export const GITHUB_APP_ID = import.meta.env.VITE_GITHUB_APP_ID || '2191216';
export const API_BASE_URL = 'https://api.github.com';

// Supabase Edge Function endpoints
export const GITHUB_INSTALL_API = import.meta.env.VITE_GITHUB_INSTALL_API ||
  'https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/github-app-install';
export const GITHUB_MINT_TOKEN_API = import.meta.env.VITE_GITHUB_MINT_TOKEN_API ||
  'https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/github-mint-token';

// GitHub App Permissions (Fixed in App settings, not runtime)
// These are shown to the user for transparency
export const GITHUB_APP_PERMISSIONS = [
  {
    name: 'Repository Contents',
    description: 'Read and write access to code, commits, branches, and files',
    level: 'Read & Write',
  },
  {
    name: 'Issues',
    description: 'Create, read, update, and close issues',
    level: 'Read & Write',
  },
  {
    name: 'Pull Requests',
    description: 'Create, merge, and review pull requests',
    level: 'Read & Write',
  },
  {
    name: 'Workflows',
    description: 'Trigger GitHub Actions workflows and view runs',
    level: 'Read & Write',
  },
  {
    name: 'Metadata',
    description: 'Read repository metadata',
    level: 'Read-only',
  },
];
