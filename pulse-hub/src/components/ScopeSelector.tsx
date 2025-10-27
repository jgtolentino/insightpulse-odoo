import type { GitHubScope } from '../types/github';

interface Props {
  scopes: GitHubScope[];
  onChange: (scopes: GitHubScope[]) => void;
}

export default function ScopeSelector({ scopes, onChange }: Props) {
  const toggleScope = (id: string) => {
    const updated = scopes.map((scope) =>
      scope.id === id ? { ...scope, enabled: !scope.enabled } : scope
    );
    onChange(updated);
  };

  return (
    <div className="card p-6">
      <h2 className="text-xl font-bold mb-4">Permission Scopes</h2>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Select the features you want AI assistants to access
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {scopes.map((scope) => {
          const borderClass = scope.enabled
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
            : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600';
          return (
            <div
              key={scope.id}
              onClick={() => toggleScope(scope.id)}
              className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${borderClass}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className="font-semibold">{scope.name}</h3>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {scope.description}
                  </p>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {scope.scopes.map((s) => (
                      <span
                        key={s}
                        className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-xs rounded"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="ml-3">
                  <input
                    type="checkbox"
                    checked={scope.enabled}
                    onChange={() => {}}
                    className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
