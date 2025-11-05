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
    Approver?: { people?: Array<{ id?: string; name?: string }> };
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
 * Process escalations for 2+ day late tasks
 */
async function processEscalations() {
  const apiKey = Deno.env.get("NOTION_API_KEY");
  const databaseId = Deno.env.get("NOTION_DATABASE_ID");

  if (!apiKey || !databaseId) {
    throw new Error("Missing NOTION_API_KEY or NOTION_DATABASE_ID");
  }

  const notion = new Client({ auth: apiKey });

  // Calculate date 2 days ago
  const twoDaysAgo = new Date();
  twoDaysAgo.setDate(twoDaysAgo.getDate() - 2);
  const filterDate = twoDaysAgo.toISOString().split("T")[0];

  // Query for tasks 2+ days late
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
            before: filterDate,
          },
        },
      ],
    },
  });

  console.log(`Found ${response.results.length} tasks for escalation`);

  const escalated = [];

  for (const page of response.results as NotionPage[]) {
    const taskName = page.properties.Name?.title?.[0]?.plain_text || "Untitled";
    const assignee = page.properties.Assignee?.people?.[0];
    const approver = page.properties.Approver?.people?.[0];
    const dueDate = page.properties["Due date"]?.date?.start;

    const daysLate = dueDate ? calculateDaysLate(dueDate) : 0;

    // Check if already escalated today
    const comments = await notion.comments.list({ block_id: page.id });
    const todayStr = new Date().toISOString().split("T")[0];
    const alreadyEscalatedToday = comments.results.some((comment: any) => {
      const commentDate = new Date(comment.created_time).toISOString().split("T")[0];
      const isEscalation = comment.rich_text?.[0]?.plain_text?.includes("🚨 ESCALATION");
      return commentDate === todayStr && isEscalation;
    });

    if (alreadyEscalatedToday) {
      console.log(`Skipping ${taskName} - already escalated today`);
      continue;
    }

    // Build escalation comment
    const commentBlocks: any[] = [
      {
        type: "text",
        text: {
          content:
            `🚨 ESCALATION: ${taskName}\n` +
            `⏰ ${daysLate} days overdue\n` +
            `📋 Status: Requires immediate attention\n\n`,
        },
      },
    ];

    if (approver?.id) {
      commentBlocks.push({
        type: "mention",
        mention: { type: "user", user: { id: approver.id } },
      });
      commentBlocks.push({
        type: "text",
        text: { content: " — This task requires your review. " },
      });
    }

    if (assignee?.id) {
      commentBlocks.push({
        type: "mention",
        mention: { type: "user", user: { id: assignee.id } },
      });
      commentBlocks.push({
        type: "text",
        text: { content: " — Please provide status update or blockers." },
      });
    }

    await notion.comments.create({
      parent: { page_id: page.id },
      rich_text: commentBlocks,
    });

    escalated.push({ task: taskName, daysLate });
    console.log(`Escalated: ${taskName} (${daysLate} days late)`);
  }

  return escalated;
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const escalated = await processEscalations();

    return new Response(
      JSON.stringify({
        success: true,
        timestamp: new Date().toISOString(),
        escalated: escalated.length,
        tasks: escalated,
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
