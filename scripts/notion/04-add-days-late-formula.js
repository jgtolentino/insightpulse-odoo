require('dotenv').config();
const { Client } = require('@notionhq/client');

const notion = new Client({ auth: process.env.NOTION_API_KEY });
const DATABASE_ID = process.env.NOTION_DATABASE_ID || '29387692-d25c-813c-8098-c7d0c08b9753';

async function addDaysLateFormula() {
  try {
    await notion.databases.update({
      database_id: DATABASE_ID,
      properties: {
        'Days late': {
          formula: {
            expression: 'if(prop("Status") == "Done" or prop("Status") == "Completed", 0, if(empty(prop("Due")), 0, if(prop("Due") > now(), 0, dateBetween(now(), prop("Due"), "days"))))'
          }
        }
      }
    });

    console.log('✅ Added "Days late" formula property to database');
    console.log('   Formula: if task is Done/Completed → 0, else → days between now and Due date');
  } catch (error) {
    if (error.code === 'validation_error' && error.message.includes('already exists')) {
      console.log('✅ "Days late" property already exists');
    } else {
      console.error('❌ Error:', error.message);
      process.exit(1);
    }
  }
}

addDaysLateFormula();
