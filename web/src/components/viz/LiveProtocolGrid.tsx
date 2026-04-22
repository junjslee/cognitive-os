"use client";

import { ProtocolNode } from "./ProtocolNode";
import { EmptyState } from "./EmptyState";
import { useLiveResource } from "@/lib/hooks/use-live-resource";
import { cn } from "@/lib/utils";
import type { Protocol } from "@/lib/types/episteme";

interface LiveProtocolGridProps {
  intervalMs?: number;
  className?: string;
}

interface ProtocolPayload {
  protocols: Protocol[];
  mode: "live" | "fixtures";
  source?: unknown;
  warnings?: string[];
}

const FALLBACK: ProtocolPayload = {
  protocols: [],
  mode: "live",
  warnings: [],
};

export function LiveProtocolGrid({
  intervalMs = 10_000,
  className,
}: LiveProtocolGridProps) {
  const { data, loading, error } = useLiveResource<ProtocolPayload>(
    "/api/protocols",
    FALLBACK,
    { intervalMs },
  );

  if (error && data.protocols.length === 0) {
    return (
      <EmptyState
        title="Protocols stream unreachable"
        hint={`/api/protocols returned ${error}.`}
        tone="error"
        className={className}
      />
    );
  }

  if (data.protocols.length === 0) {
    return (
      <EmptyState
        title={loading ? "Reading synthesized protocols…" : "No protocols synthesized yet"}
        hint="The framework records its first protocol on a successful blueprint firing. Run a constraint-removal op in a project with episteme installed; Fence Reconstruction synthesizes the first protocol on clean resolution."
        className={className}
      />
    );
  }

  return (
    <ul
      className={cn(
        "grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3",
        className,
      )}
    >
      {data.protocols.map((p) => (
        <li key={p.id}>
          <ProtocolNode protocol={p} />
        </li>
      ))}
    </ul>
  );
}
