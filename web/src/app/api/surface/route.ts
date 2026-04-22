import { NextResponse } from "next/server";
import { readSurface } from "@/lib/server/read-surface";
import { resolveMode } from "@/lib/server/mode";
import { fixtureSurface } from "@/lib/fixtures/reasoning-surface";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET() {
  const mode = resolveMode();

  if (mode === "fixtures") {
    return NextResponse.json({
      surface: fixtureSurface,
      age_minutes: 0,
      mode,
      source: { kind: "fixtures" },
      warnings: [],
    });
  }

  try {
    const result = await readSurface();
    return NextResponse.json({
      surface: result.surface,
      age_minutes: result.age_minutes,
      mode,
      source: { kind: "live", ...result.source },
      warnings: result.warnings,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "unknown";
    return NextResponse.json(
      {
        surface: null,
        age_minutes: null,
        mode,
        source: { kind: "live" },
        warnings: [`fatal read error: ${message}`],
      },
      { status: 200 },
    );
  }
}
