#!/usr/bin/env node

/**
 * OCA Intelligence MCP Server
 *
 * Provides automated OCA module discovery, documentation generation,
 * and installation for Odoo 18.0 CE
 *
 * Integrations:
 * - gitsearchai.com - Advanced GitHub search for OCA modules
 * - gittodoc.com - Automated documentation generation
 * - DeepWiki - Interactive documentation wikis
 * - GitHub API - Branch status and module metadata
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
  ListPromptsRequestSchema,
  GetPromptRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

// Tool implementations
import { searchOCAModules } from './tools/search.js';
import { generateModuleDocs } from './tools/docs.js';
import { checkBranchStatus } from './tools/branches.js';
import { analyzeDependencies } from './tools/dependencies.js';
import { suggestAlternatives } from './tools/alternatives.js';
import { validateCompatibility } from './tools/compatibility.js';
import { fetchDeepWiki } from './tools/deepwiki.js';
import { installModule } from './tools/install.js';

// Resource implementations
import { getOCARepositories } from './resources/repositories.js';
import { getModuleCatalog } from './resources/catalog.js';
import { getInstallationGuides } from './resources/guides.js';
import { getCompatibilityMatrix } from './resources/compatibility.js';

// Prompt implementations
import { getModuleDiscoveryPrompt } from './prompts/discovery.js';
import { getInstallationPrompt } from './prompts/installation.js';
import { getMigrationPrompt } from './prompts/migration.js';

const server = new Server(
  {
    name: 'oca-intel-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
      resources: {},
      prompts: {},
    },
  }
);

/**
 * Register 8 Tools
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'search_oca_modules',
        description: 'Search OCA repositories using gitsearchai.com for Odoo 18.0 modules',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Search query (e.g., "accounting reports", "helpdesk management")',
            },
            version: {
              type: 'string',
              description: 'Odoo version (default: 18.0)',
              default: '18.0',
            },
            limit: {
              type: 'number',
              description: 'Maximum results to return',
              default: 10,
            },
          },
          required: ['query'],
        },
      },
      {
        name: 'generate_module_docs',
        description: 'Generate comprehensive documentation using gittodoc.com',
        inputSchema: {
          type: 'object',
          properties: {
            repo_url: {
              type: 'string',
              description: 'GitHub repository URL (e.g., https://github.com/OCA/account-financial-reporting)',
            },
            branch: {
              type: 'string',
              description: 'Branch name (default: 18.0)',
              default: '18.0',
            },
            module: {
              type: 'string',
              description: 'Specific module name (optional)',
            },
          },
          required: ['repo_url'],
        },
      },
      {
        name: 'check_branch_status',
        description: 'Check OCA repository branch availability for Odoo 18.0',
        inputSchema: {
          type: 'object',
          properties: {
            repo_name: {
              type: 'string',
              description: 'OCA repository name (e.g., "account-financial-reporting")',
            },
            branch: {
              type: 'string',
              description: 'Branch to check (default: 18.0)',
              default: '18.0',
            },
          },
          required: ['repo_name'],
        },
      },
      {
        name: 'analyze_dependencies',
        description: 'Analyze module dependencies and installation order',
        inputSchema: {
          type: 'object',
          properties: {
            module_names: {
              type: 'array',
              items: { type: 'string' },
              description: 'List of module names to analyze',
            },
            resolve_conflicts: {
              type: 'boolean',
              description: 'Attempt to resolve dependency conflicts',
              default: true,
            },
          },
          required: ['module_names'],
        },
      },
      {
        name: 'suggest_alternatives',
        description: 'Suggest OCA alternatives for Enterprise modules',
        inputSchema: {
          type: 'object',
          properties: {
            enterprise_module: {
              type: 'string',
              description: 'Enterprise module name (e.g., "web_studio", "documents")',
            },
            version: {
              type: 'string',
              description: 'Odoo version (default: 18.0)',
              default: '18.0',
            },
          },
          required: ['enterprise_module'],
        },
      },
      {
        name: 'validate_compatibility',
        description: 'Validate module compatibility with Odoo 18.0 CE',
        inputSchema: {
          type: 'object',
          properties: {
            module_name: {
              type: 'string',
              description: 'Module name to validate',
            },
            odoo_version: {
              type: 'string',
              description: 'Target Odoo version',
              default: '18.0',
            },
            check_dependencies: {
              type: 'boolean',
              description: 'Check dependency compatibility',
              default: true,
            },
          },
          required: ['module_name'],
        },
      },
      {
        name: 'fetch_deepwiki',
        description: 'Fetch interactive documentation from DeepWiki',
        inputSchema: {
          type: 'object',
          properties: {
            repo_path: {
              type: 'string',
              description: 'Repository path on DeepWiki (e.g., "OCA/account-financial-reporting")',
            },
            topic: {
              type: 'string',
              description: 'Specific topic or module',
            },
          },
          required: ['repo_path'],
        },
      },
      {
        name: 'install_module',
        description: 'Generate installation commands with dependency resolution',
        inputSchema: {
          type: 'object',
          properties: {
            module_names: {
              type: 'array',
              items: { type: 'string' },
              description: 'Modules to install',
            },
            database: {
              type: 'string',
              description: 'Target database name',
            },
            auto_deps: {
              type: 'boolean',
              description: 'Auto-install dependencies',
              default: true,
            },
          },
          required: ['module_names', 'database'],
        },
      },
    ],
  };
});

/**
 * Handle tool execution
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'search_oca_modules':
        return await searchOCAModules(args);
      case 'generate_module_docs':
        return await generateModuleDocs(args);
      case 'check_branch_status':
        return await checkBranchStatus(args);
      case 'analyze_dependencies':
        return await analyzeDependencies(args);
      case 'suggest_alternatives':
        return await suggestAlternatives(args);
      case 'validate_compatibility':
        return await validateCompatibility(args);
      case 'fetch_deepwiki':
        return await fetchDeepWiki(args);
      case 'install_module':
        return await installModule(args);
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error executing ${name}: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
      isError: true,
    };
  }
});

/**
 * Register 7 Resources
 */
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: 'oca://repositories/all',
        name: 'OCA Repositories',
        description: 'Complete list of OCA repositories with 18.0 branch status',
        mimeType: 'application/json',
      },
      {
        uri: 'oca://modules/catalog',
        name: 'Module Catalog',
        description: 'Categorized catalog of all available OCA modules for Odoo 18.0',
        mimeType: 'application/json',
      },
      {
        uri: 'oca://guides/installation',
        name: 'Installation Guides',
        description: 'Step-by-step installation guides for common module stacks',
        mimeType: 'text/markdown',
      },
      {
        uri: 'oca://compatibility/matrix',
        name: 'Compatibility Matrix',
        description: 'Module compatibility matrix for Odoo 18.0 CE',
        mimeType: 'application/json',
      },
      {
        uri: 'oca://enterprise/alternatives',
        name: 'Enterprise Alternatives',
        description: 'OCA alternatives for Odoo Enterprise modules',
        mimeType: 'application/json',
      },
      {
        uri: 'oca://finance-ssc/stack',
        name: 'Finance SSC Stack',
        description: 'InsightPulse AI Finance SSC recommended module stack',
        mimeType: 'application/json',
      },
      {
        uri: 'oca://documentation/index',
        name: 'Documentation Index',
        description: 'Searchable index of all OCA module documentation',
        mimeType: 'application/json',
      },
    ],
  };
});

/**
 * Handle resource reading
 */
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  try {
    switch (uri) {
      case 'oca://repositories/all':
        return await getOCARepositories();
      case 'oca://modules/catalog':
        return await getModuleCatalog();
      case 'oca://guides/installation':
        return await getInstallationGuides();
      case 'oca://compatibility/matrix':
        return await getCompatibilityMatrix();
      default:
        throw new Error(`Unknown resource: ${uri}`);
    }
  } catch (error) {
    throw new Error(`Error reading resource ${uri}: ${error instanceof Error ? error.message : String(error)}`);
  }
});

/**
 * Register 5 Prompts
 */
server.setRequestHandler(ListPromptsRequestSchema, async () => {
  return {
    prompts: [
      {
        name: 'module_discovery',
        description: 'Discover OCA modules for specific business requirements',
        arguments: [
          {
            name: 'requirement',
            description: 'Business requirement or use case',
            required: true,
          },
          {
            name: 'version',
            description: 'Odoo version (default: 18.0)',
            required: false,
          },
        ],
      },
      {
        name: 'installation_workflow',
        description: 'Generate complete installation workflow for module stack',
        arguments: [
          {
            name: 'modules',
            description: 'Comma-separated list of modules',
            required: true,
          },
          {
            name: 'environment',
            description: 'Target environment (dev/staging/production)',
            required: true,
          },
        ],
      },
      {
        name: 'migration_planning',
        description: 'Plan migration from Enterprise to CE + OCA',
        arguments: [
          {
            name: 'enterprise_modules',
            description: 'Current Enterprise modules in use',
            required: true,
          },
        ],
      },
      {
        name: 'troubleshooting',
        description: 'Troubleshoot OCA module installation issues',
        arguments: [
          {
            name: 'error_message',
            description: 'Error message or symptom',
            required: true,
          },
          {
            name: 'module_name',
            description: 'Module name',
            required: false,
          },
        ],
      },
      {
        name: 'best_practices',
        description: 'OCA module best practices and recommendations',
        arguments: [
          {
            name: 'topic',
            description: 'Topic (e.g., "security", "performance", "testing")',
            required: true,
          },
        ],
      },
    ],
  };
});

/**
 * Handle prompt execution
 */
server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'module_discovery':
        return await getModuleDiscoveryPrompt(args);
      case 'installation_workflow':
        return await getInstallationPrompt(args);
      case 'migration_planning':
        return await getMigrationPrompt(args);
      default:
        throw new Error(`Unknown prompt: ${name}`);
    }
  } catch (error) {
    throw new Error(`Error executing prompt ${name}: ${error instanceof Error ? error.message : String(error)}`);
  }
});

/**
 * Start the server
 */
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('OCA Intelligence MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
