import { NextResponse } from "next/server";
import { readProtocols } from "@/lib/server/read-protocols";
import { resolveMode } from "@/lib/server/mode";
import { fixtureProtocols } from "@/lib/fixtures/chain";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET() {
  const mode = resolveMode();

  if (mode === "fixtures") {
    return NextResponse.json({
      protocols: fixtureProtocols,
      mode,
      source: { kind: "fixtures" },
      warnings: [],
    });
  }

  try {
    const result = await readProtocols();
    return NextResponse.json({
      protocols: result.protocols,
      mode,
      source: { kind: "live", ...result.source },
      warnings: result.warnings,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "unknown";
    return NextResponse.json(
      {
        protocols: [],
        mode,
        source: { kind: "live" },
        warnings: [`fatal read error: ${message}`],
      },
      { status: 200 },
    );
  }
}
