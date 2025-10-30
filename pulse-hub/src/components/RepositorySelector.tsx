import { useState, useEffect } from 'react';
import type { GitHubRepository } from '../types/github';
import { GitHubService } from '../services/github';

interface Props {
  accessToken: string;
}

export default function RepositorySelector({ accessToken }: Props) {
  const [repositories, setRepositories] = useState<GitHubRepository[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRepo, setSelectedRepo] = useState<string>('');
  const [filter, setFilter] = useState('');

  useEffect(() => {
    loadRepositories();
  }, [accessToken]);

  const loadRepositories = async () => {
    try {
      const service = new GitHubService(accessToken);
      const repos = await service.getRepositories();
      setRepositories(repos);
      if (repos.length > 0) {
        setSelectedRepo(repos[0].full_name);
      }
    } catch (error) {
      console.error('Failed to load repositories:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredRepos = repositories.filter((repo) =>
    repo.full_name.toLowerCase().includes(filter.toLowerCase()) ||
    (repo.description && repo.description.toLowerCase().includes(filter.toLowerCase()))
  );

  if (loading) {
    return (
      <div className="card p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-4"></div>
          <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
          <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="card p-6">
      <h2 className="text-xl font-bold mb-4">Repository Selection</h2>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Choose which repositories AI assistants can access
      </p>

      <input
        type="text"
        placeholder="Filter repositories..."
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        className="input w-full mb-4"
      />

      <div className="space-y-2 max-h-64 overflow-y-auto">
        {filteredRepos.map((repo) => {
          const borderClass = selectedRepo === repo.full_name
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
            : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600';
          return (
            <div
              key={repo.id}
              onClick={() => setSelectedRepo(repo.full_name)}
              className={`p-3 border rounded-lg cursor-pointer transition-colors ${borderClass}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <h3 className="font-medium">{repo.name}</h3>
                    {repo.private && (
                      <span className="px-2 py-0.5 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 text-xs rounded">
                        Private
                      </span>
                    )}
                  </div>
                  {repo.description && (
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {repo.description}
                    </p>
                  )}
                </div>
                <input
                  type="radio"
                  checked={selectedRepo === repo.full_name}
                  onChange={() => {}}
                  className="mt-1"
                />
              </div>
            </div>
          );
        })}
      </div>

      {filteredRepos.length === 0 && (
        <p className="text-center text-gray-500 dark:text-gray-400 py-8">
          No repositories found
        </p>
      )}

      <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Selected: <span className="font-mono font-semibold text-gray-900 dark:text-gray-100">{selectedRepo || 'None'}</span>
        </p>
      </div>
    </div>
  );
}
