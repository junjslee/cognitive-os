#!/usr/bin/env bash
# demo_strict_mode.sh — end-to-end episteme demo.
#
# Three acts tell the whole story in under a minute:
#   Act 1  The Posture          — what a Reasoning Surface IS, lazy surface blocks,
#                                  valid surface passes. The 0.8.1 semantic validator.
#   Act 2  The Kernel Remembers — agent tries to hide `git push` inside a script
#                                  it just wrote. The v0.10 stateful interceptor
#                                  catches it via sha256 + deep-scan on execute.
#   Act 3  The Kernel Learns    — calibration telemetry pairs predictions with
#                                  outcomes; `episteme evolve friction` ranks
#                                  the unknowns the operator keeps under-naming.
#
# Runs hermetically in a tempdir. Sets HOME to the tempdir so the real
# `~/.episteme/state/` and `~/.episteme/telemetry/` are untouched.
#
# Recording:
#   asciinema rec -c ./scripts/demo_strict_mode.sh docs/assets/strict_mode_demo.cast
#   agg docs/assets/strict_mode_demo.cast docs/assets/strict_mode_demo.gif \
#     --cols 100 --rows 34 --font-size 15 --theme monokai

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GUARD="$REPO_ROOT/core/hooks/reasoning_surface_guard.py"
TRACKER="$REPO_ROOT/core/hooks/state_tracker.py"

for required in "$GUARD" "$TRACKER"; do
  if [[ ! -f "$required" ]]; then
    printf 'fatal: required hook not found at %s\n' "$required" >&2
    exit 1
  fi
done

# Colors degrade gracefully if output isn't a tty.
if [[ -t 1 ]]; then
  BOLD=$'\033[1m'; DIM=$'\033[2m'; RED=$'\033[31m'; GREEN=$'\033[32m'
  YELLOW=$'\033[33m'; CYAN=$'\033[36m'; MAGENTA=$'\033[35m'; RESET=$'\033[0m'
else
  BOLD=""; DIM=""; RED=""; GREEN=""; YELLOW=""; CYAN=""; MAGENTA=""; RESET=""
fi

pause()   { sleep "${DEMO_PAUSE:-1.0}"; }
hold()    { sleep "${DEMO_HOLD:-1.8}"; }
narrate() { printf '%s\n' "$1"; pause; }

# Hermetic runtime: fake HOME so the real state / telemetry stays clean.
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT
export HOME="$TMPDIR"
PROJECT="$TMPDIR/proj"
mkdir -p "$PROJECT/.episteme"

NOW_ISO="$(python3 -c 'from datetime import datetime, timezone; print(datetime.now(timezone.utc).isoformat())')"

# -----------------------------------------------------------------------------
# OPEN
# -----------------------------------------------------------------------------

printf '\n'
printf '%s═══════════  episteme  —  a posture, installed  ═══════════%s\n' "$BOLD$CYAN" "$RESET"
printf '%sThree acts: the posture, the kernel remembers, the kernel learns.%s\n\n' "$DIM" "$RESET"
sleep 1

# =============================================================================
# ACT 1 — THE POSTURE
# =============================================================================

printf '%s───  ACT 1  ·  THE POSTURE  ───%s\n' "$BOLD$MAGENTA" "$RESET"
narrate "${DIM}The Reasoning Surface is the posture: Knowns, Unknowns, Assumptions,${RESET}"
narrate "${DIM}and Disconfirmation. Every high-impact op is gated on it.${RESET}"
printf '\n'

# --- Lazy surface ------------------------------------------------------------
narrate "${YELLOW}[1/4]${RESET} Lazy agent writes ${RED}disconfirmation: \"None\"${RESET}"

cat > "$PROJECT/.episteme/reasoning-surface.json" <<JSON
{
  "timestamp": "$NOW_ISO",
  "core_question": "Ship it?",
  "knowns": ["code compiles"],
  "unknowns": ["n/a"],
  "assumptions": [],
  "disconfirmation": "None"
}
JSON

printf '%s' "$DIM"
cat "$PROJECT/.episteme/reasoning-surface.json"
printf '%s\n' "$RESET"
pause

narrate "${YELLOW}[2/4]${RESET} Agent tries ${BOLD}\`git push origin main\`${RESET}"

PAYLOAD_PUSH="$(python3 -c "
import json
print(json.dumps({
  'tool_name': 'Bash',
  'tool_input': {'command': 'git push origin main'},
  'cwd': '$PROJECT',
}))
")"

set +e
RESPONSE="$(printf '%s' "$PAYLOAD_PUSH" | python3 "$GUARD" 2>&1 >/dev/null)"
EXIT_CODE=$?
set -e

if [[ "$EXIT_CODE" -eq 2 ]]; then
  printf '%s✗ BLOCKED (exit 2) — semantic validator caught \"None\"%s\n' "$RED$BOLD" "$RESET"
  printf '%s%s%s\n' "$DIM" "$(printf '%s' "$RESPONSE" | head -3)" "$RESET"
else
  printf '%sFAIL: expected block, got exit %d%s\n' "$RED" "$EXIT_CODE" "$RESET"
  exit 1
fi
hold

# --- Valid surface ----------------------------------------------------------
printf '\n'
narrate "${YELLOW}[3/4]${RESET} Agent rewrites a ${GREEN}valid${RESET} surface"

cat > "$PROJECT/.episteme/reasoning-surface.json" <<JSON
{
  "timestamp": "$NOW_ISO",
  "core_question": "Does the deploy preserve checkout-flow contract semantics?",
  "knowns": ["local tests pass", "staging green for 24h"],
  "unknowns": ["how the canary behaves under live-traffic shape shift"],
  "assumptions": ["feature flag is off by default"],
  "disconfirmation": "p95 latency on checkout exceeds 400ms within 10 minutes of deploy"
}
JSON

printf '%s' "$DIM"
cat "$PROJECT/.episteme/reasoning-surface.json"
printf '%s\n' "$RESET"
pause

narrate "${YELLOW}[4/4]${RESET} Agent retries ${BOLD}\`git push origin main\`${RESET}"

set +e
printf '%s' "$PAYLOAD_PUSH" | python3 "$GUARD" >/dev/null 2>&1
EXIT_CODE=$?
set -e

if [[ "$EXIT_CODE" -eq 0 ]]; then
  printf '%s✓ ALLOWED (exit 0) — concrete disconfirmation, substantive unknowns%s\n' "$GREEN$BOLD" "$RESET"
else
  printf '%sFAIL: expected pass, got exit %d%s\n' "$RED" "$EXIT_CODE" "$RESET"
  exit 1
fi
hold

# =============================================================================
# ACT 2 — THE KERNEL REMEMBERS
# =============================================================================

printf '\n'
printf '%s───  ACT 2  ·  THE KERNEL REMEMBERS  ───%s\n' "$BOLD$MAGENTA" "$RESET"
narrate "${DIM}What if the agent tries to hide the push inside a script it just wrote?${RESET}"
narrate "${DIM}v0.10: a stateful interceptor persists sha256+ts of every write.${RESET}"
printf '\n'

# Reset surface to lazy so the block lands on the stateful label, not validity.
cat > "$PROJECT/.episteme/reasoning-surface.json" <<JSON
{
  "timestamp": "$NOW_ISO",
  "core_question": "Ship it?",
  "knowns": [],
  "unknowns": ["tbd"],
  "assumptions": [],
  "disconfirmation": "None"
}
JSON

STEALTH="$PROJECT/stealth.py"
cat > "$STEALTH" <<'SCRIPT'
import os
os.system("git push origin main")
SCRIPT
chmod +x "$STEALTH"

narrate "${YELLOW}[1/3]${RESET} Agent writes ${MAGENTA}stealth.py${RESET} — \`git push\` wrapped in \`os.system\`, not visible in the call"
printf '%s' "$DIM"
cat "$STEALTH"
printf '%s\n' "$RESET"
pause

# Simulate the PostToolUse Write hook firing — state tracker records sha256+ts.
WRITE_PAYLOAD="$(python3 -c "
import json
print(json.dumps({
  'tool_name': 'Write',
  'tool_input': {'file_path': '$STEALTH'},
  'cwd': '$PROJECT',
}))
")"
printf '%s' "$WRITE_PAYLOAD" | python3 "$TRACKER" >/dev/null 2>&1 || true

narrate "${YELLOW}[2/3]${RESET} State tracker records the write:"
if [[ -f "$HOME/.episteme/state/session_context.json" ]]; then
  printf '%s' "$DIM"
  python3 -m json.tool "$HOME/.episteme/state/session_context.json" | head -12
  printf '%s\n' "$RESET"
else
  printf '%s(no state file — tracker did not record)%s\n' "$RED" "$RESET"
fi
hold

narrate "${YELLOW}[3/3]${RESET} Agent runs ${BOLD}\`python stealth.py\`${RESET} — the .py extension skips the 0.9 script-scanner"

BASH_STEALTH_PAYLOAD="$(python3 -c "
import json
print(json.dumps({
  'tool_name': 'Bash',
  'tool_input': {'command': 'python stealth.py'},
  'cwd': '$PROJECT',
}))
")"

set +e
RESPONSE="$(printf '%s' "$BASH_STEALTH_PAYLOAD" | python3 "$GUARD" 2>&1 >/dev/null)"
EXIT_CODE=$?
set -e

if [[ "$EXIT_CODE" -eq 2 ]]; then
  printf '%s✗ BLOCKED (exit 2) — v0.10 state store caught it: recent Write → deep-scan → match%s\n' "$RED$BOLD" "$RESET"
  printf '%s%s%s\n' "$DIM" "$(printf '%s' "$RESPONSE" | grep -E 'agent-written' | head -1)" "$RESET"
else
  printf '%sFAIL: expected stateful block, got exit %d%s\n' "$RED" "$EXIT_CODE" "$RESET"
  exit 1
fi
hold

# =============================================================================
# ACT 3 — THE KERNEL LEARNS
# =============================================================================

printf '\n'
printf '%s───  ACT 3  ·  THE KERNEL LEARNS  ───%s\n' "$BOLD$MAGENTA" "$RESET"
narrate "${DIM}Every prediction pairs with its outcome. The kernel maps its own calibration debt.${RESET}"
printf '\n'

# Seed a small telemetry fixture so the friction report has something honest to say.
TELEMETRY_DIR="$HOME/.episteme/telemetry"
mkdir -p "$TELEMETRY_DIR"
cat > "$TELEMETRY_DIR/$(date -u +%Y-%m-%d)-audit.jsonl" <<'JSONL'
{"ts":"2026-04-19T10:00:00+00:00","event":"prediction","correlation_id":"tu_001","tool":"Bash","op":"git push","cwd":"/demo","command_executed":"git push origin main","epistemic_prediction":{"core_question":"deploy?","disconfirmation":"remote rejects non-fast-forward","unknowns":["remote diverged since last pull"],"hypothesis":"clean push"},"exit_code":null}
{"ts":"2026-04-19T10:00:05+00:00","event":"outcome","correlation_id":"tu_001","tool":"Bash","cwd":"/demo","command_executed":"git push origin main","exit_code":1,"status":"error"}
{"ts":"2026-04-19T11:00:00+00:00","event":"prediction","correlation_id":"tu_002","tool":"Bash","op":"git push","cwd":"/demo","command_executed":"git push origin feature","epistemic_prediction":{"core_question":"deploy feature?","disconfirmation":"non-fast-forward rejection","unknowns":["remote diverged since last pull"],"hypothesis":"clean push"},"exit_code":null}
{"ts":"2026-04-19T11:00:02+00:00","event":"outcome","correlation_id":"tu_002","tool":"Bash","cwd":"/demo","command_executed":"git push origin feature","exit_code":1,"status":"error"}
{"ts":"2026-04-19T12:00:00+00:00","event":"prediction","correlation_id":"tu_003","tool":"Bash","op":"npm publish","cwd":"/demo","command_executed":"npm publish","epistemic_prediction":{"core_question":"publish package?","disconfirmation":"npm ERR 401 unauthorized","unknowns":["authenticated session for registry"],"hypothesis":"token still valid"},"exit_code":null}
{"ts":"2026-04-19T12:00:03+00:00","event":"outcome","correlation_id":"tu_003","tool":"Bash","cwd":"/demo","command_executed":"npm publish","exit_code":1,"status":"error"}
JSONL

narrate "${YELLOW}[1/1]${RESET} ${BOLD}episteme evolve friction${RESET} — the heuristic analyzer"

# Run the CLI with explicit telemetry-dir so the demo is hermetic.
cd "$REPO_ROOT"
printf '%s' "$DIM"
PYTHONPATH="$REPO_ROOT/src" python3 -m episteme.cli evolve friction \
  --telemetry-dir "$TELEMETRY_DIR" --top 3 2>/dev/null | head -28
printf '%s\n' "$RESET"
hold

# =============================================================================
# CLOSE
# =============================================================================

printf '\n'
printf '%s════════════════════════════════════════════════════════════%s\n' "$BOLD$CYAN" "$RESET"
printf '%sepisteme  —  install a posture, not a policy.%s\n' "$BOLD" "$RESET"
printf '%sPosture gate. Cross-call memory. Calibration loop. No config required.%s\n' "$DIM" "$RESET"
printf '%s════════════════════════════════════════════════════════════%s\n\n' "$BOLD$CYAN" "$RESET"
