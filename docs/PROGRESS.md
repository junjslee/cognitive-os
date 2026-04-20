# Progress

Running log of completed work. Most recent first.

---

## 0.8.1 — 2026-04-20 — Strict-by-default enforcement + semantic validator + bypass-resistant matching

### Hook behavior changes (`core/hooks/reasoning_surface_guard.py`)
- **Default inverted**: missing / stale / incomplete / lazy Reasoning Surface now exits 2 and blocks the tool call. Previously advisory; hard-block required `.episteme/strict-surface`.
- **Opt-out mechanism**: per-project advisory mode via `.episteme/advisory-surface` marker. Legacy `.episteme/strict-surface` is now a no-op (strict is default).
- **Semantic validator added** to `_surface_missing_fields`:
  - Min lengths: `MIN_DISCONFIRMATION_LEN = 15`, `MIN_UNKNOWN_LEN = 15`
  - Lazy-token blocklist: `none`, `null`, `nil`, `nothing`, `undefined`, `n/a`, `na`, `not applicable`, `tbd`, `todo`, `unknown`, `idk`, `해당 없음`, `해당없음`, `없음`, `모름`, `해당 사항 없음`, `-`, `--`, `---`, `—`, `...`, `?`, `pending`, `later`, `maybe`
  - Case-insensitive + whitespace-collapsed + trailing-punctuation-trimmed matching
- **Bypass resistance** via `_normalize_command`: `[,'"\[\]\(\)\{\}]` → space before regex match. Caught in tests: `subprocess.run(['git','push'])`, `os.system('git push')`, `sh -c 'npm publish'`.
- **Block message upgraded**: stderr leads with `"Execution blocked by Episteme Strict Mode. Missing or invalid Reasoning Surface."` + concrete validator reasons + advisory-mode opt-out pointer.
- **Audit entry** `mode` field replaces the old `strict` bool.

### CLI (`src/episteme/cli.py`)
- `_inject` rewritten: strict (default) creates no marker and removes any pre-existing `advisory-surface`; `--no-strict` writes `.episteme/advisory-surface` explicitly.
- Template unknowns placeholder updated to reflect the ≥ 15 char rule.
- Post-inject hint text lists lazy-token rejection explicitly.

### Tests (`tests/test_reasoning_surface_guard.py`)
- Rewritten from 9 advisory-flavored cases → 17 cases covering:
  - Strict-by-default on every failure mode (missing / stale / incomplete / lockfile)
  - Advisory-marker downgrade path
  - Legacy `strict-surface` marker no-op behavior
  - Lazy-token rejection: 8 subtest values (`none`, `N/A`, `TBD`, `해당 없음`, `없음`, `null`, `-`, `nothing`)
  - Short-string rejection (disconfirmation and unknowns)
  - Bypass vectors: subprocess list form, `os.system`, `sh -c` wrapping

### Docs
- `kernel/CHANGELOG.md` — 0.8.1 entry added
- `kernel/HOOKS_MAP.md` — enforcement row + state-file description rewritten to match new default
- `README.md` — lede paragraph rewritten: no more "advisory by default" hedge; now explicitly states block-by-default, the validator contract, and the advisory opt-out pointer
- `docs/PLAN.md`, `docs/NEXT_STEPS.md` — strict-by-default and validator items moved to Closed

### Verification
- `PYTHONPATH=. pytest tests/ -v` → **68 passed**, 8 subtests passed (17 in the guard suite, 51 pre-existing elsewhere — zero regressions)
- Hook tested end-to-end via the suite: block exit code 2, advisory-mode exit 0, normalized bypass shapes caught, lazy tokens rejected

### Architectural gaps surfaced (not fixed, logged to `NEXT_STEPS.md`)
- **Shell script files calling high-impact ops** are not caught (e.g., `./deploy.sh` that internally runs `git push`). Intercepting requires script-content reading — out of scope for this patch.
- **Write-then-execute patterns** (write a script to disk, then run it) are not caught without a stateful hook. Requires cross-call state, which is out of scope.
- **Bash variable indirection** (`CMD="git push" && $CMD`) is not caught; normalization handles quote/bracket separators but not variable substitution.

---

## 0.8.0 — 2026-04-19 — Core migration: cognitive-os → episteme

### Version alignment (0.8.0 follow-on)
- `pyproject.toml` version: `0.2.0` → `0.8.0` (was stale across 0.6.0/0.7.0/0.8.0 cycles)
- `.claude-plugin/plugin.json` version: `0.6.0` → `0.8.0`
- `.claude-plugin/marketplace.json` plugin version: `0.6.0` → `0.8.0`
- `pip install -e .` re-run so the registered `episteme` console script reports 0.8.0
- `git tag v0.8.0 && git push --tags` — migration tagged and pushed

### Python package
- `git mv src/cognitive_os → src/episteme` (history preserved)
- All internal imports updated: `from cognitive_os` → `from episteme`
- `pyproject.toml`: `name`, `description`, `[project.scripts]` entry (`episteme = "episteme.cli:main"`)
- Env vars: `COGNITIVE_OS_CONDA_ROOT` → `EPISTEME_CONDA_ROOT` (+ `_LEGACY` variant)

### Plugin & tooling
- `.claude-plugin/marketplace.json` + `plugin.json` display names updated; `source.url` and `homepage` retained (GitHub repo path unchanged)
- `.github/` issue templates, PR template, CI workflow updated
- `core/adapters/*.json`, `core/harnesses/*.json` string refs updated
- `core/hooks/*.py` log/message strings updated
- `kernel/MANIFEST.sha256` regenerated against new content
- `.git/hooks/pre-commit` updated (imports `episteme.cli`, reads `EPISTEME_CONDA_ROOT` with `COGNITIVE_OS_CONDA_ROOT` fallback)

### Documentation
- README, AGENTS, INSTALL, all `docs/*` and `kernel/*` narrative + CLI examples updated
- Runtime directory convention: `.cognitive-os/` → `.episteme/`
- Schema identifier: `cognitive-os/reasoning-surface@1` → `episteme/reasoning-surface@1`

### Templates & labs
- Only CLI command literals updated; epistemic kernel rules, schemas, and structural logic untouched

### Verification
- `PYTHONPATH=src:. pytest -q` → 60 passed
- `py_compile` across `src/episteme/` and `core/hooks/` → clean
- Pre-commit validate hook → all kernel, agents, skills pass
- `pip install -e .` metadata resolves: `episteme = "episteme.cli:main"`

### Environment completion (completed in-session)
- GitHub repo renamed via `gh repo rename` → `github.com/junjslee/episteme` (old URL 301-redirects)
- Local `origin` remote updated; all in-repo URLs now point at the new canonical URL
- Physical repo directory renamed `/Users/junlee/cognitive-os` → `/Users/junlee/episteme`
- Pip: `pip uninstall cognitive-os` → `pip install -e .` (registers `episteme` console script)
- `~/.claude/settings.json` hook command paths rewritten to `/Users/junlee/episteme/core/hooks/*`
- `~/.zshrc` aliases and hint function renamed (`ainit`, `awt`, `cci`, `aci`, `adoctor`, `aos`)
- `episteme sync` regenerated `~/.claude/CLAUDE.md` with new `@/Users/junlee/episteme/...` includes

### Dynamic Python runtime (0.8.0 follow-on)
- `CONDA_ROOT` hardcoded to `~/miniconda3` → `PYTHON_PREFIX` derived from `sys.prefix`
- New env vars: `EPISTEME_PYTHON_PREFIX`, `EPISTEME_PYTHON`, `EPISTEME_REQUIRE_CONDA`
- Legacy `EPISTEME_CONDA_ROOT` / `COGNITIVE_OS_CONDA_ROOT` still honored as fallbacks
- `episteme doctor` skips conda checks on non-conda runtimes unless `EPISTEME_REQUIRE_CONDA=1`

### Temporary compatibility shim
- Symlink `/Users/junlee/cognitive-os → /Users/junlee/episteme` created to keep the current shell session's cwd valid. Remove with `rm /Users/junlee/cognitive-os` after restarting any shells/editors that had the old path cached.

---

## 0.7.0 — 2026-04-19

### Real enforcement pass
- `core/hooks/reasoning_surface_guard.py` — added `_write_audit()` writing structured entries to `~/.episteme/audit.jsonl` on every check (passed / advisory / blocked)
- `src/episteme/cli.py` — added `_inject()`, `_surface_log()`, parser registration, and dispatch for `inject` and `log` commands
- `.claude-plugin/plugin.json` — version bumped to 0.6.0
- `kernel/CHANGELOG.md` — 0.7.0 entry added
- Verified: `episteme inject /tmp` creates strict-surface + template; hook fires real exit-2 block; `episteme log` shows timestamped audit entries

## 0.6.0 — 2026-04-19

### Gap closure (second pass)
- `kernel/CONSTITUTION.md` — added DbC contract paragraph to Principle I; added feedforward control paragraph to Principle IV; added feedforward + DbC bullets to "What this generates"
- `kernel/FAILURE_MODES.md` — added feedforward framing to intro; renamed review checklist to "pre-execution checklist" to make the feedforward intent explicit
- `.github/ISSUE_TEMPLATE/bug.yml` — added "Kernel alignment" field mapping bugs to failure modes and kernel layers
- `.github/PULL_REQUEST_TEMPLATE.md` — added "Kernel impact" checklist block
- `README.md` — replaced TODO comment with ASCII control-plane architecture diagram
- `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/NEXT_STEPS.md` — created (ops docs were absent; hook advisory fired on every kernel edit)

### Initial pass
- `.claude-plugin/marketplace.json` — fixed `source: "."` → `"https://github.com/junjslee/episteme"` (schema fix; unverified against live validator)
- `src/episteme/viewer/index.html` — removed (deprecated UI artifact)
- `.github/ISSUE_TEMPLATE/feature.yml` — added "Epistemic alignment" field; improved acceptance criteria template
- `README.md` — added governance/control-plane opening paragraph; feedforward + DbC + OPA framing in "Why this architecture"; "Zero-trust execution" section with OWASP counter-mapping table; "Human prompt debugging" section; interoperability statement; ASCII control-plane diagram
- `kernel/KERNEL_LIMITS.md` — added Cynefin problem-domain classification table
- `kernel/CHANGELOG.md` — added [0.6.0] entry
