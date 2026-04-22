import { NextResponse, type NextRequest } from "next/server";
import { readChain } from "@/lib/server/read-chain";
import { resolveMode } from "@/lib/server/mode";
import { fixtureChain } from "@/lib/fixtures/chain";
import { markChainIntegrity } from "@/lib/parsers/chain";
import type { ChainEntry } from "@/lib/types/episteme";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET(req: NextRequest) {
  const limit = clampLimit(req.nextUrl.searchParams.get("limit"));
  const mode = resolveMode();

  if (mode === "fixtures") {
    const entries = markChainIntegrity(fixtureChain).slice(0, limit);
    return NextResponse.json({
      entries,
      integrity: "ok" as const,
      mode,
      source: { kind: "fixtures" },
      warnings: [],
    });
  }

  try {
    const result = await readChain(limit);
    return NextResponse.json({
      entries: result.entries satisfies ChainEntry[],
      integrity: result.integrity,
      mode,
      source: { kind: "live", ...result.source },
      warnings: result.warnings,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "unknown";
    return NextResponse.json(
      {
        entries: [],
        integrity: "ok" as const,
        mode,
        source: { kind: "live" },
        warnings: [`fatal read error: ${message}`],
      },
      { status: 200 },
    );
  }
}

function clampLimit(raw: string | null): number {
  if (!raw) return 50;
  const n = Number.parseInt(raw, 10);
  if (!Number.isFinite(n) || n <= 0) return 50;
  return Math.min(500, Math.max(1, n));
}
