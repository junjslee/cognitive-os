# Operator Profile

- Primary machine: macOS 15.7.3, Apple M2, 8 GB unified memory, arm64, zsh.
- Tool preference:
  - Claude Code for orchestration
  - Cursor for editing and review
  - Codex supported via repo policy and synced skills where useful

## Execution Profiles

### `local_mac_base`
- Hardware: Apple M2, 8 GB unified memory, arm64, MPS available
- Valid use: orchestration, editing, tests, small automation, smoke tests, light local inference, query exploration
- Not valid for: final production model inference, heavy training runs, large data pipelines, long autonomous compute loops
- Default profile for all local work unless a remote profile is explicitly chosen

### `remote_gpu`
- Preferred profile for production model-backed runs requiring GPU
- When used, record: backend, model id, device, runtime, artifact outputs, quota constraints
- Not yet assigned to a specific host — document when a remote environment is selected

### `hosted_inference`
- Fallback when remote GPU is not available
- Before using, record: provider, model id, cost assumptions, rate limits, retry policy
- Treat as non-local production — not interchangeable with `local_mac_base`
- Cost acknowledgment required before any paid run (see workflow_policy.md)

## Python Runtime
- All local Python-backed `agent-os` work runs in Conda `base`.
- Expected Conda root: `/Users/junlee/miniconda3`
- Homebrew Python is not the supported runtime for `agent-os`.
- Non-Python tooling (Claude Code, Cursor, Git, `jq`) stays outside Conda.
