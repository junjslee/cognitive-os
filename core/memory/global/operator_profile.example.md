# Operator Profile

<!-- Fill in your machine and tool preferences. -->

- Primary machine: <!-- e.g. macOS 15.x, Apple M2, 16 GB unified memory, arm64, zsh -->
- This machine is suited for coding, tests, small automation, and light local inference.
- Heavy LLM runs, large training, or long autonomous compute loops should default to remote infrastructure.
- Tool preference:
  - Claude Code for orchestration
  - Cursor for editing and review
  - Codex supported via repo policy and synced skills where useful

## Execution Profiles

### `local_mac_base`
- Hardware: <!-- your CPU, RAM, architecture -->
- Valid use: orchestration, editing, tests, smoke tests, light inference, query exploration
- Not valid for: production model inference, heavy training, large data pipelines

### `remote_gpu`
- Preferred profile for production model-backed runs requiring GPU
- When used, record: backend, model id, device, runtime, artifact outputs, quota constraints

### `hosted_inference`
- Fallback when remote GPU is not available
- Before using: record provider, model id, cost assumptions, rate limits, retry policy
- Cost acknowledgment required before any paid run (see workflow_policy.md)

## Python Runtime
- All local Python-backed `agent-os` work runs in Conda `base`.
- Expected Conda root: <!-- e.g. /Users/yourname/miniconda3 -->
- Override with: `export AGENT_OS_CONDA_ROOT=/your/conda/path`
- Homebrew Python is not the supported runtime for `agent-os`.
