# 🛠️ Operational Vessel (Run Context)

## 📡 Sensory Input (Machine Metadata)
- OS: `{{OS_VERSION}}` (`{{OS_BUILD}}`)
- CPU: `{{CPU}}`
- Memory: `{{MEM_GB}} GB`
- Architecture: `{{ARCH}}`
- Shell: `{{SHELL}}`

## 🗡️ Tooling Manifest
- Claude Code: `{{CLAUDE_VERSION}}`
- Cursor: `{{CURSOR_VERSION}}`
- Git: `{{GIT_VERSION}}`

## ⛓️ Execution Constraints (Python Runtime)
- `cognitive-os` local Python work must run in Conda `base`.
- Expected Conda root: `{{CONDA_ROOT}}`
- **Constraint**: Homebrew Python is not a supported runtime.

## Practical Local Limits
- This machine is well suited for editing, tests, small automation, and light inference.
- Avoid assuming heavy local model inference, long training runs, or large data pipelines are practical.
- Prefer remote GPUs or hosted APIs for heavy workloads.

## External Services And APIs
- Fill in services used by this project.

## Rate Limits And Policies
- Fill in API limits, quotas, budgets, and retry rules here.

## Local Vs Remote Execution
- Run local editing, tests, documentation, and light automation here.
- Push heavy experiments, training, and GPU-heavy loops to remote infrastructure.

## Project-Specific Notes
- Add repo-specific environment constraints here.
