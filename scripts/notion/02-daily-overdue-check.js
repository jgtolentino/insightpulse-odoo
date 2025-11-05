require('dotenv').config();
const { Client } = require('@notionhq/client');

const notion = new Client({ auth: process.env.NOTION_API_KEY });
const DATABASE_ID = process.env.NOTION_DATABASE_ID || '29387692-d25c-813c-8098-c7d0c08b9753';

async function findOverdueTasks() {
  const today = new Date().toISOString().split('T')[0];
  
  const response = await notion.databases.query({
    database_id: DATABASE_ID,
    filter: {
      and: [
        { property: 'Status', status: { does_not_equal: 'Done' } },
        { property: 'Status', status: { does_not_equal: 'Completed' } },
        { property: 'Due', date: { before: today } }
      ]
    }
  });

  console.log(`Found ${response.results.length} overdue tasks`);
  return response.results;
}

async function markTaskOverdue(page) {
  const taskName = page.properties.Name?.title?.[0]?.plain_text || 'Untitled';
  const assignee = page.properties.Assignee?.people?.[0];

  // Update status to Blocked (overdue)
  await notion.pages.update({
    page_id: page.id,
    properties: {
      Status: { status: { name: 'Blocked' } }
    }
  });

  // Add comment with @mention
  const commentBlocks = [
    {
      type: 'text',
      text: {
        content: `🔔 Daily overdue check: This task is past due.\n`
      }
    }
  ];

  if (assignee?.id) {
    commentBlocks.push({
      type: 'mention',
      mention: { type: 'user', user: { id: assignee.id } }
    });
    commentBlocks.push({
      type: 'text',
      text: { content: ' — Please update status or provide ETA.' }
    });
  }

  await notion.comments.create({
    parent: { page_id: page.id },
    rich_text: commentBlocks
  });

  console.log(`✅ Marked overdue: ${taskName}`);
}

async function main() {
  try {
    const overdueTasks = await findOverdueTasks();
    
    for (const task of overdueTasks) {
      const status = task.properties.Status?.status?.name;
      
      // Skip if already marked as Blocked
      if (status !== 'Blocked') {
        await markTaskOverdue(task);
      }
    }
    
    console.log('✅ Overdue check complete');
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

main();
