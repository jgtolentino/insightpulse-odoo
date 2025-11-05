import { useState } from 'react';

interface Props {
  accessToken: string;
  installationId: string | null;
}

export default function IntegrationConfigs({ accessToken, installationId }: Props) {
  const [activeTab, setActiveTab] = useState<'chatgpt' | 'claude' | 'api'>('claude');
  const [copied, setCopied] = useState(false);

  const configs = {
    claude: `{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${accessToken}"
      }
    }
  }
}`,
    chatgpt: `{
  "openapi": "3.1.0",
  "info": {
    "title": "GitHub API via pulse.hub",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://api.github.com"
    }
  ],
  "components": {
    "securitySchemes": {
      "BearerAuth": {
        "type": "http",
        "scheme": "bearer"
      }
    }
  },
  "security": [{"BearerAuth": []}]
}`,
    api: `# Using curl
curl -H "Authorization: Bearer ${accessToken}" \\
     -H "Accept: application/vnd.github+json" \\
     https://api.github.com/user/repos

# Using JavaScript
const response = await fetch('https://api.github.com/user/repos', {
  headers: {
    'Authorization': 'Bearer ${accessToken}',
    'Accept': 'application/vnd.github+json',
  }
});

# Using Python
import requests
headers = {
    'Authorization': 'Bearer ${accessToken}',
    'Accept': 'application/vnd.github+json',
}
response = requests.get('https://api.github.com/user/repos', headers=headers)`
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(configs[activeTab]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getTabClass = (tab: string) => {
    return activeTab === tab
      ? 'border-primary-500 text-primary-600 dark:text-primary-400'
      : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300';
  };

  return (
    <div className="card p-6">
      <h2 className="text-xl font-bold mb-4">AI Integration</h2>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
        Configure your AI assistants to use GitHub
      </p>

      <div className="flex space-x-2 mb-6 border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={() => setActiveTab('claude')}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${getTabClass('claude')}`}
        >
          Claude MCP
        </button>
        <button
          onClick={() => setActiveTab('chatgpt')}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${getTabClass('chatgpt')}`}
        >
          ChatGPT
        </button>
        <button
          onClick={() => setActiveTab('api')}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${getTabClass('api')}`}
        >
          Direct API
        </button>
      </div>

      <div>
        {activeTab === 'claude' && (
          <div>
            <h3 className="font-semibold mb-2">Claude Desktop Configuration</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Add this to your <code className="px-1 bg-gray-100 dark:bg-gray-700 rounded">~/.config/claude/claude_desktop_config.json</code>
            </p>
          </div>
        )}
        {activeTab === 'chatgpt' && (
          <div>
            <h3 className="font-semibold mb-2">ChatGPT Custom GPT Actions</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Use this OpenAPI schema in your Custom GPT Actions configuration
            </p>
          </div>
        )}
        {activeTab === 'api' && (
          <div>
            <h3 className="font-semibold mb-2">Direct API Examples</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Use these examples to integrate with any tool
            </p>
          </div>
        )}

        <div className="relative">
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
            <code>{configs[activeTab]}</code>
          </pre>
          <button
            onClick={copyToClipboard}
            className="absolute top-2 right-2 px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded"
          >
            {copied ? 'Copied!' : 'Copy'}
          </button>
        </div>

        {activeTab === 'claude' && (
          <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <p className="text-sm text-blue-900 dark:text-blue-200">
              <strong>Note:</strong> After adding this configuration, restart Claude Desktop for changes to take effect.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
