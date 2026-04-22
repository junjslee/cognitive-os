import "server-only";

import os from "node:os";
import path from "node:path";

export interface HomeResolution {
  /** Absolute path to $EPISTEME_HOME. null if unresolvable. */
  path: string | null;
  /** Source of the resolution, for telemetry / UI diagnostics. */
  source: "env" | "home-default" | "unresolved";
  /** Non-empty when the env was set but rejected (relative, empty, etc.). */
  error?: string;
}

/**
 * Resolves $EPISTEME_HOME. Absolute path required when the env var is set;
 * relative paths are rejected to avoid cwd-resolution surprises in server
 * contexts. Default is $HOME/.episteme.
 */
export function resolveEpistemeHome(): HomeResolution {
  const env = process.env.EPISTEME_HOME?.trim();
  if (env) {
    if (!path.isAbsolute(env)) {
      return {
        path: null,
        source: "unresolved",
        error: `EPISTEME_HOME must be an absolute path (got ${env})`,
      };
    }
    return { path: env, source: "env" };
  }
  const home = os.homedir();
  if (!home) {
    return {
      path: null,
      source: "unresolved",
      error: "no home directory available",
    };
  }
  return { path: path.join(home, ".episteme"), source: "home-default" };
}

/** Resolve the framework directory under $EPISTEME_HOME. */
export function frameworkDir(): string | null {
  const { path: home } = resolveEpistemeHome();
  return home ? path.join(home, "framework") : null;
}

/** Resolve a specific framework stream file. */
export function protocolsPath(): string | null {
  const dir = frameworkDir();
  return dir ? path.join(dir, "protocols.jsonl") : null;
}

export function deferredDiscoveriesPath(): string | null {
  const dir = frameworkDir();
  return dir ? path.join(dir, "deferred_discoveries.jsonl") : null;
}
