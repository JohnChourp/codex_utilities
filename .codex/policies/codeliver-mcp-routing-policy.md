# CodeDeliver MCP Smart Routing Policy (On-Demand)

Load this policy whenever task intent may map to Playwright/Figma/Notion/Linear MCP usage.

## MCP Smart Routing (Playwright / Figma / Notion / Linear)

- **Auto-first policy (mandatory):** in non-Plan mode, automatically select and use the most relevant MCP server among `playwright`, `figma`, `notion`, `linear` when the user intent clearly matches one of them; do not ask permission first.
- **Trigger matrix (mandatory):**
  - `playwright`: browser automation, UI bug reproduction, screenshots/snapshots, form flows, regressions, real-page interaction debugging.
  - `figma`: Figma links/node IDs, design-to-code, visual parity checks, extracting design context/assets/variables.
  - `notion`: knowledge capture, documentation, FAQ/how-to pages, decision logs, research synthesis into Notion.
  - `linear`: issue/project/cycle/label/status workflows in Linear.
- **PM conflict policy (mandatory):** `ClickUp` remains primary baseline for CodeDeliver task workflow. Use `linear` as secondary only when the user explicitly asks for Linear, or when the context is clearly a Linear workspace workflow.
- **Fallback policy (mandatory):** if an MCP server is unavailable or auth fails, continue with the best non-blocking fallback flow and provide exact setup/login commands only when needed.
  - `notion`: `codex mcp add notion --url https://mcp.notion.com/mcp` then `codex mcp login notion`
  - `linear`: `codex mcp add linear --url https://mcp.linear.app/mcp` then `codex mcp login linear`
  - `figma`: add in `~/.codex/config.toml`:
    - `[mcp_servers.figma]`
    - `url = "https://mcp.figma.com/mcp"`
    - `bearer_token_env_var = "FIGMA_OAUTH_TOKEN"`
    - `http_headers = { "X-Figma-Region" = "us-east-1" }`
  - verify MCP availability with `codex mcp list` (and restart Codex after auth/config changes).
- **Guardrails (mandatory):**
  - Do not force MCP usage when it does not materially improve the task.
  - Do not invent data from `notion`/`linear`/`figma` when access is missing; state the limitation explicitly.
  - Keep tool usage minimal and justify MCP choice briefly in progress updates.
- **CodeDeliver examples (reference):**
  - Prompt like `βρες γιατί δεν ανοίγει modal στο sap` -> prefer `playwright` first for reproduction and UI-state evidence.
  - Prompt with Figma URL for SAP/Panel modal parity -> prefer `figma` first, then implement with existing project conventions.
  - Prompt like `γράψε doc/faq για τη ροή` -> prefer `notion` for structured capture (unless user asks local markdown only).
  - Prompt like `φτιάξε/update issue` -> keep `ClickUp` baseline; use `linear` only when explicitly requested or clearly required by workspace context.
