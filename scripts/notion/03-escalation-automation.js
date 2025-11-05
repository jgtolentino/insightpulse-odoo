require('dotenv').config();
const { Client } = require('@notionhq/client');

const notion = new Client({ auth: process.env.NOTION_API_KEY });
const DATABASE_ID = process.env.NOTION_DATABASE_ID || '29387692-d25c-813c-8098-c7d0c08b9753';

function calculateDaysLate(dueDate) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const due = new Date(dueDate);
  due.setHours(0, 0, 0, 0);
  
  const diffTime = today - due;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  return diffDays > 0 ? diffDays : 0;
}

async function findTasksForEscalation() {
  const twoDaysAgo = new Date();
  twoDaysAgo.setDate(twoDaysAgo.getDate() - 2);
  const filterDate = twoDaysAgo.toISOString().split('T')[0];
  
  const response = await notion.databases.query({
    database_id: DATABASE_ID,
    filter: {
      and: [
        { property: 'Status', status: { does_not_equal: 'Done' } },
        { property: 'Status', status: { does_not_equal: 'Completed' } },
        { property: 'Due', date: { before: filterDate } }
      ]
    }
  });

  console.log(`Found ${response.results.length} tasks for escalation (2+ days late)`);
  return response.results;
}

async function escalateTask(page) {
  const taskName = page.properties.Name?.title?.[0]?.plain_text || 'Untitled';
  const assignee = page.properties.Assignee?.people?.[0];
  const approver = page.properties.Approver?.people?.[0];
  const dueDate = page.properties.Due?.date?.start;
  
  const daysLate = dueDate ? calculateDaysLate(dueDate) : 0;

  // Check if already escalated today
  const comments = await notion.comments.list({ block_id: page.id });
  const todayStr = new Date().toISOString().split('T')[0];
  const alreadyEscalatedToday = comments.results.some(comment => {
    const commentDate = new Date(comment.created_time).toISOString().split('T')[0];
    const isEscalation = comment.rich_text?.[0]?.plain_text?.includes('🚨 ESCALATION');
    return commentDate === todayStr && isEscalation;
  });

  if (alreadyEscalatedToday) {
    console.log(`⏭️  ${taskName} - already escalated today`);
    return;
  }

  // Create escalation comment
  const commentBlocks = [
    {
      type: 'text',
      text: {
        content: `🚨 ESCALATION: ${taskName}\n⏰ ${daysLate} days overdue\n📋 Status: Requires immediate attention\n\n`
      }
    }
  ];

  if (approver?.id) {
    commentBlocks.push({
      type: 'mention',
      mention: { type: 'user', user: { id: approver.id } }
    });
    commentBlocks.push({
      type: 'text',
      text: { content: ' — This task requires your review. ' }
    });
  }

  if (assignee?.id) {
    commentBlocks.push({
      type: 'mention',
      mention: { type: 'user', user: { id: assignee.id } }
    });
    commentBlocks.push({
      type: 'text',
      text: { content: ' — Please provide status update or blockers.' }
    });
  }

  await notion.comments.create({
    parent: { page_id: page.id },
    rich_text: commentBlocks
  });

  console.log(`✅ Escalated: ${taskName} (${daysLate} days late)`);
}

async function main() {
  try {
    const tasks = await findTasksForEscalation();
    
    for (const task of tasks) {
      await escalateTask(task);
    }
    
    console.log('✅ Escalation automation complete');
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

main();
