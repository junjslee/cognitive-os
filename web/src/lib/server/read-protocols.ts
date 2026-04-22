import "server-only";

import { promises as fs } from "node:fs";
import type { Protocol } from "@/lib/types/episteme";
import { EnvelopeSchema, envelopeToProtocol } from "./envelope";
import { protocolsPath, resolveEpistemeHome } from "./episteme-home";

export interface ProtocolsReadResult {
  protocols: Protocol[];
  source: {
    home: string | null;
    home_source: ReturnType<typeof resolveEpistemeHome>["source"];
    protocols_file: string | null;
  };
  warnings: string[];
}

export async function readProtocols(): Promise<ProtocolsReadResult> {
  const { path: home, source: homeSource, error } = resolveEpistemeHome();
  const warnings: string[] = [];
  if (error) warnings.push(error);
  const file = protocolsPath();

  if (!file) {
    return {
      protocols: [],
      source: { home, home_source: homeSource, protocols_file: null },
      warnings,
    };
  }

  let text: string;
  try {
    text = await fs.readFile(file, "utf-8");
  } catch (err) {
    const code = (err as NodeJS.ErrnoException).code;
    if (code !== "ENOENT") {
      warnings.push(`${file}: ${code ?? "read error"}`);
    }
    return {
      protocols: [],
      source: { home, home_source: homeSource, protocols_file: file },
      warnings,
    };
  }

  const protocols: Protocol[] = [];
  const lines = text.split("\n").filter((ln) => ln.trim().length > 0);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]!;
    let parsedJson: unknown;
    try {
      parsedJson = JSON.parse(line);
    } catch {
      warnings.push(`protocols:line ${i + 1}: invalid JSON; skipped`);
      continue;
    }
    const envelope = EnvelopeSchema.safeParse(parsedJson);
    if (!envelope.success) {
      warnings.push(`protocols:line ${i + 1}: envelope mismatch; skipped`);
      continue;
    }
    if (envelope.data.payload.type !== "protocol") continue;
    const p = envelopeToProtocol(envelope.data);
    if (!p) {
      warnings.push(`protocols:line ${i + 1}: payload unprojectable; skipped`);
      continue;
    }
    protocols.push(p);
  }

  return {
    protocols,
    source: { home, home_source: homeSource, protocols_file: file },
    warnings,
  };
}
