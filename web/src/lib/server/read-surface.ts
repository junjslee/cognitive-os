import "server-only";

import { promises as fs } from "node:fs";
import type { ReasoningSurface } from "@/lib/types/episteme";
import { toReasoningSurface } from "./envelope";
import { resolveEpistemeProject, surfacePath } from "./episteme-project";

export interface SurfaceReadResult {
  surface: ReasoningSurface | null;
  age_minutes: number | null;
  source: {
    project: string;
    project_source: ReturnType<typeof resolveEpistemeProject>["source"];
    surface_file: string;
  };
  warnings: string[];
}

export async function readSurface(): Promise<SurfaceReadResult> {
  const project = resolveEpistemeProject();
  const file = surfacePath();
  const warnings: string[] = [];
  if (project.error) warnings.push(project.error);

  let text: string;
  try {
    text = await fs.readFile(file, "utf-8");
  } catch (err) {
    const code = (err as NodeJS.ErrnoException).code;
    if (code !== "ENOENT") {
      warnings.push(`${file}: ${code ?? "read error"}`);
    }
    return {
      surface: null,
      age_minutes: null,
      source: {
        project: project.path,
        project_source: project.source,
        surface_file: file,
      },
      warnings,
    };
  }

  let raw: unknown;
  try {
    raw = JSON.parse(text);
  } catch {
    warnings.push(`${file}: invalid JSON`);
    return {
      surface: null,
      age_minutes: null,
      source: {
        project: project.path,
        project_source: project.source,
        surface_file: file,
      },
      warnings,
    };
  }

  const surface = toReasoningSurface(raw);
  if (!surface) {
    warnings.push(`${file}: reasoning-surface shape invalid`);
    return {
      surface: null,
      age_minutes: null,
      source: {
        project: project.path,
        project_source: project.source,
        surface_file: file,
      },
      warnings,
    };
  }

  let age: number | null = null;
  const ts = Date.parse(surface.timestamp);
  if (!Number.isNaN(ts)) {
    age = Math.max(0, Math.round((Date.now() - ts) / 60_000));
  }

  return {
    surface,
    age_minutes: age,
    source: {
      project: project.path,
      project_source: project.source,
      surface_file: file,
    },
    warnings,
  };
}
