# Post-Soak Migration Plan — Strategic Doc Privatization + Product Protection Strategy

Status: **drafted (executable runbook)** · Drafted 2026-04-25 (Event 58) · Execute window: **AFTER v1.0.0 GA cut** (~2026-04-30 onwards) · Scope: operator-facing migration runbook + product-protection decision matrix.

> **DO NOT EXECUTE DURING SOAK.** This document is drafted during the active v1.0.0-rc1 7-day soak (target close `~2026-04-30 21:23:36Z`). Any execution of the commands below DURING the soak invalidates the soak's claim of stable RC behavior. Operator runs this runbook **after** the v1.0 GA cut completes (Path 2.A in `docs/POST_SOAK_TRIAGE.md` §4) **OR** after the v1.0.1-rc1 cut if Day-7 grading routes to Path 2.B.
>
> **Self-referential note.** This file (`docs/POST_SOAK_MIGRATION_PLAN.md`) appears in the migration list below — when the operator executes Section C, this file moves with the others to the private repo. Until then it lives in the public repo for operator durability (so a local disk failure pre-soak-close doesn't lose the plan).

---

## Why this exists

Earlier this session the operator surfaced a real concern: the public `junjslee/episteme` repo currently contains forward-looking strategic docs — `PLAN.md`, `NEXT_STEPS.md`, `ROADMAP_POST_V1.md`, `DESIGN_V1_1_REASONING_ENGINE.md`, the soak-triage docs — that give competitors a free roadmap. Episteme's own thesis (*reasoning visible on disk*) makes architecture-privatization contradictory; but forward-strategy is operator-business not kernel-identity, and can be privatized without violating the project's core transparency claim.

The agreed split (after rule-shape + tradeoff analysis):

- **Public (project identity, marketing surface, kernel constitutional content):** `README` (all langs), `INSTALL.md`, `AGENTS.md`, `llms.txt`, `LICENSE`, `kernel/**`, `core/**`, `src/**`, `tests/**`, `hooks/**`, `.claude-plugin/**`, `scripts/**`, `web/**`, `demos/**`, `templates/**`, AND any `docs/` file describing what the kernel currently IS or does (`POSTURE`, `NARRATIVE`, `ARCHITECTURE`, `LAYER_MODEL`, `COGNITIVE_SYSTEM_PLAYBOOK`, `DESIGN_V1_0_SEMANTIC_GOVERNANCE`, `MEMORY_CONTRACT`, `EVOLUTION_CONTRACT`, `SUBSTRATE_BRIDGE`, `HOOKS`, `HARNESSES`, `SETUP`, `COMMANDS`, `CUSTOMIZATION`, `SKILLS_AND_PERSONAS`, `DEMOS`, `SYNC_AND_MEMORY`, `ANTHROPIC_MANAGED_AGENTS_BRIDGE`, `OPEN_SOURCE_YOUR_PROFILE`, `CONTRIBUTING`, `DECISION_STORY`, `EPISTEME_ARCHITECTURE`, `PROGRESS` — historical record + trust signal).
- **Private (operator forward-strategy, decay-fast tactical content, not-yet-shipped designs):** `PLAN.md`, `NEXT_STEPS.md`, `ROADMAP_POST_V1.md`, `DESIGN_V1_1_REASONING_ENGINE.md`, `POST_SOAK_TRIAGE.md`, `PREPARED_PATCHES.md`, `DEFERRED_DISCOVERIES_TRIAGE.md`, `DISCRIMINATOR_CALIBRATION.md`, AND this file (`POST_SOAK_MIGRATION_PLAN.md`) once the migration executes.

The mechanism: the private files physically live in a sibling repo at `~/episteme-private/`; the public repo's `docs/` paths become **relative symlinks** pointing into the sibling. Agents read via path (symlinks transparent); git tracks neither the symlink nor the target (gitignored). Strategic content stays operator-private going forward.

---

## Section A · Pre-flight checklist (before running ANY command)

Verify each item before starting Section B. If any fails — **stop and resolve before proceeding**.

```bash
cd ~/episteme

# 1. v1.0 GA cut completed (or v1.0.1-rc1 cut, if routed to Path 2.B)
#    Check: docs/POST_SOAK_TRIAGE.md Phase 4 verdict recorded
#    Check: a v1.0.0 (or v1.0.1-rc1) tag exists
git tag -l | grep -E "v1\.0\.[01]" | sort -V | tail -3

# 2. Master clean and synced to origin
git fetch origin
git status              # must show: "nothing to commit, working tree clean"
[ "$(git rev-parse master)" = "$(git rev-parse origin/master)" ] && echo "synced" || echo "DIVERGED — sync first"

# 3. No active feature branches with uncommitted work
git branch -a           # review; merge or delete stragglers before migration

# 4. Backup the entire public repo (defense in depth)
cd ~
tar -czf ~/episteme-pre-migration-$(date -u +%Y%m%d).tar.gz episteme/
ls -lah ~/episteme-pre-migration-*.tar.gz

# 5. /tmp/archive-backup safety net
[ -d ~/episteme/archive ] && cp -R ~/episteme/archive /tmp/archive-pre-migration

# 6. Path-coupling audit (deferred-discovery from Event 58 surface)
cd ~/episteme
grep -rEn "docs/(PLAN|NEXT_STEPS|ROADMAP_POST_V1|DESIGN_V1_1|POST_SOAK_TRIAGE|PREPARED_PATCHES|DEFERRED_DISCOVERIES_TRIAGE|DISCRIMINATOR_CALIBRATION|POST_SOAK_MIGRATION_PLAN)" tools/ src/ core/hooks/ 2>/dev/null
# If output is non-empty: code paths reference soon-to-be-symlinked files.
# Symlinks WILL resolve transparently for read-only access (Read tool, cat, open).
# But hardcoded write-to-path code may need updating. Audit each hit.
```

If the path-coupling audit (#6) returns hits in `core/hooks/` or `src/episteme/`, **stop and decide per file** whether to: (a) update the code path to take a configurable location, (b) keep the file public despite the strategic-content concern, (c) accept that the symlinked path works for read but not write. Do not skip this step.

---

## Section B · Create the private repo

Operator runs once. Sibling layout — the public repo is at `~/episteme/`, the private repo lands at `~/episteme-private/`.

```bash
cd ~
mkdir episteme-private
cd episteme-private

git init -b master
cat > README.md <<'EOF'
# episteme-private

Strategic forward-planning docs for the public `junjslee/episteme` repo.
Private mirror — accessed by the public repo via relative symlinks at
`~/episteme/docs/<filename>` → `~/episteme-private/<filename>`.

Migrated 2026-XX-XX per `~/episteme/docs/POST_SOAK_MIGRATION_PLAN.md`
(file later moved here by that plan's own execution).
EOF
git add README.md
git commit -m "init: private mirror for episteme strategic docs"
```

Create the private GitHub repo (free tier supports unlimited private repos):

```bash
# Option 1: gh CLI
gh repo create junjslee/episteme-private --private --source=. --remote=origin --push

# Option 2: GitHub web UI — create empty private repo, then:
git remote add origin git@github.com:junjslee/episteme-private.git
git branch -M master
git push -u origin master
```

Verify the private repo is reachable but NOT publicly visible:

```bash
gh repo view junjslee/episteme-private --json visibility    # should print: "PRIVATE"
```

---

## Section C · Migrate the 9 files

Operator runs in `~/episteme/`. Each block is one file — copy, remove from public tracking, symlink, verify. The order is `PROGRESS.md` (the historical record stays public) is **not** in this list — only the 9 strategic files.

The following files migrate together (atomic Event):

1. `docs/PLAN.md`
2. `docs/NEXT_STEPS.md`
3. `docs/ROADMAP_POST_V1.md`
4. `docs/DESIGN_V1_1_REASONING_ENGINE.md`
5. `docs/POST_SOAK_TRIAGE.md`
6. `docs/PREPARED_PATCHES.md`
7. `docs/DEFERRED_DISCOVERIES_TRIAGE.md`
8. `docs/DISCRIMINATOR_CALIBRATION.md`
9. `docs/POST_SOAK_MIGRATION_PLAN.md` (this file — moves with the others)

```bash
cd ~/episteme
git checkout -b event-XX-strategic-docs-privatize origin/master    # use real Event number at time of execution

PRIVATE=~/episteme-private
FILES=(
  docs/PLAN.md
  docs/NEXT_STEPS.md
  docs/ROADMAP_POST_V1.md
  docs/DESIGN_V1_1_REASONING_ENGINE.md
  docs/POST_SOAK_TRIAGE.md
  docs/PREPARED_PATCHES.md
  docs/DEFERRED_DISCOVERIES_TRIAGE.md
  docs/DISCRIMINATOR_CALIBRATION.md
  docs/POST_SOAK_MIGRATION_PLAN.md
)

for f in "${FILES[@]}"; do
  basename=$(basename "$f")

  # 1. Copy real file to private repo
  cp "$f" "$PRIVATE/$basename"

  # 2. Stage removal from public repo (file still in working tree until commit)
  git rm "$f"

  # 3. Replace with relative symlink
  ln -s "../../episteme-private/$basename" "$f"

  # 4. Verify symlink resolves
  cat "$f" > /dev/null && echo "OK: $f resolves to $PRIVATE/$basename" || echo "FAIL: $f"
done
```

Commit the private repo first (so the symlink targets exist):

```bash
cd $PRIVATE
git add -A
git commit -m "migrate: 9 strategic docs from public episteme repo (Event XX)"
git push origin master
cd ~/episteme
```

Update the public repo's `.gitignore` to ignore the symlink paths (so a future `chkpt` hook or `git add -A` doesn't accidentally re-track them):

```bash
cat >> .gitignore <<'EOF'

# ─── Strategic docs migrated to ~/episteme-private/ (Event XX) ───────────────
# These paths are symlinks pointing into the sibling private repo.
# Local agents read them via the symlink; git neither tracks the symlink
# itself nor follows it to the target. See docs/POST_SOAK_MIGRATION_PLAN.md
# (now living in the private repo as part of its own migration).
docs/PLAN.md
docs/NEXT_STEPS.md
docs/ROADMAP_POST_V1.md
docs/DESIGN_V1_1_REASONING_ENGINE.md
docs/POST_SOAK_TRIAGE.md
docs/PREPARED_PATCHES.md
docs/DEFERRED_DISCOVERIES_TRIAGE.md
docs/DISCRIMINATOR_CALIBRATION.md
docs/POST_SOAK_MIGRATION_PLAN.md
EOF
```

Commit the public repo's deletions + gitignore update:

```bash
git add -A
git commit -m "docs(strategy): migrate 9 strategic docs to private mirror (Event XX)"
git push -u origin event-XX-strategic-docs-privatize
gh pr create --title "docs(strategy): privatize forward-planning docs" \
  --body "Moves PLAN/NEXT_STEPS/ROADMAP_POST_V1/DESIGN_V1_1/POST_SOAK_TRIAGE/PREPARED_PATCHES/DEFERRED_DISCOVERIES_TRIAGE/DISCRIMINATOR_CALIBRATION/POST_SOAK_MIGRATION_PLAN to ~/episteme-private/. Public repo's docs/ paths are now symlinks (gitignored). See public history at git log --before=$(date -u +%Y-%m-%d) for archival rationale."
# Operator merges via GitHub UI with --merge strategy (Event-57 protocol Path A)
```

---

## Section D · Update `AGENTS.md` so future agents know about the private mirror

Append a section to `~/episteme/AGENTS.md` (in the same migration commit, OR as a follow-on Event):

```markdown
## Strategic docs live in a sibling private repo

Forward-planning docs were moved to `~/episteme-private/` (private GitHub
mirror) on YYYY-MM-DD per `~/episteme-private/POST_SOAK_MIGRATION_PLAN.md`.
The following paths in this public repo are RELATIVE SYMLINKS, gitignored:

- `docs/PLAN.md`               → `../../episteme-private/PLAN.md`
- `docs/NEXT_STEPS.md`         → `../../episteme-private/NEXT_STEPS.md`
- `docs/ROADMAP_POST_V1.md`    → `../../episteme-private/ROADMAP_POST_V1.md`
- `docs/DESIGN_V1_1_REASONING_ENGINE.md` → `../../episteme-private/DESIGN_V1_1_REASONING_ENGINE.md`
- `docs/POST_SOAK_TRIAGE.md`   → `../../episteme-private/POST_SOAK_TRIAGE.md`
- `docs/PREPARED_PATCHES.md`   → `../../episteme-private/PREPARED_PATCHES.md`
- `docs/DEFERRED_DISCOVERIES_TRIAGE.md` → `../../episteme-private/DEFERRED_DISCOVERIES_TRIAGE.md`
- `docs/DISCRIMINATOR_CALIBRATION.md` → `../../episteme-private/DISCRIMINATOR_CALIBRATION.md`

Agents reading these files via path (Read tool, `cat`, kernel hooks)
follow the symlinks transparently. Agents writing to these paths write
through the symlinks to the private repo. The sibling layout
(`~/episteme/` and `~/episteme-private/`) is required for the relative
symlinks to resolve.

Public repo's `docs/PROGRESS.md` is NOT migrated — historical record +
trust signal stay public.
```

---

## Section E · Verification gates after migration

Run all of these. Any failure stops the migration; rollback per Section F.

```bash
cd ~/episteme

# 1. Symlink resolution — every migrated path must read its content
for f in docs/PLAN.md docs/NEXT_STEPS.md docs/ROADMAP_POST_V1.md \
         docs/DESIGN_V1_1_REASONING_ENGINE.md docs/POST_SOAK_TRIAGE.md \
         docs/PREPARED_PATCHES.md docs/DEFERRED_DISCOVERIES_TRIAGE.md \
         docs/DISCRIMINATOR_CALIBRATION.md; do
  [ -L "$f" ] && [ -r "$f" ] && head -1 "$f" > /dev/null && \
    echo "OK: $f" || echo "FAIL: $f"
done

# 2. Git status must show clean tree (symlinks gitignored)
git status   # nothing to commit; symlinks not appearing as untracked

# 3. episteme doctor — kernel runtime wiring intact
episteme doctor

# 4. episteme kernel verify — manifest integrity
episteme kernel verify

# 5. Test suite passes (one-off — soak is over by now)
PYTHONPATH=. pytest -q | tail -5

# 6. Hook firing on the public repo doesn't leak private content
#    Trigger a synthetic high-impact op and verify the chkpt commit
#    (if any) does NOT contain content from the migrated files.
git log --oneline -5
git show HEAD -- docs/PLAN.md   # should be empty (file no longer in tree)
```

If all six pass: migration successful. The private repo carries forward strategic planning; the public repo carries forward project identity.

---

## Section F · Rollback plan

If verification fails or the operator changes their mind, rollback is straightforward (no force-push, no history rewrite):

```bash
cd ~/episteme

# 1. Drop the migration branch's commit
git checkout master
git branch -D event-XX-strategic-docs-privatize

# 2. Reset public repo to pre-migration state (origin/master untouched if PR not merged)
git fetch origin
git reset --hard origin/master   # operator-only step (block_dangerous policy)

# 3. Verify symlinks gone, real files restored from origin
ls -la docs/PLAN.md   # should show regular file, not symlink
cat docs/PLAN.md      # should show pre-migration content

# 4. Undo gitignore additions
# Manually edit ~/episteme/.gitignore — remove the "Strategic docs migrated..." block

# 5. Optionally archive the private repo (don't delete — operator may revisit)
gh repo edit junjslee/episteme-private --description "ARCHIVED — migration rolled back YYYY-MM-DD"
gh repo archive junjslee/episteme-private
```

If the migration PR was already merged on origin: rollback requires a counter-PR that re-introduces the files (cherry-pick from the pre-migration commit) and removes the gitignore entries. The private repo content stays untouched as a backup.

---

## Section G · Product Protection Strategy

Operator's two questions, answered.

### G.1 · License recommendation

**Operator's stated goal:** *open for individual developers, prevent corporations from cloning and monetizing.*

The license matrix:

| License | Type | Operator-relevant property | Real-world adopters | For episteme |
|---|---|---|---|---|
| **MIT** (current) | Permissive OSS | Anyone can do anything; corps can clone + monetize freely | most of the OSS ecosystem | ❌ no protection — explicitly the case operator wants to leave |
| **Apache-2.0** | Permissive OSS + patent grant | Same as MIT plus patent-retaliation clause | Apache projects, many vendors | ❌ same protection profile as MIT |
| **AGPL-3.0** | Strong copyleft | Network use triggers source-disclosure; if a corp runs episteme as part of an internal service, they must publish the modified source | Grafana, MinIO (pre-AGPL exit), MongoDB (pre-SSPL) | ✅ partial — most corps refuse to AGPL their internal codebases, so it deters integration; OSI-approved (true OSS) |
| **BSL** (Business Source License) | Source-available | Free for non-production use; production use requires a commercial license; converts to OSS license (e.g., Apache) after a fixed time window (typically 4 years) | HashiCorp (Terraform), CockroachDB, Couchbase, Sentry (pre-FSL) | ✅ strong — explicit corp-monetization guard; community-tolerated though not OSI-approved |
| **FSL** (Functional Source License) v1.1 | Source-available | Like BSL but with explicit "non-competing use" exemption — corps can use internally; cannot use to build a competing product; converts to MIT or Apache after 2 years | Sentry (current), Keygen | ✅ best fit — non-competing exemption matches the "individual devs free; competitors restricted" intent precisely |
| **Elastic License v2** | Source-available | Free use except: (a) cannot offer as managed/hosted service, (b) cannot circumvent license, (c) cannot remove license | Elastic, Redis Labs (Redis Stack pre-fork) | ⚠️ targets cloud-resale specifically; episteme isn't primarily a SaaS-resale concern |
| **Commons Clause** + MIT/Apache | License-stack | Restricts "selling" the software; otherwise OSS-permissive | Redis (pre-RSAL), Akka (pre-BSL) | ⚠️ legally messier than purpose-built source-available licenses; community confusion |
| **SSPL** (Server Side Public License) | Aggressive copyleft | Running as a service forces all SaaS dependencies to be open | MongoDB, Elastic (pre-ELv2) | ❌ aggressively rejected by OSS community (Debian, Fedora, AWS); OSI explicitly rejected SSPL as not-open-source |

**Recommendation: FSL (Functional Source License) v1.1 with MIT 2-year future license.** Concrete reasoning:

1. **Non-competing-use exemption matches operator intent.** Individual developers and non-competing companies (anyone not building a *competing cognition-governance kernel for AI agents*) can use, modify, and embed episteme freely under FSL. Companies building competitors must wait the 2-year window before the code converts to MIT.
2. **2-year future-license window strikes the right balance.** Long enough to make near-term commercial cloning unattractive (a competitor would have to build today against 2-year-old episteme); short enough that the project's eventual OSS commitment is real, not theatrical. HashiCorp's BSL uses 4 years; that's longer than necessary for a fast-moving dev-tools space.
3. **Sentry uses FSL for the same business-defensibility reason.** Sentry is the closest comparable positioning to episteme — developer-facing tool, strong monitoring/observability adjacency, explicit anti-competitor framing. Their 2024 switch from BSL to FSL signals FSL is the more refined version of the BSL-class license.
4. **OSI-not-approved is acceptable for episteme's stage.** OSI alignment matters most for projects seeking enterprise/government adoption pipelines that have OSS-compliance procurement gates. Episteme is pre-1.0 with a single maintainer and no enterprise sales motion. The community-trust cost of "source-available, not OSS" is low here.

**Trade-off to be honest about.** Switching from MIT to FSL changes the license forward; everyone who has cloned under MIT keeps MIT for that snapshot. The license-change Event needs an explicit changelog entry naming the date. Some pure-OSS contributors will decline to engage with a non-OSI license — that's a real cost. For episteme's current threat model (corporate cloning + product-integration without licensing), FSL's protection clearly outweighs the contributor-pull cost.

**Implementation when operator chooses FSL:** replace `LICENSE` with the FSL v1.1 text from `https://fsl.software/`; add a clear `LICENSE.notice` explaining the future-MIT conversion; bump `kernel/CHANGELOG.md` MAJOR (license change is governance-class); announce on the public README + a release note.

**If operator prefers a different posture:**

- **Maximum protection (most defensive):** BSL with 4-year window. Discourages every form of commercial cloning more aggressively than FSL but rules out non-competing internal corp use without paid license.
- **Maximum openness with weak protection:** AGPL-3.0. True OSS. Corps technically can monetize but must publish derivatives under AGPL — most won't accept that obligation, so it deters integration.
- **Minimum disruption (status quo):** Keep MIT. Accept that the moat is the user-private chain (each operator's accumulated protocols), not the source code. The architecture-as-public-thesis stance is consistent with MIT.

> **Operator decision (Event 59 · 2026-04-25): AGPL-3.0 chosen.** The operator picked AGPL-3.0 over the FSL recommendation. Reasoning: strong copyleft is the cleanest deterrent — most corporations refuse to AGPL their internal codebases (AGPL-3.0's network-use trigger forces source disclosure if episteme is integrated into a hosted service), so AGPL produces the same "deters corp integration" effect as FSL's non-competing clause but with the additional benefit of being OSI-approved (true OSS, no community-trust cost). Commercial-licensing channel — for organizations that want to use episteme without AGPL obligations — is opened via the README footer (`For commercial licensing or consulting, contact me.`). The full FSL recommendation prose above is preserved as audit trail (Pillar 2 ethos: nothing changes silently); the actual choice is AGPL-3.0. The executable swap procedure lives at **§ J** below; the staged AGPL-3.0 license text is at `LICENSE.AGPL-3.0` (repo root) ready for the swap.

### G.2 · `git filter-repo` history scrub — recommendation: **DO NOT SCRUB**

The case for scrubbing: removes the historical visibility of `PLAN.md` / `NEXT_STEPS.md` / `DESIGN_V1_1` content from public commits. A determined competitor running `git log -p docs/PLAN.md` post-migration would still see every revision of strategic content prior to the migration.

The case against scrubbing dominates decisively for episteme's specific situation:

| Cost of scrubbing | Detail |
|---|---|
| **Force-push damage** | Rewriting every commit hash invalidates every fork's tracking branch. Anyone who has cloned (estimated < 50 unique clones at this stage but rising) gets a `non-fast-forward` error on next pull. Bad signal — reads as panic / cover-up. |
| **External-reference breakage** | Commit-hash permalinks in old GitHub issues, blog posts, social shares, kernel/CHANGELOG.md cross-references all break. Fixing them requires manual edits across surfaces operator may not control (other people's blog posts). |
| **GitHub indexing residue** | GitHub's own search/cache may retain old content for hours-to-weeks after the force-push. Scrubbing doesn't immediately make content unfindable. |
| **Partial coverage only** | Anyone who cloned BEFORE the scrub keeps the original history forever in their local copy. Scrubbing reduces but does not eliminate strategic-content discoverability. |
| **Trust-signal damage** | A force-push on `master` in a governance-themed project that explicitly markets `tamper-evident` chains is structurally hypocritical — the project would be tampering with its own most authoritative log. |

| Benefit of scrubbing | Detail |
|---|---|
| **Removes one search vector** | A casual `git log -p docs/PLAN.md` no longer surfaces strategic content. Determined adversaries have other vectors (cached clones, web archives, GitHub APIs). |
| **Decay-fast content already self-protects** | This week's `NEXT_STEPS.md` is irrelevant 3 months from now. Strategic content at any one timestamp ages out faster than the cost of scrubbing accrues. |
| **Most useful to true competitors** | A serious competitor who reads PROGRESS.md (which is NOT migrating) gets a clearer engineering retrospective than they would from raw PLAN.md history anyway. The scrub doesn't close the most-useful read. |

**Verdict.** Cost of scrubbing massively outweighs benefit. Leave history alone. Future strategic content goes private at the migration; past public content stays as the trust signal.

**Explicit exception path** (if operator decides to scrub anyway):

```bash
# DO ONLY at v1.0 GA cut, with explicit advance notice
# Pre-scrub: notify any known forkers + post a notice on the repo
git filter-repo --path docs/PLAN.md --path docs/NEXT_STEPS.md \
  --path docs/ROADMAP_POST_V1.md --path docs/DESIGN_V1_1_REASONING_ENGINE.md \
  --path docs/POST_SOAK_TRIAGE.md --path docs/PREPARED_PATCHES.md \
  --path docs/DEFERRED_DISCOVERIES_TRIAGE.md --path docs/DISCRIMINATOR_CALIBRATION.md \
  --invert-paths
git push --force-with-lease origin master

# Post-scrub: explicit changelog entry naming the date and the rationale
# (kernel/CHANGELOG.md major bump — this IS a governance-class operation)
```

If chosen: **schedule the scrub for the same Event as the migration**, not later. Bundling the destructive op with the architecturally-coherent migration commit is more honest than doing it as a separate "spring cleaning" Event whose intent is harder to read.

---

## Section H · Soak invariants (this draft Event)

This Event is **drafting only**; nothing executes during the soak. Specifically:

- ❌ NO `core/hooks/` edits.
- ❌ NO `core/blueprints/` edits.
- ❌ NO `src/episteme/` edits.
- ❌ NO `tests/` edits.
- ❌ NO `kernel/` edits.
- ❌ NO `git filter-repo` execution.
- ❌ NO LICENSE file changes.
- ❌ NO Section C migration commands run.
- ✅ ONE new `docs/POST_SOAK_MIGRATION_PLAN.md` file (this).
- ✅ Event 58 entry in `docs/PROGRESS.md`.
- ✅ Resume-here update in `docs/NEXT_STEPS.md`.

Day-7 grading proceeds unchanged. Soak clock continues from `2026-04-23T21:23:36Z` toward `~2026-04-30 21:23:36Z`. The migration EXECUTES post-soak only — when operator decides per `docs/POST_SOAK_TRIAGE.md` §4 routing.

---

## Section I · References

- `docs/POST_SOAK_TRIAGE.md` — Day-7 gate-grading rubric and Path 2.A / 2.B / 2.C decision rule. Migration triggers on Path 2.A (GA cut) or 2.B (v1.0.1-rc1 cut).
- `AGENTS.md` — `## Git workflow protocol — always-clean-master` (Event 57). The migration follows this protocol's Path A (PR-merge with `--merge` strategy).
- `core/memory/global/agent_feedback.md` — universal-principled rules. The license-change is a `Rule shape — positive vs negative system` decision (FSL is positive: enumerated "non-competing" allowed, default-deny; MIT is negative: enumerated nothing forbidden, default-allow).
- `kernel/CONSTITUTION.md` — root claim. License change is a governance-class operation, requires CHANGELOG MAJOR bump.
- `docs/EVOLUTION_CONTRACT.md` — propose → critique → gate → promote. Migration + license change are the largest single-Event governance ops in the repo's history; a gate-pass on the operator review is required before either executes.
- `https://fsl.software/` — Functional Source License v1.1 reference (FSL).
- `https://mariadb.com/bsl11/` — Business Source License v1.1 reference (BSL).
- `https://www.gnu.org/licenses/agpl-3.0.html` — AGPL-3.0 reference.
- `LICENSE.AGPL-3.0` (repo root) — staged AGPL-3.0 text prepared in Event 59. Swap procedure in § J below.

---

## Section J · AGPL-3.0 swap procedure (operator-decided · Event 59)

> **EXECUTES POST-SOAK ONLY.** License change is governance-class — bundles the active LICENSE rotation with manifest version-string updates + kernel/CHANGELOG MAJOR bump + public announcement. Do NOT run any command in this section while the v1.0.0-rc1 soak clock is active. Trigger: same as the strategic-doc migration above (Path 2.A GA cut, OR Path 2.B v1.0.1-rc1 cut). Operator may execute § J in the SAME Event as Sections C-D-E (one consolidated post-soak migration commit) OR in a separate follow-on Event — operator preference.

### J.1 · Pre-flight verification (in addition to § A)

```bash
cd ~/episteme

# 1. Confirm operator's license decision is still AGPL-3.0
#    If operator has changed their mind, abort and revisit § G.1.

# 2. Verify the staged license text matches canonical AGPL-3.0 byte-for-byte
diff <(curl -fsSL https://www.gnu.org/licenses/agpl-3.0.txt) \
     <(tail -n +27 LICENSE.AGPL-3.0)
# Should output nothing (byte-identity).
# (`tail -n +27` strips the staging header — adjust line count if the
#  staging header was edited after Event 59.)

# 3. Verify no recent commits modified LICENSE since Event 59 staging
git log --oneline -- LICENSE | head -5
# Most recent commit on LICENSE should be the original MIT addition;
# any subsequent commit means out-of-band license modification — investigate.

# 4. Verify kernel/CHANGELOG.md is ready for a MAJOR bump entry
ls kernel/CHANGELOG.md
```

### J.2 · The swap (one atomic commit)

```bash
cd ~/episteme
git checkout -b event-XX-license-swap-mit-to-agpl3 origin/master

# 1. Archive the MIT license under a clear name
git mv LICENSE LICENSE.MIT.archived

# 2. Promote the staged AGPL-3.0 file to active LICENSE
#    NOTE: edit the staged file FIRST to remove the staging header
#    (lines 1-26 of LICENSE.AGPL-3.0 — the box-drawn STAGED notice).
#    The active LICENSE must contain ONLY the AGPL-3.0 text starting at
#    "                    GNU AFFERO GENERAL PUBLIC LICENSE".
sed -i '' '1,/^================================================================================$/d' LICENSE.AGPL-3.0  # macOS sed; remove header through the closing separator
sed -i '' '1,/^$/d' LICENSE.AGPL-3.0                                                                                  # remove blank line after the header
git mv LICENSE.AGPL-3.0 LICENSE

# 3. Update manifest license fields — MIT → AGPL-3.0
sed -i '' 's/license = "MIT"/license = "AGPL-3.0-only"/' pyproject.toml
sed -i '' 's/"license": "MIT"/"license": "AGPL-3.0-only"/' .claude-plugin/plugin.json
sed -i '' 's/"license": "MIT"/"license": "AGPL-3.0-only"/' .claude-plugin/marketplace.json

# 4. Verify manifest fields were updated
grep -E '"license"|^license' pyproject.toml .claude-plugin/plugin.json .claude-plugin/marketplace.json

# 5. Add the kernel/CHANGELOG MAJOR entry (Evolution Contract requirement)
#    Operator authors the entry inline OR uses the template below.
```

### J.3 · `kernel/CHANGELOG.md` MAJOR entry (template — operator edits)

Append to `kernel/CHANGELOG.md` above the most recent version entry:

```markdown
## [vX.Y.Z] — YYYY-MM-DD — License switch · MIT → AGPL-3.0-only

**Governance-class change.** The kernel and all distribution artifacts
(`pyproject.toml`, `.claude-plugin/plugin.json`,
`.claude-plugin/marketplace.json`, public-facing `LICENSE`) switch from
MIT to AGPL-3.0-only effective this version.

**Why.** The kernel's value increasingly accrues to operators
who integrate it into hosted services (the Pillar 3 active-guidance
loop, the chain's tamper-evident provenance, Phase 12's calibration
loop — all become more valuable as they accumulate operator-private
data over time). Under MIT, a corporation could clone the kernel,
embed it into a closed-source hosted product, and ship without sharing
modifications back. AGPL-3.0's network-use disclosure trigger (§ 13)
forces source-availability for any hosted-service integration.
Individual developers and OSS projects retain full freedom; the
license operates as a deterrent against integration-without-disclosure.

**What changes for downstream users.**

- **Pre-this-version clones (under MIT)** keep MIT for that snapshot —
  MIT does not retroactively convert. Forks at older commits stay MIT.
- **From this version onward** (any code redistributed or hosted as a
  service) must comply with AGPL-3.0 § 13 disclosure. The reference
  implementation's `web/` surface satisfies § 13 by linking
  commit-permalinked source on every page footer + responding to
  `/source` route with the deployed source archive.
- **Commercial licensing** (internal corporate use, embedded in
  closed-source products) is available — see README footer for contact.
- **No code change** beyond LICENSE and manifest license fields. No
  kernel-architecture commitments are altered by this version.

**Audit trail.** Operator decision documented at:
- `docs/POST_SOAK_MIGRATION_PLAN.md` § G.1 (FSL recommendation +
  AGPL-3.0 operator-choice rationale; preserves both as audit trail)
- `docs/POST_SOAK_MIGRATION_PLAN.md` § J (this swap procedure)
- `docs/PROGRESS.md` Event 59 (staging) + Event XX (swap execution)
```

### J.4 · README license-switch announcement note

Add a banner near the top of `README.md` (above the TL;DR) that runs for
~30 days after the swap, then can be removed in a routine docs Event:

```markdown
> **License changed `MIT → AGPL-3.0-only` on YYYY-MM-DD.** Pre-vX.Y.Z
> clones keep MIT for that snapshot. From vX.Y.Z onward: AGPL-3.0
> applies (network-use disclosure per § 13). Commercial licensing
> available for organizations that prefer non-AGPL terms — see the
> [Commercial licensing](#commercial-licensing) footer.
```

### J.5 · Public announcement (operator-discretionary)

The license change is significant enough to warrant a public note beyond
the CHANGELOG entry. Recommended channels:

- GitHub Release notes for the version that ships under AGPL-3.0
  (separate `## License change` section before the standard release
  notes content)
- Project social channels (Twitter/X, LinkedIn, devrel platforms)
  if operator has those — not required, but increases the signal
  reach to potential downstream forks
- A blog post on `epistemekernel.com` or operator's personal site
  explaining WHY (the Section G.1 reasoning, in operator's voice)

Operator authors the announcement copy at execution time — voice and
positioning are operator-decisional, not template-able.

### J.6 · Commit + ship

```bash
cd ~/episteme
git add -A
git commit -m "chore(license): MIT → AGPL-3.0-only (Event XX · governance-class)"
git push -u origin event-XX-license-swap-mit-to-agpl3
gh pr create --title "chore(license): MIT → AGPL-3.0-only (governance-class)" \
  --body "Switches active license MIT → AGPL-3.0-only per docs/POST_SOAK_MIGRATION_PLAN.md § J. Pre-vX.Y.Z clones keep MIT for that snapshot; from this version onward AGPL-3.0 applies. Commercial licensing channel via README footer. See kernel/CHANGELOG entry for full rationale."
# Operator merges via GitHub UI with --merge strategy (Event-57 protocol Path A)
```

### J.7 · Post-swap verification

```bash
cd ~/episteme

# 1. LICENSE is now AGPL-3.0 (head should match canonical AGPL preamble)
head -5 LICENSE
# Expect:
#                     GNU AFFERO GENERAL PUBLIC LICENSE
#                        Version 3, 19 November 2007
#  Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>

# 2. LICENSE.MIT.archived exists (audit trail)
ls -la LICENSE.MIT.archived
head -3 LICENSE.MIT.archived
# Expect: MIT License header

# 3. LICENSE.AGPL-3.0 staged file is gone (renamed to LICENSE)
ls LICENSE.AGPL-3.0 2>&1
# Expect: No such file or directory

# 4. Manifest license fields all show AGPL-3.0-only
grep -E 'license' pyproject.toml .claude-plugin/plugin.json .claude-plugin/marketplace.json

# 5. CHANGELOG entry visible at top
head -30 kernel/CHANGELOG.md

# 6. README banner visible
head -25 README.md
```

If any of the six fails: rollback per § J.8.

### J.8 · Rollback (if swap surfaces issues post-merge)

License rollback is destructive in business terms (downstream users may
have already cloned under AGPL) but technically straightforward:

```bash
cd ~/episteme
git checkout master
git pull --ff-only origin master
git checkout -b event-XX-license-rollback origin/master

git mv LICENSE LICENSE.AGPL-3.0
git mv LICENSE.MIT.archived LICENSE

# Revert manifest license fields
sed -i '' 's/license = "AGPL-3.0-only"/license = "MIT"/' pyproject.toml
sed -i '' 's/"license": "AGPL-3.0-only"/"license": "MIT"/' .claude-plugin/plugin.json
sed -i '' 's/"license": "AGPL-3.0-only"/"license": "MIT"/' .claude-plugin/marketplace.json

# Revert kernel/CHANGELOG entry — manually edit out the AGPL section,
# add a `License rollback` MAJOR entry naming the date and rationale.

git add -A
git commit -m "chore(license): rollback AGPL-3.0 → MIT (Event XX)"
# Open PR, announce on the same channels that announced the original switch.
```

If rollback is needed: announce more carefully than the original switch.
Whiplash on license decisions damages community trust more than the
original switch did. A rollback should explain WHY the change didn't
hold (e.g., "downstream forks blocked critical contributions; AGPL
turned out to be a contributor-deterrent in practice").

---

## Section K · Reference Anchor Expansion (v1.1 prep · operator-decided Event 60)

> **EXECUTES POST-SOAK ONLY.** Editing `kernel/REFERENCES.md` is governance-class
> per Principle I (`kernel/CONSTITUTION.md`) — *introducing a new load-bearing
> borrowed concept into kernel wording without a corresponding `kernel/REFERENCES.md`
> entry violates Principle I.* The reverse is also true: adding a REFERENCES entry
> commits the kernel to a load-bearing concept and must be approved with the same
> care as the wording itself. Do NOT run any command in this section while the
> v1.0.0-rc1 soak clock is active. Trigger: same as the strategic-doc migration
> above (Path 2.A GA cut, OR Path 2.B v1.0.1-rc1 cut).

### K.1 · Pre-flight verification (in addition to § A)

```bash
cd ~/episteme

# 1. Confirm operator's review-resolved decisions are still standing.
#    If operator has changed mind on any of the four anchors (Peirce, Engelbart,
#    Bender, Heidegger) OR re-considered Girard, abort and revisit § G.1's
#    Operator decision paragraph + this section's K.4.

# 2. Soak window verified closed (Path 2.A or 2.B per § A pre-flight #1).

# 3. Audit existing kernel/REFERENCES.md for citation-overlap with the four
#    new anchors (deferred-discovery from Event 60 surface):
grep -niE "Peirce|Engelbart|Bender|Heidegger|abductive|stochastic.parrot|das.man|augmenting" kernel/REFERENCES.md
# If any match: operator decides whether the existing entry is sufficient,
# needs strengthening, or should be removed in favor of the K.2 entries.

# 4. Audit existing kernel/FAILURE_MODES.md mode 10 (`framework-as-Doxa`) for
#    whether it should also gain a citation pointer to Bender + Heidegger
#    (deferred-discovery from Event 60 surface):
grep -nA5 "mode 10\|framework-as-Doxa\|framework_as_Doxa" kernel/FAILURE_MODES.md
# Operator decides at execution: REFERENCES-only OR REFERENCES + mode-10-citation.

# 5. Audit DESIGN_V1_1_REASONING_ENGINE.md for the integration sites K.3 names:
grep -nE "Cognitive Arm A|Cognitive Arm B|Cognitive Arm C|abduct|bootstrap|Doxa" docs/DESIGN_V1_1_REASONING_ENGINE.md
# Confirms the K.3 sites still exist post-any-other-edits since Event 56.
```

### K.2 · The four anchor entries — exact text for `kernel/REFERENCES.md`

Operator copies the four blocks below into `kernel/REFERENCES.md` at the
location the existing references file uses (alphabetical OR thematic groupings;
see deferred-discovery #1 — operator picks at execution). Entries are written in
the same style as the existing references file: source citation → concept term →
how the kernel operationalizes it → cross-reference to specific spec locations.

#### K.2.A · Peirce — Abductive Reasoning (anchors Cognitive Arm B)

```markdown
### Charles Sanders Peirce — Abductive Reasoning

**Source.** Peirce, C. S. *Pragmatism as the Logic of Abduction* (Harvard
Lectures on Pragmatism, 1903). Modern philosophy-of-science reformulation:
Lipton, P. *Inference to the Best Explanation* (Routledge, 1991, 2nd ed. 2004).

**Concept.** Abduction is the third inferential mode (alongside deduction and
induction): the cognitive operation that *generates a hypothesis to explain
surprising observations* — the leap from scattered evidence to "the best
explanation that, if true, would account for what was observed." Peirce
defined abduction precisely as a separate mode of inference because neither
deduction (which derives consequences from premises) nor induction (which
generalizes from cases) can account for the act of *hypothesis formation
itself*.

**Where the kernel operationalizes it.** Cognitive Arm B (Causal Synthesis)
Step 2 — the LLM-driven Reflective Session — is structurally an abductive
inference. The kernel composes a structured prompt over a deferred-discoveries
cluster and asks: *"What is the SINGLE root-cause architectural flaw these N
entries point at, if any?"* This is the abductive leap from scattered
observations to a hypothesized root cause.

**Why this matters for D7.** Abduction is the *weakest* of the three
inferential modes. Peirce himself named this — abductive conclusions are
provisional and require independent verification. The kernel's D7 counter
(`per-entry independent verification on closure`) is the load-bearing
counterweight: the abductive Macro-CP hypothesis must be tested against
per-entry post-resolution evidence; a wrong root-cause shows up as M < N
closures-with-evidence rather than a silent macro-failure. The Peirce citation
makes the design's honesty about Arm B's weakest joint structurally visible.

**Cross-references.** `docs/DESIGN_V1_1_REASONING_ENGINE.md` § Cognitive Arm B
(Mechanism Step 2 + Goodhart resistance D7).
```

#### K.2.B · Engelbart — Augmenting Human Intellect (anchors Pillar 3 + Cognitive Arms A/C, with critical alignment)

```markdown
### Douglas Engelbart — Augmenting Human Intellect / Bootstrapping

**Source.** Engelbart, D. C. *Augmenting Human Intellect: A Conceptual
Framework* (Stanford Research Institute, AFOSR-3223, October 1962).

**Concept.** Intelligence Augmentation (IA) — the design stance that treats
computers as tools that *extend* human cognitive capability rather than
replace it. Engelbart's specific load-bearing mechanism is *bootstrapping*:
the recursive improvement loop where the tool that improves the tool
improves the tool, with humans and tools co-evolving over time. The 1962
framework imagines a continuous capability uplift through deliberate
tool-self-improvement.

**Where the kernel operationalizes it.** Pillar 3 (Framework Synthesis &
Active Guidance) is structurally an Engelbartian bootstrap loop: synthesized
protocols at decision N inform decision N+1; the framework refines itself
across operator-history. Cognitive Arms A (Temporal Integrity) and C
(Self-Consistency Convergence) extend the bootstrapping mechanism to the
kernel's own knowledge artifacts (protocols decay; protocols promote to
models; models derive disconfirmations).

**Critical alignment — episteme accepts the mechanism, rejects the optimism.**
Engelbart's 1962 framing assumed that augmentation is structurally beneficial.
The kernel's posture is post-Kahneman and post-deskilling: IA *without
structural constraints* produces operator deskilling — the human reasoning
capacity erodes when the tool's outputs are accepted uncritically. Episteme
installs the bootstrap loop *with* the constraints Engelbart's framework
lacks:

- **D3** (re-elicitation never auto-edits the framework — operator gates
  every promotion).
- **D11** (Operator Fatigue Guardrails — sub-second approval times flag as
  `attention_bottleneck` drift, counter to compliance-theater).
- **D2** (retrospective-only computation — the agent never sees the audit
  signature at decision time, so bootstrapping cannot Goodhart-optimize).

The citation positions episteme as *IA-aligned with constraints* rather than
naive-IA. The mechanism is shared with Engelbart; the optimism is not.

**Cross-references.** `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` § Pillar 3
(Framework Synthesis & Active Guidance); `docs/DESIGN_V1_1_REASONING_ENGINE.md`
§ Cognitive Arm A (Temporal Integrity) + § Cognitive Arm C (Self-Consistency
Convergence).
```

#### K.2.C · Bender et al. — Stochastic Parrots (ML anchor for anti-Doxa posture)

```markdown
### Bender, Gebru, McMillan-Major, Mitchell — Stochastic Parrots

**Source.** Bender, E. M., Gebru, T., McMillan-Major, A., & Mitchell, M.
*On the Dangers of Stochastic Parrots: Can Language Models Be Too Big?*
Proceedings of the 2021 ACM Conference on Fairness, Accountability, and
Transparency (FAccT '21), pp. 610–623. DOI: 10.1145/3442188.3445922.

**Concept.** Large language models predict the *statistically most likely
next token* given context, not context-fit truth. The "stochastic parrot"
metaphor names this directly: the model produces fluent, grammatically
correct, contextually-plausible output without any model of meaning or
verification against world-state. The paper's load-bearing critique: scale
alone does not produce understanding; bigger parrots are still parrots.

**Where the kernel operationalizes it.** The Reasoning Surface's structural
validation (≥ 15 character minimums on each field, lazy-token blocklist,
falsifiable Disconfirmation requirement, Knowns-Unknowns-Assumptions
separation) operates as a forcing function against the parrot's default
behavior. The model cannot satisfy the surface by emitting statistically-
fluent platitudes — the fields demand *specifics* (named observables, named
unknowns, named assumptions) that grep against the project tree (Layer 3
grounding). The validation does not make the model intelligent; it makes the
parrot's default behavior *insufficient* for the kernel to admit the op.

**Where the failure mode lives.** `kernel/FAILURE_MODES.md` mode 10
(`framework-as-Doxa`) names the risk that the kernel's accumulated framework
itself becomes the parrot — synthesized protocols crystallize past
statistical-central answers as future advice. Pillar 3's active-guidance
loop is exactly this risk; Cognitive Arm A (Temporal Integrity, Protocol
Decay) is the structural counter.

**Cross-references.** `kernel/FAILURE_MODES.md` mode 10; `kernel/REASONING_SURFACE.md`
(structural-validation contract); `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`
preamble (the "fluent-vacuous" framing).
```

#### K.2.D · Heidegger — Das Man (philosophical-ontological anchor for anti-Doxa posture)

```markdown
### Martin Heidegger — Das Man (the They)

**Source.** Heidegger, M. *Sein und Zeit* (Niemeyer, 1927); English: *Being
and Time*, trans. Macquarrie & Robinson (Harper, 1962). Specifically the
analysis of *Das Man* (the They / the anonymous They) in Division One,
Chapter IV (§§ 25–27).

**Concept.** *Das Man* names the existential-ontological structure by which
individual accountability dissolves into the average: *"one says,"* *"one
does,"* *"everyone agrees that..."* The "anonymous They" is not any specific
person — it is the structural mechanism by which inauthentic existence
defers responsibility to a statistical-conformity center. Heidegger's
analysis: Dasein (the being-that-can-question-being) tends toward *fallenness*
into Das Man as the path of least resistance; authentic existence requires
*resoluteness* — the act of taking individual responsibility for a specific
question, against the pull of the averaging They.

**Where the kernel operationalizes it.** LLM majority-voting is *Das Man at
scale*: the model speaks "as one says it" — the statistically-central answer
across training data — rather than as the specific context demands. The
Reasoning Surface's *Core Question* field is the structural counterforce:
the agent must declare *the one question this action is actually trying to
answer*, breaking from the averaging mode and assuming responsibility for a
specific, falsifiable claim. The Core Question is Heidegger's resoluteness
operationalized as a file-system contract.

**Why both Bender and Heidegger.** Bender et al. anchor the *empirical-
mechanistic* face of the critique (LLMs predict statistically-central
tokens). Heidegger anchors the *philosophical-ontological* root (averaging
is how accountability dissolves, regardless of substrate). The kernel needs
both depths: Bender names what the substrate does; Heidegger names *why
that matters* for the operator's authentic existence as a thinker.

**Cross-references.** `kernel/FAILURE_MODES.md` mode 10 (parallel root with
Bender); `kernel/REASONING_SURFACE.md` (Core Question field as resoluteness
contract); `docs/COGNITIVE_SYSTEM_PLAYBOOK.md` § 1 (Doxa framing).
```

### K.3 · Kernel-wording integration snippets — exact text for spec body insertions

Operator copies these into the named locations in
`docs/DESIGN_V1_1_REASONING_ENGINE.md` and `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`
when § K executes. Each snippet is one paragraph or sentence that names the
anchor inline so the kernel-wording carries the load-bearing citation.

#### K.3.A · Cognitive Arm B § Goodhart resistance (after current D7 paragraph)

Append to the D7 paragraph in `docs/DESIGN_V1_1_REASONING_ENGINE.md`
§ Cognitive Arm B § Goodhart resistance:

> The cognitive type of the Reflective Session is *abductive* in Peirce's
> sense (1903) — the leap from scattered observations to the hypothesis
> that, if true, would best explain them. Abduction is the weakest of the
> three inferential modes; Peirce himself named this. D7 is the kernel's
> structural answer to the abductive weakness — per-entry independent
> verification surfaces wrong-hypothesis closures as M < N evidence-confirmed,
> rather than letting the abductive leap pass uninspected.

#### K.3.B · Pillar 3 description (in DESIGN_V1_0_SEMANTIC_GOVERNANCE.md)

Append a paragraph to the Pillar 3 introduction in
`docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`:

> Pillar 3's bootstrap loop is *Engelbartian* in mechanism (1962): tool-
> human co-evolution where synthesized protocols at decision N inform
> decision N+1, with capability uplifting recursively across operator-
> history. The kernel accepts Engelbart's mechanism but rejects his 1962
> optimism — IA without structural constraints produces deskilling. The
> bootstrap loop here ships *with* the constraints Engelbart's framework
> lacked: D3 (re-elicitation never auto-edits), D11 (operator fatigue
> guardrails), D2 (retrospective-only computation).

#### K.3.C · Cognitive Arms A + C (in DESIGN_V1_1_REASONING_ENGINE.md)

Add a one-line annotation to each of Cognitive Arm A and Cognitive Arm C
introductions in `docs/DESIGN_V1_1_REASONING_ENGINE.md`:

For Arm A introduction:

> The arm extends Engelbart's bootstrap loop (1962) into the kernel's
> own knowledge artifacts — protocols become falsifiable across time,
> not just across cases.

For Arm C introduction:

> The arm carries the Engelbartian bootstrap mechanism toward an
> asymptote of self-consistency — protocols promote to models, models
> derive disconfirmations, the kernel's own self-model refines under its
> own discipline. The 1962 optimism stays rejected: every model inherits
> decay (D9), every promotion is operator-gated (D3), every auto-derived
> disconfirmation is operator-overridable (D10).

#### K.3.D · Anti-Doxa preamble (in DESIGN_V1_0_SEMANTIC_GOVERNANCE.md)

Append a paragraph to the *Why this exists* section in
`docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`:

> The anti-Doxa posture has two anchors. *Empirically*: Bender et al.'s
> Stochastic Parrots critique (FAccT 2021) — LLMs predict the
> statistically-central next token, not context-fit truth. *Philosophically-
> ontologically*: Heidegger's analysis of Das Man (Being and Time, 1927) —
> the "anonymous They" as the structural mechanism by which individual
> accountability dissolves into averaging. The kernel installs both depths
> as forcing functions: the Reasoning Surface's structural validation
> rejects the parrot's fluent-vacuous output (Bender), and the Core
> Question field forces the agent to break from Das Man and assume
> responsibility for the specific question this action addresses
> (Heidegger).

#### K.3.E · `framework-as-Doxa` mode 10 (in `kernel/FAILURE_MODES.md` — operator decision)

OPTIONAL parallel update — operator decides at execution whether mode 10's
entry should also gain a citation pointer to Bender + Heidegger, OR whether
the REFERENCES.md entries are sufficient cross-reference. If operator chooses
to add: append after mode 10's existing description:

> The failure mode's empirical mechanism is named in Bender et al.
> (Stochastic Parrots, 2021); its ontological-existential root is named
> in Heidegger's Das Man analysis (Being and Time, 1927). Cognitive Arm A
> (Temporal Integrity, Protocol Decay) is the kernel's structural counter:
> the framework cannot become the parrot if its protocols are themselves
> falsifiable across time.

### K.4 · Girard rejection — audit trail (Pillar 2 ethos: rejected candidates also recorded)

Operator considered and rejected René Girard's *mimetic theory* (Mensonge
romantique et vérité romanesque, 1961) as an anti-Doxa anchor during the
Event 60 review pass. The rejection rationale, preserved here as audit trail:

- **Mimetic stretch.** Girard's mimesis is *interpersonal desire transmission*
  — a theory of cultural anthropology built on imitation as the structure of
  human wanting. LLM token-prediction is *statistical conformity to training-
  data distributions*. The two share the surface word "mimesis" but the
  underlying cognitive structures differ. Citing Girard for the anti-Doxa
  posture would be metaphorically powerful but academically loose.

- **Tighter alternatives chosen.** Bender et al. directly anchors the ML-
  empirical mechanism (statistical averaging). Heidegger's Das Man directly
  anchors the philosophical-ontological structure (anonymous accountability
  dissolution). Both are tighter fits than Girard's mimesis; both together
  cover the empirical and ontological depths Girard would have only
  metaphorically gestured at.

- **Reference-quality consistency.** Episteme's existing references
  (Kahneman / Munger / Dalio / Popper / Boyd / Meyer) are all *direct*
  anchors to specific kernel mechanisms. Adding Girard as the only
  metaphorical citation would lower the average citation precision and
  invite the same loose-citation pattern in future spec work.

The rejection is final for v1.1 prep. If a future Event surfaces a tighter
operationalization of Girardian mimesis to a specific kernel mechanism (e.g.,
a new failure mode that genuinely involves interpersonal desire transmission
rather than statistical conformity), Girard can be reconsidered. Until that
specific operationalization is named, Girard stays out.

### K.5 · Commit + ship

```bash
cd ~/episteme
git checkout -b event-XX-references-anchor-expansion origin/master  # use real Event number at execution time

# 1. Edit kernel/REFERENCES.md — paste the four K.2 blocks at the operator's
#    chosen location (alphabetical OR thematic grouping per deferred-discovery #1).

# 2. Edit kernel/CHANGELOG.md — append a MAJOR or MINOR bump entry per the
#    Evolution Contract (governance-class: new load-bearing concepts entering
#    kernel wording). Title: "References expanded · Peirce + Engelbart + Bender + Heidegger".

# 3. Edit docs/DESIGN_V1_1_REASONING_ENGINE.md — paste the K.3.A snippet into
#    Cognitive Arm B § Goodhart resistance, and the K.3.C snippets into
#    Cognitive Arms A + C introductions. Bump the design doc status to
#    `approved (reframed, second pass)` per its own approval-versioning convention,
#    with an Approval Record paragraph documenting the Event-60-resolved decision.

# 4. Edit docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md — paste K.3.B into Pillar 3,
#    K.3.D into the Why-this-exists preamble.

# 5. (OPERATOR DECISION at execution) Edit kernel/FAILURE_MODES.md — paste K.3.E
#    into mode 10 description, OR skip if operator chooses REFERENCES-only scope.

# 6. Verify scope — confirm kernel/CHANGELOG.md MAJOR or MINOR bump, REFERENCES,
#    DESIGN_V1_0, DESIGN_V1_1 all updated coherently. Operator confirms.

git add -A
git commit -m "kernel(references): expand REFERENCES with Peirce + Engelbart + Bender + Heidegger; integrate kernel wording (Event XX)"
git push -u origin event-XX-references-anchor-expansion
gh pr create --title "kernel(references): Peirce + Engelbart + Bender + Heidegger anchors" \
  --body "Adds four reference anchors to kernel/REFERENCES.md per Event 60 review-resolved decisions. Wording integrated into Pillar 3 + Cognitive Arms A/B/C specs. Girard rejection preserved as audit trail in docs/POST_SOAK_MIGRATION_PLAN.md § K.4. CHANGELOG MAJOR/MINOR bump per Evolution Contract."
# Operator merges via GitHub UI with --merge strategy (Event-57 protocol Path A).
```

### K.6 · Post-execution verification

```bash
cd ~/episteme

# 1. All four anchors land in REFERENCES
grep -cE "Peirce|Engelbart|Bender|Heidegger" kernel/REFERENCES.md
# Expect: 4 or more (each anchor's block contains the surname multiple times).

# 2. Spec wording integrations land
grep -E "Peirce|abductive" docs/DESIGN_V1_1_REASONING_ENGINE.md
grep -E "Engelbart|bootstrap" docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md docs/DESIGN_V1_1_REASONING_ENGINE.md
grep -E "Bender|Stochastic Parrot" docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md
grep -E "Heidegger|Das Man" docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md

# 3. CHANGELOG entry visible at top
head -30 kernel/CHANGELOG.md

# 4. (If chosen) FAILURE_MODES mode 10 carries the citation pointer
grep -A10 "framework-as-Doxa" kernel/FAILURE_MODES.md

# 5. Girard NOT introduced as a kernel reference (rejection preserved in K.4)
grep -i "girard\|mimetic" kernel/REFERENCES.md
# Expect: nothing in kernel/REFERENCES.md.
# (Girard appears only in docs/POST_SOAK_MIGRATION_PLAN.md § K.4 audit trail.)
```

If any check fails: rollback per the same pattern as § J.8 (non-destructive
git revert, no force-push).

---

## Operator decision checklist (resolve before executing)

Answer each before running Section C (or § J / § K):

1. **Day-7 routing.** Is Day-7 grading complete? Path 2.A (GA cut) or Path 2.B (v1.0.1-rc1 cut) confirmed? Migration runs in either; do not run during the soak window.
2. **License path.** ✅ RESOLVED in Event 59 — **AGPL-3.0-only**. Staged at `LICENSE.AGPL-3.0` (repo root). Swap procedure at § J. Operator may execute § J in the same Event as Sections C-D-E (one consolidated post-soak migration commit) OR as a separate follow-on Event.
3. **History scrub.** Recommended: leave history alone. Operator override possible but strongly advised against. Decision must be made before executing Section C — bundle the scrub with the migration commit if chosen, not later.
4. **Sibling-layout assumption.** Migration assumes `~/episteme/` and `~/episteme-private/` are siblings on the operator's filesystem. Single-machine MacBook-Air-2 usage today is fine; multi-machine usage requires a follow-up plan (path-resolution via env var or git-submodule alternative).
5. **Path-coupling audit.** Section A step 6 — any tool/code that hardcodes a path to one of the 9 migrating files needs a separate decision (read-only is fine via symlink; write needs path update).
6. **Reference anchor expansion.** ✅ RESOLVED in Event 60 — **ADD Peirce + Engelbart + Bender + Heidegger; REJECT Girard.** Staged at § K above with exact `kernel/REFERENCES.md` insertion text + spec-body wording integration snippets. Operator may execute § K in the same Event as Sections C-D-E + § J (one consolidated post-soak governance commit) OR as a separate follow-on Event.

Once these six are resolved, Section C is mechanical. Operator runs the commands; migration completes in ~10 minutes. § J and § K run separately or bundled per operator preference.
