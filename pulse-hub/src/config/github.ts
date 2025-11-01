import type { GitHubScope } from '../types/github';

export const GITHUB_CLIENT_ID = import.meta.env.VITE_GITHUB_CLIENT_ID || '';
export const GITHUB_REDIRECT_URI = import.meta.env.VITE_OAUTH_REDIRECT_URI || 'http://localhost:3000/callback';
export const API_BASE_URL = 'https://api.github.com';

export const GITHUB_SCOPES: GitHubScope[] = [
  {
    id: 'issues',
    name: 'Issues',
    description: 'Create, read, update, and close issues',
    scopes: ['repo'],
    enabled: true,
  },
  {
    id: 'code',
    name: 'Code',
    description: 'Read files and push commits',
    scopes: ['repo'],
    enabled: true,
  },
  {
    id: 'pull_requests',
    name: 'Pull Requests',
    description: 'Create, merge, and review pull requests',
    scopes: ['repo'],
    enabled: true,
  },
  {
    id: 'actions',
    name: 'Actions',
    description: 'Trigger workflows and view runs',
    scopes: ['workflow'],
    enabled: false,
  },
  {
    id: 'projects',
    name: 'Projects',
    description: 'Update project boards',
    scopes: ['project'],
    enabled: false,
  },
  {
    id: 'admin',
    name: 'Repository Admin',
    description: 'Manage settings and webhooks',
    scopes: ['admin:repo_hook'],
    enabled: false,
  },
];

export const getSelectedScopes = (selectedScopes: GitHubScope[]): string => {
  const scopes = selectedScopes
    .filter((scope) => scope.enabled)
    .flatMap((scope) => scope.scopes);
  return [...new Set(scopes)].join(' ');
};
