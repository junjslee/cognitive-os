# Continuity Plan

**Operational summary** (load first if you have a token budget):

- Episteme is currently a single-maintainer project. The architecture positions toward Path B (standard with reference implementation) per External Resonance Signal 001. **Standards require institutional continuity.** Without succession + decision-rights + escrow + foundation evaluation, "standard" is aspirational marketing.
- This document declares the bus-factor mitigation framework: who decides what, on what timeline, with what authority; what's preserved when the maintainer is unavailable; what triggers institutional governance.
- AGPL-3.0-or-later § 13 protects against extraction. It does NOT protect against bus-factor death. This document is the orthogonal protection.
- v1.1 first slice (Event 81 / CP-PROJECT-GOVERNANCE-CONTINUITY-01): **decision-rights framework + successor model + mirror-infrastructure declaration + foundation-evaluation criteria**. Foundation governance evaluation (Component 2) and lawyer engagement (Component 6) deferred to adoption-scale signal.

---

## What this is

Single-maintainer projects fail in ways multi-maintainer projects don't:

- The maintainer is unavailable for an extended period (life event, illness, irreconcilable distraction).
- The maintainer's positions on architecture become untenable to the community (visions diverge irreconcilably).
- Two divergent visions emerge for vN+1 with no governance to resolve.
- The maintainer dies. (The lowest-probability case but the highest-stakes one — also the one most reliably under-planned for.)

This document is the contract that says: *if any of those happens, here is what survives + here is who decides what.*

Without this contract, the kernel is "junjslee's project" — a proper noun bound to a single individual. With this contract, the kernel can become a standard — a common noun whose authority outlives any specific maintainer.

---

## What this is NOT

- **Not a binding legal document.** This is operator-authored intent + community-facing transparency. Foundation governance + lawyer-grade succession contracts are deferred to Component 2 + Component 6 of the CP, gated on adoption-scale signal.
- **Not a death plan.** The cases this protects against are mostly mundane: extended unavailability, acquired-elsewhere distraction, architectural disagreement. Death is the limit case, not the central case.
- **Not a transfer-of-authority preview.** The maintainer remains the maintainer until the maintainer says otherwise OR the trigger conditions below fire.

---

## § 1 · Decision-rights framework

Three decision tiers; each tier has a default actor + a fallback procedure when the actor is unavailable:

### Tier I · Architecture / spec evolution

**Decisions:** new pillars, new blueprints, kernel/* doc changes that alter load-bearing claims, breaking schema changes, license / governance shifts.

**Default actor:** maintainer (junjslee).

**Fallback procedure (maintainer unavailable for ≥ 4 weeks):** open governance issue at GitHub repo `junjslee/episteme` AND the operator-private mirror (per § 4 below). Decision deferred until maintainer responds OR a designated successor (per § 2) accepts authority via the documented succession protocol.

**Forbidden default actions in fallback:** force-push to master; relicense; merge breaking changes; promote any draft spec to approved status.

### Tier II · Polish / cleanup / non-breaking change

**Decisions:** v1.x.y patch releases, doc cleanups, hook fixes, CLI ergonomic improvements, test additions.

**Default actor:** maintainer (junjslee).

**Fallback procedure (maintainer unavailable for ≥ 2 weeks):** designated successor (per § 2) may merge non-breaking PRs marked with the `polish` or `cleanup` label after the documented review checklist. Successor has merge authority on Tier II only.

### Tier III · Routine / operational

**Decisions:** dependency bumps, CI config tweaks, README typo fixes, marketing-surface (web/) updates that don't touch kernel/*.

**Default actor:** any contributor with merge rights.

**Fallback procedure:** standard PR review; merge after one approval. No special procedure.

---

## § 2 · Successor model

A designated successor is **NOT** a co-maintainer-by-default. Designation is a declared authority that activates under fallback conditions (Tier I or Tier II availability triggers).

### Designation procedure

1. The maintainer names a successor in writing in this document (§ 5 below) and in a private succession-record document held in `~/episteme-private/docs/CONTINUITY_RECORD.md` (operator-personal; not in public git).
2. The successor accepts in writing in the same documents.
3. The successor is granted GitHub repo merge rights at the time of designation (but does not exercise them on Tier I / Tier II decisions until fallback triggers fire).

### Activation triggers

- Maintainer-unresponsive on a Tier I PR for 4 consecutive weeks → successor may activate Tier I authority.
- Maintainer-unresponsive on a Tier II PR for 2 consecutive weeks → successor may activate Tier II authority.
- Maintainer-declared transfer (signed in the succession record) → immediate activation.
- Maintainer-deceased (verified via independent attestation) → immediate full activation.

### Constraints on successor authority

- Successor cannot relicense (§ 1 Tier I forbidden default).
- Successor cannot rewrite history (force-push) without operator-survivor sign-off.
- Successor cannot remove the AGPL-3.0-or-later § 13 disclosure obligation.
- Successor inherits the no-AI-co-author-trailer rule (per `~/episteme/core/memory/global/agent_feedback.md`) until amended via Tier I governance event.

### As of this document version

**Successor designation: NOT YET FILLED.** Component 3 of CP-PROJECT-GOVERNANCE-CONTINUITY-01 names the search + designation as work for v1.1+ cycle. This document ships the framework; the actual designation happens when the maintainer identifies + invites + receives written acceptance from a candidate.

---

## § 3 · What's preserved (the substrate)

When the maintainer is unavailable, what survives:

### Public substrate (under AGPL-3.0-or-later)

- The full kernel source tree at `github.com/junjslee/episteme` master.
- All released tags (v0.x, v1.0, v1.x).
- The web surface at `epistemekernel.com` (if hosting renewal lapses, the static substrate is in git).
- The Claude Code plugin marketplace listing (operator-account-bound; survives via plugin-marketplace ToS).
- Public docs + READMEs (4 languages: English / Korean / Spanish / Chinese).

### Private substrate (operator-personal; not auto-survivable)

`~/episteme-private/` is on the operator's machine. It contains operational state (PROGRESS.md, NEXT_STEPS.md, PLAN.md), positioning narrative (POSTURE.md, NARRATIVE.md), strategic forward-vision (DESIGN_V1_1_REASONING_ENGINE.md, ROADMAP_POST_V1.md), the CP queue (cp-v1.0.1-polish.md, cp-v1.1-architectural.md, cp-v1.2-federation.md), the operator's profile canonicals (operator_profile.md, cognitive_profile.md, workflow_policy.md, agent_feedback.md), and the SOAK_CLOSE_LOG, EXTERNAL_RESONANCE, and CONTINUITY_RECORD documents.

**Without explicit escrow infrastructure (§ 4 below), the private substrate dies with the maintainer's machine access.**

### What's lost without § 4 mitigation

- Roadmap context (why decisions were made; what alternatives were evaluated).
- Operator-personal cognitive substrate (the profile canonicals are private by design).
- The unbroken audit trail of governance decisions (PROGRESS.md narrative).
- The CP queue's deferred work (without escrow, the next-Event roadmap evaporates).

---

## § 4 · Mirror infrastructure

To make the private substrate auto-survivable WITHOUT publishing it (which would defeat the privatization), the recommended mirror posture:

### Layer 1 · Encrypted local backup

The maintainer maintains a regularly-refreshed encrypted backup of `~/episteme-private/` on a separate physical device (not just iCloud / Time Machine — those are bound to the maintainer's account). Format: tar.gz + age-encrypted; recovery key stored physically separate from the device.

**Cadence:** monthly during active development; quarterly during steady-state.

**Status as of this document:** **NOT YET WIRED.** This is operator-side infrastructure work — a backup script + key-storage discipline. Tracked as a follow-up to this Event.

### Layer 2 · Trusted-third-party escrow

A trusted third party (legal counsel, designated successor, or family member) holds an encrypted copy of `~/episteme-private/` + the recovery key. Released to the successor / community on documented trigger.

**Trigger:** maintainer-deceased (verified via independent attestation) OR maintainer-explicit-release (signed in succession record).

**Status as of this document:** **NOT YET ARRANGED.** External-stakeholder work; gated on adoption-scale signal that warrants this complexity.

### Layer 3 · Selective publication on succession

Upon successor activation under § 2, the successor may selectively publicize portions of `~/episteme-private/` that materially affect Tier I decisions. Defaults:

- PROGRESS.md: publishable as historical record.
- PLAN.md / NEXT_STEPS.md / cp-* files: publishable as roadmap continuity.
- operator_profile.md / cognitive_profile.md: NOT publishable (they encode the original maintainer's cognitive style; not the successor's).
- agent_feedback.md: publishable selectively (universal rules can carry forward; project-specific rules need re-validation).

The successor uses judgment; this default list is the starting point.

---

## § 5 · Foundation governance evaluation criteria (deferred)

When the kernel reaches sufficient adoption scale, foundation governance becomes load-bearing. The criteria for that transition:

### Adoption-scale triggers

- ≥ 100 forks of the public repo OR ≥ 1000 unique cloners over a rolling 90-day window.
- ≥ 3 institutional adopters (companies, research labs, universities) integrating the kernel into production workflows.
- ≥ 1 external contributor with merge-tier history of ≥ 5 substantive PRs.
- A dependent project / standard implementer surfaces (per Path B positioning).

When at least 2 of the 4 trigger.

### Evaluation candidates

- **Linux Foundation umbrella** (e.g., LFAI&Data) — institutional anchor for AI-tooling standards; high overhead but high-credibility.
- **Apache Software Foundation** — mature governance template; well-known to adopters.
- **Open Source Initiative** — standards-body posture rather than codebase-host; complementary to LF/ASF.
- **Standalone non-profit** — bespoke 501(c)(3) governance; maximum control but maximum administrative cost.

### Evaluation criteria

- Cost (time + money) of foundation participation vs benefit (institutional credibility + bus-factor mitigation).
- Compatibility with AGPL-3.0-or-later license + § 13 disclosure ethos.
- Foundation governance compatibility with kernel's own anti-Doxa discipline (does the foundation impose statistical-mean decision-making on the project?).
- Speed: how long from foundation entry to fully-governed steady state.

**Status as of this document:** **NOT YET TRIGGERED.** Per Event 72 signal-check (Day-7 baseline): forks=2, unique cloners=1034 over 14 days, external contributors=0, dependent projects=0. Below trigger threshold. Re-evaluate at v1.2+ adoption checkpoint.

### Activation procedure

When triggers fire:

1. Open a Tier I governance issue evaluating candidates against the criteria.
2. Engage external counsel (Component 6 of CP-PROJECT-GOVERNANCE-CONTINUITY-01) for foundation-vs-standalone-non-profit comparison.
3. Operator-decision: foundation vs standalone vs status-quo (continue maintainer-led).
4. If foundation: draft transfer-of-stewardship agreement; align with foundation's governance cadence; transition over 6-12 month window.

---

## § 6 · EVOLUTION_CONTRACT.md extension (deferred to Component 5)

The existing `docs/EVOLUTION_CONTRACT.md` (governance machinery for kernel evolution) does NOT currently cover succession. CP-PROJECT-GOVERNANCE-CONTINUITY-01 Component 5 calls for an extension covering:

- The succession activation triggers from § 2.
- The decision-rights framework from § 1.
- The mirror infrastructure obligations from § 4.
- The foundation evaluation criteria from § 5.

**Status as of this document:** **NOT YET EXTENDED.** Tracked as follow-up Event after this doc lands. The extension is mechanical (cross-reference + integration); the load-bearing content is in this file.

---

## What's load-bearing for v1.1 vs v1.2+

**Load-bearing for v1.1 (Event 81 first slice):**
- This document itself. Shipping the framework + criteria.
- Public surface acknowledgment: README + AGENTS.md may eventually link here for institutional readers.

**Load-bearing for v1.2+ (deferred):**
- Successor designation (§ 2 — needs candidate).
- Mirror infrastructure wiring (§ 4 Layers 1-2 — operator-side work).
- Foundation evaluation activation (§ 5 — gated on adoption signal).
- EVOLUTION_CONTRACT.md extension (§ 6 — Component 5 follow-up).
- Lawyer engagement (Component 6 — gated on adoption signal).

---

## Cross-references

- [`AGENTS.md`](../AGENTS.md) — repo operating policy; this file extends it with succession-tier governance.
- [`docs/EVOLUTION_CONTRACT.md`](../docs/EVOLUTION_CONTRACT.md) — governance machinery; succession extension lands here per Component 5.
- [`kernel/CONSTITUTION.md`](./CONSTITUTION.md) — Pillar 4 (working-simple precedes working-complex; Gall) — the framework here is intentionally simpler than full foundation governance; complexity is gated on adoption signal.
- [`kernel/MODEL_PROGRESS_RISK_MODEL.md`](./MODEL_PROGRESS_RISK_MODEL.md) § Posture C — graceful-obsolescence plan complements the succession plan; succession serves the kernel-still-relevant case, obsolescence serves the kernel-no-longer-load-bearing case.
- `~/episteme-private/docs/cp-v1.1-architectural.md` § CP-PROJECT-GOVERNANCE-CONTINUITY-01 — spec source.
- `~/episteme-private/docs/EXTERNAL_RESONANCE.md` § Signal 001 — Path B framing requires succession discipline; this doc operationalizes that requirement.
- `LICENSE` (AGPL-3.0-or-later) — protects against extraction; this doc protects against bus factor (orthogonal).

---

## Maintenance

This file is correct when:

- The decision-rights framework (§ 1) reflects the current maintainer + successor state.
- The successor designation (§ 2) is filled OR explicitly named as not-yet-filled with a follow-up trigger.
- The mirror infrastructure (§ 4) is wired OR explicitly named as not-yet-wired with a follow-up trigger.
- The foundation evaluation criteria (§ 5) trigger thresholds are current with adoption signals.
- The cross-references resolve.

Version: v1.0 (Event 81, 2026-04-29). First slice: framework + criteria + named follow-ups. Components 2 + 5 + 6 (foundation evaluation, EVOLUTION_CONTRACT extension, lawyer engagement) deferred to adoption-scale signal triggers.
