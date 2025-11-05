import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { Client } from "https://esm.sh/@notionhq/client@2.2.15";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

interface NotionPage {
  id: string;
  properties: {
    Name?: { title?: Array<{ plain_text?: string }> };
    Status?: { status?: { name?: string } };
    "Due date"?: { date?: { start?: string } };
    Assignee?: { people?: Array<{ id?: string; name?: string }> };
  };
}

/**
 * Calculate days late for a task
 */
function calculateDaysLate(dueDate: string): number {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const due = new Date(dueDate);
  due.setHours(0, 0, 0, 0);

  const diffTime = today.getTime() - due.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  return diffDays > 0 ? diffDays : 0;
}

/**
 * Process overdue tasks
 */
async function processOverdueTasks() {
  const apiKey = Deno.env.get("NOTION_API_KEY");
  const databaseId = Deno.env.get("NOTION_DATABASE_ID");

  if (!apiKey || !databaseId) {
    throw new Error("Missing NOTION_API_KEY or NOTION_DATABASE_ID");
  }

  const notion = new Client({ auth: apiKey });
  const today = new Date().toISOString().split("T")[0];

  // Query for overdue tasks
  const response = await notion.databases.query({
    database_id: databaseId,
    filter: {
      and: [
        {
          property: "Status",
          status: {
            does_not_equal: "Complete",
          },
        },
        {
          property: "Due date",
          date: {
            before: today,
          },
        },
      ],
    },
  });

  console.log(`Found ${response.results.length} overdue tasks`);

  const processed = [];

  for (const page of response.results as NotionPage[]) {
    const taskName = page.properties.Name?.title?.[0]?.plain_text || "Untitled";
    const currentStatus = page.properties.Status?.status?.name;
    const dueDate = page.properties["Due date"]?.date?.start;
    const assignee = page.properties.Assignee?.people?.[0];

    // Skip if already marked as Overdue
    if (currentStatus === "Overdue") {
      console.log(`Skipping ${taskName} - already overdue`);
      continue;
    }

    const daysLate = dueDate ? calculateDaysLate(dueDate) : 0;

    // Update status to Overdue
    await notion.pages.update({
      page_id: page.id,
      properties: {
        Status: {
          status: {
            name: "Overdue",
          },
        },
      },
    });

    // Add comment
    const commentBlocks: any[] = [
      {
        type: "text",
        text: { content: `⏰ Overdue: ${taskName} — ${daysLate} days late.\n` },
      },
    ];

    if (assignee?.id) {
      commentBlocks.push({
        type: "mention",
        mention: { type: "user", user: { id: assignee.id } },
      });
      commentBlocks.push({
        type: "text",
        text: { content: " please update or escalate." },
      });
    }

    await notion.comments.create({
      parent: { page_id: page.id },
      rich_text: commentBlocks,
    });

    processed.push({ task: taskName, daysLate });
    console.log(`Processed: ${taskName} (${daysLate} days late)`);
  }

  return processed;
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const processed = await processOverdueTasks();

    return new Response(
      JSON.stringify({
        success: true,
        timestamp: new Date().toISOString(),
        processed: processed.length,
        tasks: processed,
      }),
      {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
        status: 200,
      }
    );
  } catch (error) {
    console.error("Error:", error);

    return new Response(
      JSON.stringify({
        success: false,
        error: error.message,
      }),
      {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
        status: 500,
      }
    );
  }
});
