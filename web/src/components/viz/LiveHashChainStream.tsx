"use client";

import { HashChainStream } from "./HashChainStream";
import { EmptyState } from "./EmptyState";
import { useLiveResource } from "@/lib/hooks/use-live-resource";
import { cn } from "@/lib/utils";
import type { ChainEntry } from "@/lib/types/episteme";

interface LiveHashChainStreamProps {
  intervalMs?: number;
  limit?: number;
  className?: string;
}

interface ChainPayload {
  entries: ChainEntry[];
  integrity: "ok" | "broken";
  mode: "live" | "fixtures";
  source?: unknown;
  warnings?: string[];
}

const FALLBACK: ChainPayload = {
  entries: [],
  integrity: "ok",
  mode: "live",
  warnings: [],
};

export function LiveHashChainStream({
  intervalMs = 10_000,
  limit = 50,
  className,
}: LiveHashChainStreamProps) {
  const url = `/api/chain?limit=${limit}`;
  const { data, loading, error } = useLiveResource<ChainPayload>(
    url,
    FALLBACK,
    { intervalMs },
  );

  if (error && data.entries.length === 0) {
    return (
      <EmptyState
        title="Chain stream unreachable"
        hint={`/api/chain returned ${error}. Check that $EPISTEME_HOME resolves to a directory the server can read.`}
        tone="error"
        className={className}
      />
    );
  }

  if (data.entries.length === 0) {
    return (
      <EmptyState
        title={loading ? "Reading hash chain…" : "Chain genesis pending"}
        hint="No hash-chained records under $EPISTEME_HOME/framework/. The first protocol synthesized on a successful op (Fence removal, Axiomatic judgment, Blueprint D firing) lands as the chain's first record."
        className={className}
      />
    );
  }

  return (
    <div className={cn("flex flex-col gap-2 h-full", className)}>
      {data.integrity === "broken" && (
        <div className="border border-disconfirm/40 bg-disconfirm/5 px-3 py-1.5 font-mono text-[0.6875rem] uppercase tracking-wider text-disconfirm">
          chain integrity: BROKEN — first mismatch highlighted below
        </div>
      )}
      <HashChainStream entries={data.entries} className="flex-1" />
    </div>
  );
}
