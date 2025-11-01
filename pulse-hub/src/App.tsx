import { useState, useEffect, useCallback } from 'react';
import type { GitHubConnection, GitHubScope } from './types/github';
import { GITHUB_SCOPES } from './config/github';
import ConnectionStatus from './components/ConnectionStatus';
import ScopeSelector from './components/ScopeSelector';
import IntegrationConfigs from './components/IntegrationConfigs';
import RepositorySelector from './components/RepositorySelector';
import ActivityDashboard from './components/ActivityDashboard';
import { GitHubService } from './services/github';

function App() {
  const [connection, setConnection] = useState<GitHubConnection>({
    isConnected: false,
    accessToken: null,
    user: null,
    selectedScopes: GITHUB_SCOPES,
  });
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const handleConnect = useCallback(async (token: string) => {
    try {
      const service = new GitHubService(token);
      const user = await service.getCurrentUser();

      setConnection((prev) => ({
        isConnected: true,
        accessToken: token,
        user,
        selectedScopes: prev.selectedScopes,
      }));
    } catch (error) {
      console.error('Failed to connect:', error);
    }
  }, []);

  useEffect(() => {
    // Check for OAuth errors in query parameters
    const searchParams = new URLSearchParams(window.location.search);
    const error = searchParams.get('error');
    const errorDescription = searchParams.get('error_description');

    if (error) {
      console.error('OAuth error:', error, errorDescription);
      alert(`Authentication failed: ${errorDescription || error}`);
      window.history.replaceState({}, document.title, '/');
      return;
    }

    // Check for access token in hash (from OAuth callback)
    const hash = window.location.hash;
    if (hash) {
      const params = new URLSearchParams(hash.substring(1));
      const token = params.get('access_token');

      if (token) {
        handleConnect(token);
        window.history.replaceState({}, document.title, '/');
      }
    }
  }, [handleConnect]);

  const handleDisconnect = () => {
    setConnection({
      isConnected: false,
      accessToken: null,
      user: null,
      selectedScopes: GITHUB_SCOPES,
    });
  };

  const handleScopeChange = (scopes: GitHubScope[]) => {
    setConnection({
      ...connection,
      selectedScopes: scopes,
    });
  };

  return (
    <div className="min-h-screen">
      <header className="border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">P</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold">pulse.hub</h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  GitHub OAuth Connector for AI
                </p>
              </div>
            </div>
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="btn-secondary"
            >
              {darkMode ? '☀️' : '🌙'}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          <ConnectionStatus
            connection={connection}
            onDisconnect={handleDisconnect}
          />

          {!connection.isConnected && (
            <ScopeSelector
              scopes={connection.selectedScopes}
              onChange={handleScopeChange}
            />
          )}

          {connection.isConnected && (
            <>
              <RepositorySelector accessToken={connection.accessToken!} />
              <IntegrationConfigs
                accessToken={connection.accessToken!}
                selectedScopes={connection.selectedScopes}
              />
              <ActivityDashboard />
            </>
          )}
        </div>
      </main>

      <footer className="border-t border-gray-200 dark:border-gray-700 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-500 dark:text-gray-400 text-sm">
            pulse.hub - Part of the InsightPulse Platform
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App
