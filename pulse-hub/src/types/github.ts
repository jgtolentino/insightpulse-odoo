export interface GitHubUser {
  login: string;
  id: number;
  avatar_url: string;
  name: string;
  email: string;
  bio: string;
  public_repos: number;
}

export interface GitHubRepository {
  id: number;
  name: string;
  full_name: string;
  private: boolean;
  description: string;
  html_url: string;
  owner: {
    login: string;
    avatar_url: string;
  };
}

export interface GitHubScope {
  id: string;
  name: string;
  description: string;
  scopes: string[];
  enabled: boolean;
}

export interface GitHubConnection {
  isConnected: boolean;
  accessToken: string | null;
  user: GitHubUser | null;
  installationId: string | null;
}

export interface AIIntegrationConfig {
  type: 'chatgpt' | 'claude-mcp' | 'api';
  config: string;
  title: string;
  description: string;
}

export interface ActivityLog {
  id: string;
  type: 'issue' | 'commit' | 'pr' | 'workflow';
  action: string;
  timestamp: Date;
  repository: string;
  details: string;
}
