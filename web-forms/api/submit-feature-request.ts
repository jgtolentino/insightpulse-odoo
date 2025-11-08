/**
 * Serverless Function: Submit Feature Request to Notion
 *
 * Deploy to Vercel, Netlify, or any serverless platform
 *
 * Environment Variables Required:
 * - NOTION_API_TOKEN
 * - NOTION_FEATURE_DB_ID
 *
 * Usage:
 *   POST /api/submit-feature-request
 *   Body: { title, category, useCase, priority, email, solution?, tags? }
 */

import { Client } from '@notionhq/client';

interface FeatureRequest {
  title: string;
  category: string;
  useCase: string;
  priority: string;
  email: string;
  solution?: string;
  tags?: string;
}

// Priority emoji mapping
const PRIORITY_EMOJI: Record<string, string> = {
  'Critical': '🔥',
  'High': '⬆️',
  'Medium': '➡️',
  'Low': '⬇️'
};

export default async function handler(req: Request): Promise<Response> {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return new Response(
      JSON.stringify({ error: 'Method not allowed' }),
      { status: 405, headers: { 'Content-Type': 'application/json' } }
    );
  }

  // CORS headers
  const headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST',
    'Access-Control-Allow-Headers': 'Content-Type'
  };

  try {
    // Parse request body
    const data: FeatureRequest = await req.json();

    // Validate required fields
    const { title, category, useCase, priority, email } = data;
    if (!title || !category || !useCase || !priority || !email) {
      return new Response(
        JSON.stringify({ error: 'Missing required fields' }),
        { status: 400, headers }
      );
    }

    // Initialize Notion client
    const notion = new Client({
      auth: process.env.NOTION_API_TOKEN
    });

    const databaseId = process.env.NOTION_FEATURE_DB_ID;
    if (!databaseId) {
      throw new Error('NOTION_FEATURE_DB_ID not configured');
    }

    // Generate external ID
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const categorySlug = category.toLowerCase().replace(/\s+/g, '_');
    const externalId = `feature_${categorySlug}_${timestamp}`;

    // Build page content
    const contentBlocks = [
      {
        object: 'block' as const,
        type: 'heading_2' as const,
        heading_2: {
          rich_text: [{ type: 'text' as const, text: { content: 'Use Case' } }]
        }
      },
      {
        object: 'block' as const,
        type: 'paragraph' as const,
        paragraph: {
          rich_text: [{ type: 'text' as const, text: { content: useCase } }]
        }
      }
    ];

    // Add proposed solution if provided
    if (data.solution) {
      contentBlocks.push(
        {
          object: 'block' as const,
          type: 'heading_2' as const,
          heading_2: {
            rich_text: [{ type: 'text' as const, text: { content: 'Proposed Solution' } }]
          }
        },
        {
          object: 'block' as const,
          type: 'paragraph' as const,
          paragraph: {
            rich_text: [{ type: 'text' as const, text: { content: data.solution } }]
          }
        }
      );
    }

    // Add metadata
    const metadata = `Submitted by: ${email}\nSubmitted on: ${new Date().toISOString()}`;
    contentBlocks.push({
      object: 'block' as const,
      type: 'callout' as const,
      callout: {
        rich_text: [{ type: 'text' as const, text: { content: metadata } }],
        icon: { emoji: 'ℹ️' }
      }
    });

    // Parse tags
    const tagList = data.tags
      ? data.tags.split(',').map(tag => tag.trim()).filter(Boolean)
      : [];

    // Build properties
    const properties: any = {
      'Title': {
        title: [{ text: { content: title } }]
      },
      'Status': {
        select: { name: '🆕 New' }
      },
      'Priority': {
        select: { name: `${PRIORITY_EMOJI[priority]} ${priority}` }
      },
      'Category': {
        multi_select: [{ name: category }]
      },
      'Requester Email': {
        email: email
      },
      'Use Case': {
        rich_text: [{ text: { content: useCase.substring(0, 2000) } }]
      },
      'Requested Date': {
        date: { start: new Date().toISOString() }
      },
      'Votes': {
        number: 0
      },
      'External ID': {
        rich_text: [{ text: { content: externalId } }]
      },
      'Last Synced': {
        date: { start: new Date().toISOString() }
      }
    };

    // Add tags if provided
    if (tagList.length > 0) {
      properties['Tags'] = {
        multi_select: tagList.map(tag => ({ name: tag }))
      };
    }

    // Check if page already exists (idempotency)
    const existingPages = await notion.databases.query({
      database_id: databaseId,
      filter: {
        property: 'External ID',
        rich_text: {
          equals: externalId
        }
      }
    });

    let pageId: string;

    if (existingPages.results.length > 0) {
      // Update existing page
      pageId = existingPages.results[0].id;
      await notion.pages.update({
        page_id: pageId,
        properties
      });
    } else {
      // Create new page
      const response = await notion.pages.create({
        parent: { database_id: databaseId },
        properties,
        children: contentBlocks
      });
      pageId = response.id;
    }

    // Return success response
    return new Response(
      JSON.stringify({
        success: true,
        pageId,
        externalId,
        message: 'Feature request submitted successfully!'
      }),
      { status: 200, headers }
    );

  } catch (error: any) {
    console.error('Error submitting feature request:', error);

    return new Response(
      JSON.stringify({
        error: 'Failed to submit feature request',
        details: error.message
      }),
      { status: 500, headers }
    );
  }
}

// For Vercel Edge Runtime
export const config = {
  runtime: 'edge'
};
