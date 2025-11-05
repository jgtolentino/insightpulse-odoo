#!/usr/bin/env node
/**
 * Test Notion API connection and database access
 */

import { Client } from '@notionhq/client';

const notion = new Client({ auth: process.env.NOTION_API_KEY });
const DATABASE_ID = process.env.NOTION_DATABASE_ID || 'd3df2f839b1f469ca390aa14e74db9ad';

async function testConnection() {
  console.log('🔍 Testing Notion API connection...\n');

  try {
    // Test 1: Get database info
    console.log('Test 1: Fetching database info...');
    const database = await notion.databases.retrieve({ database_id: DATABASE_ID });
    console.log(`✅ Database: ${database.title[0]?.plain_text || 'Untitled'}`);
    console.log(`   Properties: ${Object.keys(database.properties).length}`);

    // Test 2: Query tasks
    console.log('\nTest 2: Querying tasks...');
    const response = await notion.databases.query({
      database_id: DATABASE_ID,
      page_size: 5
    });
    console.log(`✅ Found ${response.results.length} tasks (showing 5)`);

    // Test 3: Show sample tasks
    console.log('\nTest 3: Sample tasks:');
    for (const page of response.results) {
      const taskName = page.properties.Name?.title?.[0]?.plain_text || 'Untitled';
      const status = page.properties.Status?.status?.name || 'No status';
      const dueDate = page.properties['Due date']?.date?.start || 'No due date';
      console.log(`   - ${taskName}`);
      console.log(`     Status: ${status} | Due: ${dueDate}`);
    }

    console.log('\n✅ All tests passed! Ready to run automations.');
  } catch (error) {
    console.error('\n❌ Connection test failed:', error.message);
    process.exit(1);
  }
}

testConnection();
