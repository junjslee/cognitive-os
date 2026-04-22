import "server-only";

import { z } from "zod";
import type { ChainEntry, Protocol, ReasoningSurface } from "@/lib/types/episteme";

/**
 * Zod schemas at the JSONL boundary. Mirror kernel's _chain.py envelope and
 * _framework.py payload dispatch. Line-level parse failures surface via
 * result.success === false and are skipped with a warning upstream.
 */

const hashString = z.string().regex(/^sha256:/);

/**
 * CP7 envelope — identical shape across protocols.jsonl, deferred_discoveries.jsonl,
 * and any other hash-chained stream. schema_version bumps only on envelope changes.
 */
export const EnvelopeSchema = z.looseObject({
  schema_version: z.string(),
  ts: z.string(),
  prev_hash: hashString,
  payload: z.looseObject({ type: z.string() }),
  entry_hash: hashString,
});

export type Envelope = z.infer<typeof EnvelopeSchema>;

/**
 * Known payload discriminators the kernel writes today.
 * - "protocol" via _framework.write_protocol
 * - "deferred_discovery" via _framework.write_deferred_discovery
 * - "chain_reset" via _chain.reset_stream (genesis only)
 */
export const PROTOCOL_TYPE = "protocol";
export const DEFERRED_DISCOVERY_TYPE = "deferred_discovery";
export const CHAIN_RESET_TYPE = "chain_reset";

// ---------------------------------------------------------------------------
// Kernel payload schemas — permissive, only what we actually project to UI
// ---------------------------------------------------------------------------

const ProtocolPayloadSchema = z.looseObject({
  type: z.literal(PROTOCOL_TYPE),
  blueprint: z.string().optional(),
  correlation_id: z.string().optional(),
  synthesized_protocol: z.string().optional(),
  protocol_id: z.string().optional(),
  protocol_name: z.string().optional(),
  summary: z.string().optional(),
  conflict_cause: z.string().optional(),
  observed_signal: z.string().optional(),
  inferred_cause: z.string().optional(),
  decision: z.string().optional(),
  triggers: z.array(z.string()).optional(),
  invocations: z.number().optional(),
  confidence: z.number().optional(),
  written_at: z.string().optional(),
  context_signature: z.record(z.string(), z.unknown()).optional(),
  legacy_format: z.string().optional(),
});

// ---------------------------------------------------------------------------
// Envelope → UI mappers
// ---------------------------------------------------------------------------

type StreamKey = "protocols" | "deferred_discoveries";

/**
 * Convert one envelope to a UI ChainEntry. Integrity (tamper_suspected) is
 * applied later by the reader after walking the stream; we cannot detect a
 * break from a single entry.
 */
export function envelopeToChainEntry(
  env: Envelope,
  stream: StreamKey,
  seq: number,
): ChainEntry {
  const payload = env.payload;
  const payloadType = payload.type;

  let kind: ChainEntry["kind"] = "protocol_applied";
  let label = String(payload["protocol_name"] ?? payloadType);

  if (env.prev_hash === "sha256:GENESIS" || payloadType === CHAIN_RESET_TYPE) {
    kind = "genesis";
    label =
      payloadType === CHAIN_RESET_TYPE
        ? `chain reset: ${String(payload["reason"] ?? "unspecified")}`
        : `${stream} genesis`;
  } else if (payloadType === PROTOCOL_TYPE) {
    const blueprint = payload["blueprint"];
    const protocolName = payload["protocol_name"] ?? payload["protocol_id"];
    kind =
      typeof blueprint === "string" && blueprint
        ? "protocol_synthesized"
        : "protocol_applied";
    label =
      (typeof protocolName === "string" && protocolName) ||
      (typeof blueprint === "string" && blueprint) ||
      "protocol";
  } else if (payloadType === DEFERRED_DISCOVERY_TYPE) {
    kind = "deferred_discovery";
    const desc = payload["description"];
    label =
      typeof desc === "string" && desc.length > 0
        ? desc.length > 72
          ? desc.slice(0, 72) + "…"
          : desc
        : "deferred discovery";
  }

  const ref =
    (typeof payload["correlation_id"] === "string" && payload["correlation_id"]) ||
    (typeof payload["protocol_id"] === "string" && payload["protocol_id"]) ||
    (typeof payload["decision_id"] === "string" && payload["decision_id"]) ||
    undefined;

  return {
    seq,
    ts: env.ts,
    kind,
    label,
    prev_hash: stripSha(env.prev_hash),
    this_hash: stripSha(env.entry_hash),
    ref,
  };
}

/**
 * Convert a protocol envelope into the UI Protocol shape.
 * Fields missing on disk get defensible defaults rather than undefined
 * so the ProtocolNode component always renders cleanly.
 */
export function envelopeToProtocol(env: Envelope): Protocol | null {
  const parsed = ProtocolPayloadSchema.safeParse(env.payload);
  if (!parsed.success) return null;
  const p = parsed.data;

  const id =
    p.protocol_id ??
    p.correlation_id ??
    `${env.ts}-${env.entry_hash.slice(7, 15)}`;
  const name =
    p.protocol_name ??
    p.blueprint ??
    p.synthesized_protocol?.slice(0, 64) ??
    "unnamed protocol";

  const summary =
    p.summary ??
    p.synthesized_protocol ??
    p.conflict_cause ??
    "No summary on disk.";

  return {
    id,
    name,
    summary,
    because: {
      observed_signal: p.observed_signal ?? p.conflict_cause ?? "",
      inferred_cause: p.inferred_cause ?? "",
      decision: p.decision ?? p.synthesized_protocol ?? "",
    },
    triggers: p.triggers ?? [],
    invocations: p.invocations ?? 0,
    confidence: typeof p.confidence === "number" ? p.confidence : 0.5,
    synthesized_at: p.written_at ?? env.ts,
    last_chain_hash: stripSha(env.entry_hash),
    provenance: p.correlation_id
      ? { decision_id: p.correlation_id }
      : undefined,
  };
}

/** Reasoning-surface JSON lives un-enveloped; validate directly. */
export const ReasoningSurfaceRawSchema = z.looseObject({
  schema: z.string(),
  timestamp: z.string(),
  domain: z
    .enum(["clear", "complicated", "complex", "chaotic", "disorder"])
    .optional(),
  core_question: z.string(),
  hypothesis: z.string().optional(),
  knowns: z.array(z.string()),
  unknowns: z.array(z.string()),
  assumptions: z.array(z.unknown()),
  disconfirmation: z.union([z.string(), z.array(z.string())]),
  flaw_classification: z.string().optional(),
  posture_selected: z.enum(["patch", "refactor", "defer"]).optional(),
  patch_vs_refactor_evaluation: z.string().optional(),
  blast_radius_map: z
    .array(
      z.looseObject({
        surface: z.string(),
        status: z.string(),
        rationale: z.string().optional(),
      }),
    )
    .optional(),
  sync_plan: z
    .array(z.looseObject({ surface: z.string(), action: z.string() }))
    .optional(),
  deferred_discoveries: z
    .array(
      z.looseObject({
        description: z.string(),
        observable: z.string(),
        log_only_rationale: z.string(),
      }),
    )
    .optional(),
});

export function toReasoningSurface(raw: unknown): ReasoningSurface | null {
  const parsed = ReasoningSurfaceRawSchema.safeParse(raw);
  if (!parsed.success) return null;
  const r = parsed.data;
  // Schema field is freeform on disk; the UI type pins it to the versioned literal.
  // We keep the on-disk value but alias through the known shape.
  return {
    ...r,
    schema: "episteme/reasoning-surface@1",
    domain: r.domain ?? "complicated",
    assumptions: r.assumptions.map((a) =>
      typeof a === "string"
        ? a
        : (a as { claim: string; falsification: string }),
    ),
  } as ReasoningSurface;
}

function stripSha(s: string): string {
  return s.startsWith("sha256:") ? s.slice("sha256:".length) : s;
}
