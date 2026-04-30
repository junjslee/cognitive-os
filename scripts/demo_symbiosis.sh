#!/usr/bin/env bash
# demo_symbiosis.sh — the bidirectional loop demo
#
# Run hermetically in a tempdir. Narrates the six acts of demos/04_symbiosis/:
#   1. Underspecified prompt
#   2. Reasoning Surface forces Unknowns
#   3. Advisory surfaces the premise back to the user
#   4. User refines
#   5. Framework synthesizes a protocol
#   6. Active guidance fires on the next matching call
#
# All kernel output is simulated for cinematic pacing — the schema, advisory
# format, and protocol envelope match the real CP7 / CP9 shapes shipped in v1.0
# RC. No real kernel state is mutated. Pair with asciinema rec to produce the
# .cast asset shipped at docs/assets/demo_symbiosis.cast.

set -euo pipefail

# ── pacing ──────────────────────────────────────────────────────────────────
PACE_FAST=0.6
PACE_SLOW=1.4
PACE_BEAT=2.2

# ── colors (terminal-safe; no-op if NO_COLOR set) ───────────────────────────
if [[ -t 1 && -z "${NO_COLOR:-}" ]]; then
  C_DIM=$'\033[2m'
  C_BONE=$'\033[97m'
  C_CHAIN=$'\033[36m'
  C_DOXA=$'\033[31m'
  C_EPI=$'\033[32m'
  C_USER=$'\033[33m'
  C_OFF=$'\033[0m'
else
  C_DIM='' C_BONE='' C_CHAIN='' C_DOXA='' C_EPI='' C_USER='' C_OFF=''
fi

bar() { printf '%s────────────────────────────────────────────────────────────────────────────────%s\n' "$C_DIM" "$C_OFF"; }
title() { printf '%s%s%s\n' "$C_BONE" "$1" "$C_OFF"; }
prompt_user() { printf '%s$ %s%s\n' "$C_DIM" "$C_USER$1$C_OFF" "$C_OFF"; }
narration() { printf '%s%s%s\n' "$C_DIM" "$1" "$C_OFF"; }
agent() { printf '%s%s%s\n' "$C_CHAIN" "$1" "$C_OFF"; }
doxa() { printf '%s%s%s\n' "$C_DOXA" "$1" "$C_OFF"; }
episteme() { printf '%s%s%s\n' "$C_EPI" "$1" "$C_OFF"; }

# ── Setup ───────────────────────────────────────────────────────────────────
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"

clear
bar
title "  episteme · Demo 04 — Symbiosis"
title "  agent and human debug each other's intent · ~90 seconds"
bar
sleep "$PACE_BEAT"
echo

# ── Act 1 — Underspecified prompt ──────────────────────────────────────────
bar
title "  Act 1 — The underspecified prompt"
bar
echo
narration "  20 minutes into a PagerDuty incident. The user types:"
sleep "$PACE_FAST"
echo
prompt_user "the /api/orders endpoint is slow under load. add a Redis cache to fix it."
sleep "$PACE_BEAT"
echo
narration "  The prompt names a remediation before naming a measurement."
narration "  The premise — \"the bottleneck is cache-shaped\" — is buried inside."
narration "  A fluent agent would accept the framing and write Redis code."
sleep "$PACE_BEAT"
echo

# ── Act 2 — Reasoning Surface forces Unknowns ─────────────────────────────
bar
title "  Act 2 — The Reasoning Surface forces Unknowns"
bar
echo
narration "  Before any high-impact tool runs, the file-system hook"
narration "  demands a Reasoning Surface. The agent must commit to:"
sleep "$PACE_FAST"
echo
agent "  {"
agent "    \"core_question\": \"Is the p95 regression bottlenecked on a"
agent "                       cache-shaped read pattern, or on a non-cache-"
agent "                       shaped pattern (N+1, contention, GC) where"
agent "                       Redis would mask the symptom?\","
agent "    \"unknowns\": ["
agent "      \"Whether the query plan shows a single SELECT with N row"
agent "       fetches (cache-amenable) or N+1 individual SELECTs (cache"
agent "       would mask, not fix). The query plan has not been pulled.\""
agent "    ],"
agent "    \"assumptions\": ["
agent "      { \"claim\": \"The user's framing implicitly assumes the"
agent "                 bottleneck is cache-shaped. This is the load-"
agent "                 bearing premise of the request.\" }"
agent "    ],"
agent "    \"disconfirmation\": \"p95 latency unchanged or worse after"
agent "                         the Redis read-through cache deploys to"
agent "                         staging for 24 hours under load.\""
agent "  }"
sleep "$PACE_BEAT"
echo
narration "  The premise is now on disk. Falsifiable. Visible to both parties."
sleep "$PACE_BEAT"
echo

# ── Act 3 — Advisory surfaces the premise back to the user ────────────────
bar
title "  Act 3 — Advisory surfaces the premise to the user"
bar
echo
episteme "  [episteme] Reasoning Surface accepted"
episteme "  ─────────────────────────────────────"
episteme ""
episteme "    Hidden premise detected and named explicitly:"
episteme ""
episteme "      \"The bottleneck is cache-shaped\""
episteme "        ↳ stated only as a solution shape (\"add a Redis cache\")"
episteme "        ↳ not yet verified against the query plan or trace"
episteme ""
episteme "    This plan pre-commits to a falsifiable disconfirmation:"
episteme "      \"p95 unchanged after 24h staging soak\""
episteme ""
episteme "    The advisory above is what the operator's request would have"
episteme "    looked like if they had named their assumption first."
sleep "$PACE_BEAT"
echo

# ── Act 4 — User refines ──────────────────────────────────────────────────
bar
title "  Act 4 — The human refines"
bar
echo
narration "  The user reads the advisory. The framing they did not realize"
narration "  they had imported becomes visible. A short pause."
sleep "$PACE_SLOW"
echo
narration "  The user types again:"
sleep "$PACE_FAST"
echo
prompt_user "audit /api/orders — find where p95 actually goes. don't add anything until we know."
sleep "$PACE_BEAT"
echo
narration "  The agent did not coach the user. The agent declared its own"
narration "  Unknowns. The Unknowns surfaced the user's hidden assumption."
narration "  The user changed their own prompt."
sleep "$PACE_BEAT"
echo

# ── Act 5 — Protocol synthesized ──────────────────────────────────────────
bar
title "  Act 5 — Framework synthesizes a context-fit protocol"
bar
echo
narration "  Axiomatic Judgment fires on the conflict between"
narration "  Source A (\"add a cache\") and Source B (the disconfirmation"
narration "  requirement). The resolved rule is hash-chained:"
sleep "$PACE_FAST"
echo
episteme "  ~/.episteme/framework/protocols.jsonl  (cp7-chained-v1)"
episteme "  ─────────────────────────────────────────────────────"
episteme "  context_signature:"
episteme "    blueprint:        axiomatic_judgment"
episteme "    op_class:         endpoint-perf-regression"
episteme "    constraint_head:  add-cache"
episteme ""
episteme "  selected_rule:"
episteme "    \"In endpoint-perf-regression context, when the operator's"
episteme "     prompt names a remediation before naming a measurement,"
episteme "     surface the cache-shape-vs-query-shape diagnosis as a"
episteme "     falsifiable Unknown BEFORE recommending the proposed"
episteme "     remediation.\""
episteme ""
episteme "  this_hash: a1f4c8e2b7d35…"
sleep "$PACE_BEAT"
echo

# ── Act 6 — Active guidance fires on next matching call ──────────────────
bar
title "  Act 6 — Active guidance fires on the next matching call"
bar
echo
narration "  A week later. Different endpoint. Same shape."
sleep "$PACE_FAST"
echo
prompt_user "add caching to /api/users — it's slow."
sleep "$PACE_FAST"
echo
episteme "  [episteme guide] active-guidance fired BEFORE agent drafted a surface"
episteme "  ────────────────────────────────────────────────────────────────────"
episteme ""
episteme "    Past pattern in this project (synthesized last week):"
episteme ""
episteme "      context: endpoint-perf-regression + cache-recommended-prematurely"
episteme "      rule:    when remediation precedes measurement,"
episteme "               surface the disconfirmation requirement first"
episteme ""
episteme "    Last firing: /api/orders → diagnosis revealed N+1 ORM query."
episteme "                 Cache would have masked the symptom under low load,"
episteme "                 amplified the failure under high."
episteme ""
episteme "    Suggest: pull the query plan FIRST."
sleep "$PACE_BEAT"
echo
narration "  The user, having already been through this loop once, types:"
sleep "$PACE_FAST"
echo
prompt_user "audit /api/users — pull the query plan and the trace. don't write anything yet."
sleep "$PACE_BEAT"
echo

# ── Closing ────────────────────────────────────────────────────────────────
bar
title "  Symbiosis"
bar
echo
narration "  No one had to remember the protocol. The framework remembered."
narration "  The user did not have to coach the agent. The framework coached"
narration "  the user. The agent did not draft an under-grounded plan."
narration "  The framework surfaced the protocol that made the under-grounded"
narration "  plan unavailable in the first place."
sleep "$PACE_BEAT"
echo
narration "  Both parties' thinking changed."
narration "  The lesson is durable, tamper-evident, context-fit."
narration "  The next slow endpoint starts at the right question."
sleep "$PACE_BEAT"
echo
bar
title "  episteme · 생각의 틀, posture over prompt"
bar
echo
sleep "$PACE_FAST"
