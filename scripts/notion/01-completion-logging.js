#!/usr/bin/env node
/**
 * Notion Automation: Completion Logging
 * Trigger: Due date is edited AND Status = Complete
 * Action: Add comment with completion details
 *
 * Usage: node 01-completion-logging.js
 */

import { Client } from '@notionhq/client';

const notion = new Client({ auth: process.env.NOTION_API_KEY });
const DATABASE_ID = process.env.NOTION_DATABASE_ID || 'd3df2f839b1f469ca390aa14e74db9ad';

/**
 * Watch for changes to database pages
 * This would typically run as a webhook listener or cron job
 */
async function watchCompletionEvents() {
  console.log('🔍 Watching for completion events...');

  // Query recently edited pages with Status = Complete
  const response = await notion.databases.query({
    database_id: DATABASE_ID,
    filter: {
      property: 'Status',
      status: {
        equals: 'Complete'
      }
    },
    sorts: [
      {
        property: 'Last edited time',
        direction: 'descending'
      }
    ],
    page_size: 10 // Check last 10 completed items
  });

  for (const page of response.results) {
    await processCompletedTask(page);
  }
}

/**
 * Process a completed task and add audit comment
 */
async function processCompletedTask(page) {
  const properties = page.properties;

  // Extract task details
  const taskName = properties.Name?.title?.[0]?.plain_text || 'Untitled';
  const assignee = properties.Assignee?.people?.[0]?.name || 'Unassigned';
  const approver = properties.Approver?.people?.[0]?.name || 'No approver';
  const dueDate = properties['Due date']?.date?.start || 'No due date';
  const lastEdited = page.last_edited_time;

  // Check if we already commented (avoid duplicates)
  const comments = await notion.comments.list({ block_id: page.id });
  const hasCompletionComment = comments.results.some(comment =>
    comment.rich_text?.[0]?.plain_text?.includes('✅ Task completed:')
  );

  if (hasCompletionComment) {
    console.log(`⏭️  Skipping ${taskName} - already logged`);
    return;
  }

  // Add completion comment
  const commentText = `✅ Task completed: ${taskName}
Completed by: ${assignee}
Reviewed by: ${approver}
Due: ${dueDate}
Timestamp: ${new Date(lastEdited).toLocaleString('en-PH', { timeZone: 'Asia/Manila' })}`;

  await notion.comments.create({
    parent: { page_id: page.id },
    rich_text: [
      {
        type: 'text',
        text: { content: commentText }
      }
    ]
  });

  console.log(`✅ Logged completion: ${taskName}`);
}

/**
 * Main execution
 */
async function main() {
  try {
    await watchCompletionEvents();
    console.log('✅ Completion logging complete');
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { watchCompletionEvents, processCompletedTask };
