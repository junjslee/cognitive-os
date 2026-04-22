import "server-only";

export type EpistemeMode = "live" | "fixtures";

/**
 * Resolve the operating mode for route handlers.
 *
 * Default:
 *  - NODE_ENV=production → "fixtures" (marketing deploys stay rich without kernel access)
 *  - else                → "live"     (local dev reads $EPISTEME_HOME)
 *
 * Explicit EPISTEME_MODE overrides the default.
 */
export function resolveMode(): EpistemeMode {
  const explicit = process.env.EPISTEME_MODE?.trim().toLowerCase();
  if (explicit === "live" || explicit === "fixtures") return explicit;
  return process.env.NODE_ENV === "production" ? "fixtures" : "live";
}
