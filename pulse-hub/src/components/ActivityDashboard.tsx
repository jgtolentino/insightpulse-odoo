import { useState } from 'react';
import type { ActivityLog } from '../types/github';

export default function ActivityDashboard() {
  const [activities] = useState<ActivityLog[]>([
    {
      id: '1',
      type: 'issue',
      action: 'Created issue #42: Add dark mode support',
      timestamp: new Date(Date.now() - 3600000),
      repository: 'user/repo',
      details: 'AI Assistant: ChatGPT',
    },
    {
      id: '2',
      type: 'commit',
      action: 'Pushed commit: Fix login bug',
      timestamp: new Date(Date.now() - 7200000),
      repository: 'user/repo',
      details: 'AI Assistant: Claude',
    },
    {
      id: '3',
      type: 'pr',
      action: 'Created PR #15: Feature enhancement',
      timestamp: new Date(Date.now() - 10800000),
      repository: 'user/another-repo',
      details: 'AI Assistant: Claude',
    },
  ]);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'issue':
        return '🐛';
      case 'commit':
        return '📝';
      case 'pr':
        return '🔀';
      case 'workflow':
        return '⚙️';
      default:
        return '📌';
    }
  };

  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / 3600000);

    if (hours < 1) {
      const minutes = Math.floor(diff / 60000);
      return minutes + ' minutes ago';
    } else if (hours < 24) {
      return hours + ' hours ago';
    } else {
      const days = Math.floor(hours / 24);
      return days + ' days ago';
    }
  };

  return (
    <div className="card p-6">
      <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Actions performed by AI assistants
      </p>

      {activities.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">No activity yet</p>
          <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
            Activity will appear here when AI assistants use your GitHub connection
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {activities.map((activity) => (
            <div
              key={activity.id}
              className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
            >
              <div className="flex items-start space-x-3">
                <span className="text-2xl">{getTypeIcon(activity.type)}</span>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 dark:text-gray-100">
                    {activity.action}
                  </p>
                  <div className="flex items-center space-x-2 mt-1 text-sm text-gray-500 dark:text-gray-400">
                    <span>{activity.repository}</span>
                    <span>•</span>
                    <span>{formatTime(activity.timestamp)}</span>
                  </div>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                    {activity.details}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-6 grid grid-cols-3 gap-4">
        <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">3</p>
          <p className="text-sm text-gray-600 dark:text-gray-400">Total Actions</p>
        </div>
        <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">2</p>
          <p className="text-sm text-gray-600 dark:text-gray-400">Repositories</p>
        </div>
        <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">5000/5000</p>
          <p className="text-sm text-gray-600 dark:text-gray-400">API Rate Limit</p>
        </div>
      </div>
    </div>
  );
}
