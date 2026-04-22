import "server-only";

import { promises as fs } from "node:fs";
import type { ChainEntry } from "@/lib/types/episteme";
import {
  EnvelopeSchema,
  envelopeToChainEntry,
  type Envelope,
} from "./envelope";
import {
  protocolsPath,
  deferredDiscoveriesPath,
  resolveEpistemeHome,
} from "./episteme-home";

export interface ChainReadResult {
  entries: ChainEntry[];
  integrity: "ok" | "broken";
  source: {
    home: string | null;
    home_source: ReturnType<typeof resolveEpistemeHome>["source"];
    protocols_file: string | null;
    deferred_file: string | null;
  };
  warnings: string[];
}

/**
 * Read both hash-chained streams from $EPISTEME_HOME/framework/, union them,
 * and order newest-first by ts. Integrity is verified per-stream (the chains
 * are independent by kernel design; a break in one does not halt the other).
 */
export async function readChain(limit = 50): Promise<ChainReadResult> {
  const { path: home, source: homeSource, error } = resolveEpistemeHome();
  const warnings: string[] = [];
  if (error) warnings.push(error);

  const protoFile = protocolsPath();
  const deferFile = deferredDiscoveriesPath();

  const protoResult = await readStream(protoFile, "protocols", warnings);
  const deferResult = await readStream(deferFile, "deferred_discoveries", warnings);

  const integrity: ChainReadResult["integrity"] =
    protoResult.integrity === "broken" || deferResult.integrity === "broken"
      ? "broken"
      : "ok";

  // Synthesize a stable cross-stream seq by ts descending, then cap.
  const combined = [...protoResult.entries, ...deferResult.entries]
    .sort((a, b) => (b.ts > a.ts ? 1 : b.ts < a.ts ? -1 : 0))
    .slice(0, Math.max(1, Math.min(limit, 500)));

  // Re-number combined seq for display; head is seq 0.
  const renumbered = combined.map((e, i) => ({ ...e, seq: i }));

  return {
    entries: renumbered,
    integrity,
    source: {
      home,
      home_source: homeSource,
      protocols_file: protoFile,
      deferred_file: deferFile,
    },
    warnings,
  };
}

interface StreamReadResult {
  entries: ChainEntry[];
  integrity: "ok" | "broken";
}

async function readStream(
  file: string | null,
  stream: "protocols" | "deferred_discoveries",
  warnings: string[],
): Promise<StreamReadResult> {
  if (!file) return { entries: [], integrity: "ok" };

  const text = await safeRead(file, warnings);
  if (text === null) return { entries: [], integrity: "ok" };

  const envelopes: Envelope[] = [];
  const lines = text.split("\n").filter((ln) => ln.trim().length > 0);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]!;
    let parsedJson: unknown;
    try {
      parsedJson = JSON.parse(line);
    } catch {
      warnings.push(`${stream}:line ${i + 1}: invalid JSON; skipped`);
      continue;
    }
    const result = EnvelopeSchema.safeParse(parsedJson);
    if (!result.success) {
      warnings.push(`${stream}:line ${i + 1}: envelope shape mismatch; skipped`);
      continue;
    }
    envelopes.push(result.data);
  }

  // Per-stream tamper-evidence. Break on first prev_hash mismatch.
  let integrity: "ok" | "broken" = "ok";
  let expectedPrev = "sha256:GENESIS";
  const entries: ChainEntry[] = [];
  for (let i = 0; i < envelopes.length; i++) {
    const env = envelopes[i]!;
    const broken = env.prev_hash !== expectedPrev;
    const entry = envelopeToChainEntry(env, stream, i);
    if (broken) {
      entry.tamper_suspected = true;
      integrity = "broken";
      warnings.push(
        `${stream}:line ${i + 1}: prev_hash mismatch — chain broken from here`,
      );
    }
    entries.push(entry);
    expectedPrev = env.entry_hash;
  }

  return { entries, integrity };
}

async function safeRead(
  file: string,
  warnings: string[],
): Promise<string | null> {
  try {
    return await fs.readFile(file, "utf-8");
  } catch (err) {
    const code = (err as NodeJS.ErrnoException).code;
    if (code === "ENOENT") return null; // expected on fresh install
    if (code === "EACCES") {
      warnings.push(`${file}: permission denied`);
      return null;
    }
    warnings.push(`${file}: read error (${code ?? "unknown"})`);
    return null;
  }
}
