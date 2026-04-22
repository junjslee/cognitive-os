"use client";

import { ReasoningMatrix } from "./ReasoningMatrix";
import { EmptyState } from "./EmptyState";
import { useLiveResource } from "@/lib/hooks/use-live-resource";
import type { ReasoningSurface } from "@/lib/types/episteme";

interface LiveReasoningMatrixProps {
  intervalMs?: number;
  className?: string;
}

interface SurfacePayload {
  surface: ReasoningSurface | null;
  age_minutes: number | null;
  mode: "live" | "fixtures";
  source?: unknown;
  warnings?: string[];
}

const FALLBACK: SurfacePayload = {
  surface: null,
  age_minutes: null,
  mode: "live",
  warnings: [],
};

export function LiveReasoningMatrix({
  intervalMs = 10_000,
  className,
}: LiveReasoningMatrixProps) {
  const { data, loading, error, stale } = useLiveResource<SurfacePayload>(
    "/api/surface",
    FALLBACK,
    { intervalMs },
  );

  if (error && !data.surface) {
    return (
      <EmptyState
        title="Reasoning surface unreachable"
        hint={`The /api/surface endpoint returned an error (${error}). The kernel may be down or the project path misconfigured. Set $EPISTEME_PROJECT to the repo root where .episteme/reasoning-surface.json lives.`}
        tone="error"
        className={className}
      />
    );
  }

  if (!data.surface) {
    return (
      <EmptyState
        title={loading ? "Reading reasoning surface…" : "No active reasoning surface"}
        hint="Run `episteme init` in your project root, then write a Reasoning Surface for your current core question. The kernel's guard creates .episteme/reasoning-surface.json on the next high-impact op."
        className={className}
      />
    );
  }

  return (
    <div className={className}>
      {stale && (
        <div className="mb-2 font-mono text-[0.625rem] uppercase tracking-wider text-unknown">
          refreshing · last good data shown
        </div>
      )}
      {data.age_minutes !== null && data.age_minutes > 30 && (
        <div className="mb-2 font-mono text-[0.625rem] uppercase tracking-wider text-unknown">
          surface is {data.age_minutes}m old · kernel TTL exceeded
        </div>
      )}
      <ReasoningMatrix surface={data.surface} />
    </div>
  );
}
