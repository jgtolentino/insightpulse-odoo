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
    const params = new URLSearchParams({
      client_id: clientId,
      redirect_uri: redirectUri,
      scope: scopes,
      response_type: 'token',
    });
    return `https://github.com/login/oauth/authorize?${params.toString()}`;
  }
}
