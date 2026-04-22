import "server-only";

import path from "node:path";

export interface ProjectResolution {
  path: string;
  source: "env" | "cwd";
  error?: string;
}

/**
 * Resolves the project directory that owns the active .episteme/reasoning-surface.json.
 * $EPISTEME_PROJECT wins when set (absolute required). Fallback is process.cwd()
 * of the running Next.js server — useful for local dev when the site is run
 * from the repo root of the project being instrumented.
 */
export function resolveEpistemeProject(): ProjectResolution {
  const env = process.env.EPISTEME_PROJECT?.trim();
  if (env) {
    if (!path.isAbsolute(env)) {
      return {
        path: process.cwd(),
        source: "cwd",
        error: `EPISTEME_PROJECT must be absolute (got ${env}); fell back to cwd`,
      };
    }
    return { path: env, source: "env" };
  }
  return { path: process.cwd(), source: "cwd" };
}

export function surfacePath(): string {
  const { path: root } = resolveEpistemeProject();
  return path.join(root, ".episteme", "reasoning-surface.json");
}
