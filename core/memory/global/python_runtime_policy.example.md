# Python Runtime Policy

- All local Python-backed `agent-os` commands must run in Conda `base`.
- The expected Conda root is set via `AGENT_OS_CONDA_ROOT` (default: `~/miniconda3`).
- Homebrew Python is not the supported runtime for `agent-os`.
- Non-Python tooling such as Claude Code, Cursor, Git, and `jq` stays outside Conda.

<!-- Copy this file to python_runtime_policy.md and adjust the Conda path if needed. -->
