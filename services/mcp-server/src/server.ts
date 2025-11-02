#!/usr/bin/env node
/**
 * MCP Server for Odoo Operations
 *
 * Provides Model Context Protocol interface to Odoo via XML-RPC
 * Runs on Fastify with WebSocket support
 */

import Fastify from 'fastify';
import fastifyWebsocket from '@fastify/websocket';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { WebSocketServerTransport } from '@modelcontextprotocol/sdk/server/websocket.js';
import { createOdooTools } from './odoo.js';
import type { FastifyRequest } from 'fastify';
import type { WebSocket } from 'ws';

// Environment configuration
const PORT = parseInt(process.env.PORT || '8080', 10);
const HOST = process.env.HOST || '0.0.0.0';

// Validate required environment variables
const REQUIRED_ENV_VARS = ['ODOO_URL', 'ODOO_DB', 'ODOO_USER', 'ODOO_PASSWORD'];
for (const envVar of REQUIRED_ENV_VARS) {
  if (!process.env[envVar]) {
    console.warn(`[warn] ${envVar} not set; odoo.health will fail until configured.`);
  }
}

// Create Fastify instance
const fastify = Fastify({
  logger: {
    level: process.env.LOG_LEVEL || 'info',
    transport: {
      target: 'pinto-pretty',
      options: {
        translateTime: 'HH:MM:ss Z',
        ignore: 'pid,hostname',
      },
    },
  },
});

// Register WebSocket plugin
await fastify.register(fastifyWebsocket);

// Health check endpoint
fastify.get('/healthz', async (_request, reply) => {
  return reply.send({ ok: true, service: 'pulser-hub-mcp', timestamp: new Date().toISOString() });
});

// Root endpoint
fastify.get('/', async (_request, reply) => {
  return reply.send({
    service: 'pulser-hub-mcp',
    version: '1.0.0',
    protocol: 'Model Context Protocol',
    endpoints: {
      health: '/healthz',
      websocket: '/ws',
    },
    status: 'ok',
  });
});

// WebSocket MCP endpoint
fastify.register(async function (fastify) {
  fastify.get('/ws', { websocket: true }, (socket: WebSocket, request: FastifyRequest) => {
    fastify.log.info({ remoteAddress: request.ip }, 'MCP WebSocket connection established');

    // Create MCP server instance for this connection
    const mcpServer = new Server(
      {
        name: 'pulser-hub-mcp',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Register Odoo tools
    const odooTools = createOdooTools({
      url: process.env.ODOO_URL || '',
      database: process.env.ODOO_DB || '',
      username: process.env.ODOO_USER || '',
      password: process.env.ODOO_PASSWORD || '',
    });

    // Register tool handlers
    mcpServer.setRequestHandler('tools/list', async () => ({
      tools: odooTools.tools,
    }));

    mcpServer.setRequestHandler('tools/call', async (request) => {
      const { name, arguments: args } = request.params as {
        name: string;
        arguments: Record<string, unknown>;
      };

      fastify.log.info({ tool: name, args }, 'Tool call received');

      const handler = odooTools.handlers[name];
      if (!handler) {
        throw new Error(`Unknown tool: ${name}`);
      }

      try {
        const result = await handler(args);
        fastify.log.info({ tool: name, success: true }, 'Tool call completed');
        return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
      } catch (error) {
        fastify.log.error({ tool: name, error }, 'Tool call failed');
        throw error;
      }
    });

    // Create WebSocket transport
    const transport = new WebSocketServerTransport(socket as any);

    // Handle connection lifecycle
    socket.on('close', () => {
      fastify.log.info('MCP WebSocket connection closed');
    });

    socket.on('error', (error) => {
      fastify.log.error({ error }, 'MCP WebSocket error');
    });

    // Connect server to transport
    mcpServer.connect(transport).catch((error) => {
      fastify.log.error({ error }, 'Failed to connect MCP server to WebSocket transport');
      socket.close();
    });
  });
});

// Graceful shutdown
const signals = ['SIGINT', 'SIGTERM'];
for (const signal of signals) {
  process.on(signal, async () => {
    fastify.log.info({ signal }, 'Received shutdown signal');
    await fastify.close();
    process.exit(0);
  });
}

// Start server
async function start() {
  try {
    await fastify.listen({ port: PORT, host: HOST });
    fastify.log.info(`MCP server listening on ${HOST}:${PORT}`);
    fastify.log.info('WebSocket endpoint: /ws');
    fastify.log.info('Health check: /healthz');
  } catch (error) {
    fastify.log.error(error);
    process.exit(1);
  }
}

start();
