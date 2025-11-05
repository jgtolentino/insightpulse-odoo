import { GITHUB_APP_PERMISSIONS, GITHUB_INSTALL_API } from '../config/github';

export default function PermissionSummary() {
  const handleInstall = async () => {
    try {
      // Call the installation start endpoint
      const response = await fetch(`${GITHUB_INSTALL_API}/start`);

      if (!response.ok) {
        throw new Error('Failed to initiate GitHub App installation');
      }

      const data = await response.json();

      // Store state for CSRF verification
      if (data.state) {
        sessionStorage.setItem('github_app_state', data.state);
      }

      // Redirect to GitHub App installation page
      window.location.href = data.redirect_url;
    } catch (error) {
      console.error('Installation error:', error);
      alert('Failed to start installation. Please try again.');
    }
  };

  return (
    <div className="card p-6">
      <h2 className="text-xl font-bold mb-4">GitHub App Permissions</h2>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
        This app will request the following permissions. These are configured in the GitHub App settings and cannot be changed at runtime.
      </p>

      <div className="space-y-3 mb-6">
        {GITHUB_APP_PERMISSIONS.map((permission) => (
          <div
            key={permission.name}
            className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <h3 className="font-semibold">{permission.name}</h3>
                  <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-xs rounded">
                    {permission.level}
                  </span>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {permission.description}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={handleInstall}
        className="w-full btn-primary flex items-center justify-center space-x-2"
      >
        <svg
          className="w-5 h-5"
          fill="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
        </svg>
        <span>Install GitHub App</span>
      </button>

      <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-4">
        You'll be redirected to GitHub to authorize the installation
      </p>
    </div>
  );
}
