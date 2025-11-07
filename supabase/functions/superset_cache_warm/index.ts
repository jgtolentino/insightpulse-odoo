// deno-lint-ignore-file no-explicit-any
const supersetBaseUrl = Deno.env.get("SUPERSET_BASE_URL")!;
const supersetApiKey = Deno.env.get("SUPERSET_API_KEY")!;
const dashboardsEnv = Deno.env.get("SUPERSET_DASHBOARDS") || "1 2 3";
const dashboards = dashboardsEnv.split(" ").filter((d) => d.trim());

Deno.serve(async (_req) => {
  try {
    const results: any[] = [];

    for (const dashboardId of dashboards) {
      try {
        const response = await fetch(
          `${supersetBaseUrl}/api/v1/dashboard/${dashboardId}/warm_up_cache`,
          {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${supersetApiKey}`,
              "Content-Type": "application/json",
            },
          }
        );

        results.push({
          dashboard: dashboardId,
          ok: response.ok,
          status: response.status,
        });

        console.log(`Warmed dashboard ${dashboardId}: ${response.status}`);
      } catch (e) {
        results.push({
          dashboard: dashboardId,
          ok: false,
          error: String(e),
        });
      }
    }

    return new Response(
      JSON.stringify({
        warmed: results,
        success: results.filter((r) => r.ok).length,
        total: results.length,
      }),
      {
        status: 200,
        headers: { "content-type": "application/json" },
      }
    );
  } catch (e) {
    console.error("Superset cache warm error:", e);
    return new Response(
      JSON.stringify({ error: String(e) }),
      {
        status: 500,
        headers: { "content-type": "application/json" },
      }
    );
  }
});
