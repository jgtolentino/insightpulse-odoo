import { useState, useEffect, useCallback } from 'react';
import type { GitHubConnection } from './types/github';
import { GITHUB_INSTALL_API } from './config/github';
import ConnectionStatus from './components/ConnectionStatus';
import PermissionSummary from './components/PermissionSummary';
import IntegrationConfigs from './components/IntegrationConfigs';
import RepositorySelector from './components/RepositorySelector';
import ActivityDashboard from './components/ActivityDashboard';
import { GitHubService } from './services/github';

function App() {
  const [connection, setConnection] = useState<GitHubConnection>({
    isConnected: false,
    accessToken: null,
    user: null,
    installationId: null,
  });
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const handleConnect = useCallback(async (token: string, installationId?: string) => {
    try {
      const service = new GitHubService(token);
      const user = await service.getCurrentUser();

      setConnection({
        isConnected: true,
        accessToken: token,
        user,
        installationId: installationId || null,
      });
    } catch (error) {
      console.error('Failed to connect:', error);
    }
  }, []);

  useEffect(() => {
    // Check for GitHub App installation callback
    const searchParams = new URLSearchParams(window.location.search);

    const installationId = searchParams.get('installation_id');
    const setupAction = searchParams.get('setup_action');
    const state = searchParams.get('state');

    if (installationId) {
      // Validate state parameter for CSRF protection
      const savedState = sessionStorage.getItem('github_app_state');

      if (state && savedState && state !== savedState) {
        console.error('State mismatch - possible CSRF attack');
        alert('Authentication failed: Invalid state parameter');
        window.history.replaceState({}, document.title, '/');
        return;
      }

      // Clean up state
      sessionStorage.removeItem('github_app_state');

      // Handle the installation callback
      handleInstallationCallback(installationId, setupAction);
      window.history.replaceState({}, document.title, '/');
      return;
    }
  }, [handleConnect]);

  const handleInstallationCallback = async (installationId: string, setupAction: string | null) => {
    try {
      // Call the callback endpoint to complete installation
      const response = await fetch(`${GITHUB_INSTALL_API}/callback?installation_id=${installationId}${setupAction ? `&setup_action=${setupAction}` : ''}`);

      if (!response.ok) {
        throw new Error('Failed to complete installation');
      }

      const data = await response.json();

      if (data.success) {
        alert(`GitHub App installed successfully for ${data.account}!`);
        // Store installation_id for future use
        sessionStorage.setItem('github_installation_id', installationId);
      }
    } catch (error) {
      console.error('Installation callback error:', error);
      alert('Failed to complete installation. Please try again.');
    }
  };

  const handleDisconnect = () => {
    sessionStorage.removeItem('github_installation_id');
    setConnection({
      isConnected: false,
      accessToken: null,
      user: null,
      installationId: null,
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
            <PermissionSummary />
          )}

          {connection.isConnected && (
            <>
              <RepositorySelector accessToken={connection.accessToken!} />
              <IntegrationConfigs
                accessToken={connection.accessToken!}
                installationId={connection.installationId}
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
