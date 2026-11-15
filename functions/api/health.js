// AI-assisted: Claude Code (claude-opus-5-5), reviewed by cesarp03

// GET /api/health. Reports whether the LLM secret exists on the platform,
// never its value.
export function onRequestGet({ env }) {
  return Response.json({
    status: "ok",
    llm_key_configured: Boolean(env.LLM_API_KEY),
  });
}
