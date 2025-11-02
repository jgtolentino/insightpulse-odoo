/**
 * Odoo MCP Tools
 *
 * Implements MCP tools for Odoo operations via XML-RPC
 */

import { fetch } from 'undici';
import { z } from 'zod';

export interface OdooConfig {
  url: string;
  database: string;
  username: string;
  password: string;
}

interface OdooXmlRpcResponse {
  result?: any;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
}

/**
 * Odoo XML-RPC client
 */
class OdooClient {
  private uid: number | null = null;

  constructor(private config: OdooConfig) {}

  /**
 * Call Odoo XML-RPC endpoint
   */
  private async call(service: string, method: string, args: any[]): Promise<any> {
    const url = `${this.config.url}/xmlrpc/2/${service}`;

    const xmlPayload = this.buildXmlRpcPayload(method, args);

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'text/xml',
      },
      body: xmlPayload,
    });

    if (!response.ok) {
      throw new Error(`Odoo XML-RPC error: ${response.statusText}`);
    }

    const text = await response.text();
    return this.parseXmlRpcResponse(text);
  }

  /**
   * Build XML-RPC request payload
   */
  private buildXmlRpcPayload(method: string, args: any[]): string {
    const params = args.map((arg) => this.encodeValue(arg)).join('');

    return `<?xml version="1.0"?>
<methodCall>
  <methodName>${method}</methodName>
  <params>${params}</params>
</methodCall>`;
  }

  /**
   * Encode value for XML-RPC
   */
  private encodeValue(value: any): string {
    if (value === null || value === undefined) {
      return '<param><value><boolean>0</boolean></value></param>';
    }

    if (typeof value === 'boolean') {
      return `<param><value><boolean>${value ? '1' : '0'}</boolean></value></param>`;
    }

    if (typeof value === 'number') {
      if (Number.isInteger(value)) {
        return `<param><value><int>${value}</int></value></param>`;
      }
      return `<param><value><double>${value}</double></value></param>`;
    }

    if (typeof value === 'string') {
      const escaped = value
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
      return `<param><value><string>${escaped}</string></value></param>`;
    }

    if (Array.isArray(value)) {
      const items = value.map((item) => this.encodeArrayItem(item)).join('');
      return `<param><value><array><data>${items}</data></array></value></param>`;
    }

    if (typeof value === 'object') {
      const members = Object.entries(value)
        .map(
          ([key, val]) =>
            `<member><name>${key}</name>${this.encodeValue(val).replace(/<\/?param>/g, '')}</member>`
        )
        .join('');
      return `<param><value><struct>${members}</struct></value></param>`;
    }

    throw new Error(`Cannot encode value of type ${typeof value}`);
  }

  /**
   * Encode array item for XML-RPC
   */
  private encodeArrayItem(value: any): string {
    return this.encodeValue(value).replace(/<\/?param>/g, '');
  }

  /**
   * Parse XML-RPC response
   */
  private parseXmlRpcResponse(xml: string): any {
    // Simple XML parsing for Odoo responses
    // In production, use a proper XML parser like fast-xml-parser

    if (xml.includes('<fault>')) {
      const faultMatch = xml.match(/<string>(.*?)<\/string>/);
      throw new Error(`Odoo fault: ${faultMatch?.[1] || 'Unknown error'}`);
    }

    // Extract value from response
    const valueMatch = xml.match(/<value>(.*?)<\/value>/s);
    if (!valueMatch) {
      throw new Error('Invalid XML-RPC response');
    }

    return this.parseValue(valueMatch[1]);
  }

  /**
   * Parse XML-RPC value
   */
  private parseValue(xml: string): any {
    // Integer
    let match = xml.match(/<int>(-?\d+)<\/int>/);
    if (match) return parseInt(match[1], 10);

    // Double
    match = xml.match(/<double>([\d.]+)<\/double>/);
    if (match) return parseFloat(match[1]);

    // Boolean
    match = xml.match(/<boolean>([01])<\/boolean>/);
    if (match) return match[1] === '1';

    // String
    match = xml.match(/<string>(.*?)<\/string>/s);
    if (match) {
      return match[1]
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&amp;/g, '&');
    }

    // Array
    if (xml.includes('<array>')) {
      const items: any[] = [];
      const dataMatch = xml.match(/<data>(.*?)<\/data>/s);
      if (dataMatch) {
        const valueMatches = dataMatch[1].matchAll(/<value>(.*?)<\/value>/gs);
        for (const m of valueMatches) {
          items.push(this.parseValue(m[1]));
        }
      }
      return items;
    }

    // Struct (object)
    if (xml.includes('<struct>')) {
      const obj: Record<string, any> = {};
      const memberMatches = xml.matchAll(/<member>.*?<name>(.*?)<\/name>.*?<value>(.*?)<\/value>.*?<\/member>/gs);
      for (const m of memberMatches) {
        obj[m[1]] = this.parseValue(m[2]);
      }
      return obj;
    }

    // Fallback
    return xml.trim();
  }

  /**
   * Authenticate and get UID
   */
  async authenticate(): Promise<number> {
    if (this.uid !== null) {
      return this.uid;
    }

    this.uid = await this.call('common', 'authenticate', [
      this.config.database,
      this.config.username,
      this.config.password,
      {},
    ]);

    if (!this.uid) {
      throw new Error('Authentication failed: invalid credentials');
    }

    return this.uid;
  }

  /**
   * Execute Odoo method
   */
  async execute(model: string, method: string, args: any[] = [], kwargs: Record<string, any> = {}): Promise<any> {
    const uid = await this.authenticate();

    return await this.call('object', 'execute_kw', [
      this.config.database,
      uid,
      this.config.password,
      model,
      method,
      args,
      kwargs,
    ]);
  }

  /**
   * Search records
   */
  async search(model: string, domain: any[] = [], limit?: number, offset?: number): Promise<number[]> {
    const kwargs: any = {};
    if (limit !== undefined) kwargs.limit = limit;
    if (offset !== undefined) kwargs.offset = offset;

    return await this.execute(model, 'search', [domain], kwargs);
  }

  /**
   * Read records
   */
  async read(model: string, ids: number[], fields?: string[]): Promise<any[]> {
    const kwargs: any = {};
    if (fields) kwargs.fields = fields;

    return await this.execute(model, 'read', [ids], kwargs);
  }

  /**
   * Search and read records
   */
  async searchRead(
    model: string,
    domain: any[] = [],
    fields?: string[],
    limit?: number,
    offset?: number
  ): Promise<any[]> {
    const kwargs: any = {};
    if (fields) kwargs.fields = fields;
    if (limit !== undefined) kwargs.limit = limit;
    if (offset !== undefined) kwargs.offset = offset;

    return await this.execute(model, 'search_read', [domain], kwargs);
  }

  /**
   * Create record
   */
  async create(model: string, values: Record<string, any>): Promise<number> {
    return await this.execute(model, 'create', [values]);
  }

  /**
   * Write (update) records
   */
  async write(model: string, ids: number[], values: Record<string, any>): Promise<boolean> {
    return await this.execute(model, 'write', [ids, values]);
  }

  /**
   * Delete records
   */
  async unlink(model: string, ids: number[]): Promise<boolean> {
    return await this.execute(model, 'unlink', [ids]);
  }
}

/**
 * Create Odoo MCP tools
 */
export function createOdooTools(config: OdooConfig) {
  const client = new OdooClient(config);

  const tools = [
    {
      name: 'odoo.health',
      description: 'Check Odoo connection health and authentication',
      inputSchema: {
        type: 'object',
        properties: {},
      },
    },
    {
      name: 'odoo.search_read',
      description: 'Search and read Odoo records',
      inputSchema: {
        type: 'object',
        properties: {
          model: {
            type: 'string',
            description: 'Odoo model name (e.g., res.partner, sale.order)',
          },
          domain: {
            type: 'array',
            description: 'Search domain (Odoo-style, e.g., [["name", "=", "John"]])',
            default: [],
          },
          fields: {
            type: 'array',
            description: 'Fields to retrieve (e.g., ["name", "email"])',
            items: { type: 'string' },
          },
          limit: {
            type: 'number',
            description: 'Maximum number of records to return',
            default: 10,
          },
          offset: {
            type: 'number',
            description: 'Offset for pagination',
            default: 0,
          },
        },
        required: ['model'],
      },
    },
    {
      name: 'odoo.create',
      description: 'Create a new Odoo record',
      inputSchema: {
        type: 'object',
        properties: {
          model: {
            type: 'string',
            description: 'Odoo model name',
          },
          values: {
            type: 'object',
            description: 'Field values for the new record',
          },
        },
        required: ['model', 'values'],
      },
    },
    {
      name: 'odoo.write',
      description: 'Update existing Odoo records',
      inputSchema: {
        type: 'object',
        properties: {
          model: {
            type: 'string',
            description: 'Odoo model name',
          },
          ids: {
            type: 'array',
            description: 'Record IDs to update',
            items: { type: 'number' },
          },
          values: {
            type: 'object',
            description: 'Field values to update',
          },
        },
        required: ['model', 'ids', 'values'],
      },
    },
    {
      name: 'odoo.unlink',
      description: 'Delete Odoo records',
      inputSchema: {
        type: 'object',
        properties: {
          model: {
            type: 'string',
            description: 'Odoo model name',
          },
          ids: {
            type: 'array',
            description: 'Record IDs to delete',
            items: { type: 'number' },
          },
        },
        required: ['model', 'ids'],
      },
    },
  ];

  const handlers: Record<string, (args: any) => Promise<any>> = {
    'odoo.health': async () => {
      const uid = await client.authenticate();
      return { uid, status: 'ok', message: 'Connected to Odoo successfully' };
    },

    'odoo.search_read': async (args) => {
      const schema = z.object({
        model: z.string(),
        domain: z.array(z.any()).default([]),
        fields: z.array(z.string()).optional(),
        limit: z.number().default(10),
        offset: z.number().default(0),
      });

      const params = schema.parse(args);
      return await client.searchRead(
        params.model,
        params.domain,
        params.fields,
        params.limit,
        params.offset
      );
    },

    'odoo.create': async (args) => {
      const schema = z.object({
        model: z.string(),
        values: z.record(z.any()),
      });

      const params = schema.parse(args);
      const id = await client.create(params.model, params.values);
      return { id, created: true };
    },

    'odoo.write': async (args) => {
      const schema = z.object({
        model: z.string(),
        ids: z.array(z.number()),
        values: z.record(z.any()),
      });

      const params = schema.parse(args);
      const success = await client.write(params.model, params.ids, params.values);
      return { success, updated: params.ids.length };
    },

    'odoo.unlink': async (args) => {
      const schema = z.object({
        model: z.string(),
        ids: z.array(z.number()),
      });

      const params = schema.parse(args);
      const success = await client.unlink(params.model, params.ids);
      return { success, deleted: params.ids.length };
    },
  };

  return { tools, handlers };
}
