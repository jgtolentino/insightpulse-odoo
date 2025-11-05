import { API_BASE_URL } from '../config/github';
import type { GitHubUser, GitHubRepository } from '../types/github';

export class GitHubService {
  private accessToken: string;

  constructor(accessToken: string) {
    this.accessToken = accessToken;
  }

  private async fetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        Authorization: `Bearer ${this.accessToken}`,
        Accept: 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.statusText}`);
    }

    return response.json();
  }

  async getCurrentUser(): Promise<GitHubUser> {
    return this.fetch<GitHubUser>('/user');
  }

  async getRepositories(): Promise<GitHubRepository[]> {
    return this.fetch<GitHubRepository[]>('/user/repos?per_page=100&sort=updated');
  }

  async getRateLimit() {
    return this.fetch('/rate_limit');
  }

  static generateAuthUrl(clientId: string, redirectUri: string, scopes: string): string {
    // Generate random 32-character state nonce for CSRF protection
    const state = Array.from(crypto.getRandomValues(new Uint8Array(16)))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');

    const params = new URLSearchParams({
      client_id: clientId,
      redirect_uri: redirectUri,
      scope: scopes,
      state: state,
    });

    // Store state in sessionStorage for validation on callback
    sessionStorage.setItem('github_oauth_state', state);

    return `https://github.com/login/oauth/authorize?${params.toString()}`;
  }
}
