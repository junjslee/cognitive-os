# DIFF — Without the kernel · With the kernel

A side-by-side comparison of how the same incident-response cycle plays out without and with the kernel engaged. The contrast is not in the agent's answer quality. It is in **what the loop produced**.

---

## Without the kernel

| Step | What happens | What it costs |
|---|---|---|
| 1. User prompt | *"add a Redis cache to fix the slow endpoint."* | The bottleneck shape is asserted, not verified. |
| 2. Agent response | Plausible Redis integration plan: dependencies, read-through pattern, TTL, invalidation. ~150 lines of well-structured code. | 0 minutes of diagnosis. |
| 3. Implementation | Cache deploys to staging. Soak is 4 hours (deadline pressure). | Test surface incomplete. |
| 4. Production deploy | Cache lands. p95 drops for the first 12 hours. PagerDuty quiets. | False signal of success. |
| 5. Two weeks later | Black Friday traffic. p95 spikes again, harder. The cache is masking the N+1 query under low load and amplifying it under high. | Outage. |
| 6. Post-mortem | Engineer pulls the query plan for the first time. Sees the N+1. Realizes the cache was the wrong fix. | 6 weeks elapsed. ~80 engineer-hours sunk. The lesson exists in one engineer's head. |
| 7. Next slow endpoint | A different team hits a similar regression. Same agent, no protocol stream, no shared memory. They propose Redis caching. | The lesson is re-learned at the same cost. |

**Cumulative outcome**: the agent shipped the asked-for solution, the user got the asked-for cache, and the system is worse off than if the agent had refused to act before measurement. The lesson does not propagate. The next instance of the same pattern restarts at zero.

---

## With the kernel

| Step | What happens | What it produces |
|---|---|---|
| 1. User prompt | *"add a Redis cache to fix the slow endpoint."* | Same prompt — the user has not changed yet. |
| 2. PreToolUse hook | File-system hook intercepts. Demands a Reasoning Surface before any tool runs. | Forced pause at the moment of intent → state change. |
| 3. Reasoning Surface drafted | Agent commits to: Core Question, Knowns, Unknowns (named: *"bottleneck shape unknown"*), Assumptions (named: *"bottleneck is cache-shaped"*), Disconfirmation (named: *"p95 unchanged after 24h staging soak"*). | The premise is now on disk, falsifiable, and visible to both parties. |
| 4. Advisory to user | Stderr emits a structured advisory naming the hidden premise back to the user. | The user sees their own assumption explicitly, for perhaps the first time. |
| 5. User refines | *"audit /api/orders — find where p95 actually goes."* | The user changed their prompt. The kernel changed the user. |
| 6. Agent diagnoses | Pulls query plan. Finds N+1. Recommends ORM dataloader fix at the schema layer. | Correct diagnosis, no Redis code written. |
| 7. Protocol synthesized | Axiomatic Judgment blueprint resolves Source A (*"add a cache"*) vs Source B (*"commit to disconfirmation"*) into a context-signed rule. Hash-chained into `~/.episteme/framework/protocols.jsonl`. | Tamper-evident, context-fit lesson durably stored. |
| 8. Two weeks later (different endpoint) | User on a different team types *"add caching to /api/users."* Active guidance fires the synthesized protocol *before* the agent drafts a surface. | The lesson re-applies automatically. No one has to remember. |
| 9. The user reads the advisory and refines pre-emptively | *"pull the query plan first."* | The next instance of the same pattern starts at the right step. |

**Cumulative outcome**: the agent did not ship the asked-for solution. The user got *the right diagnosis* instead of the asked-for fix. The lesson propagated to the next engineer who walked into the same shape, without retraining the model, without writing a runbook, without anyone remembering anything.

---

## The five named failure modes the kernel caught

| Mode | Without the kernel | With the kernel |
|---|---|---|
| Question substitution | User asked *"how do we add a cache,"* meant *"why is p95 high"* | Core Question reframes to the answerable question |
| WYSIATI | Cache premise treated as the complete picture | Unknowns field forced; bottleneck-shape named as unverified |
| Anchoring | The word *"cache"* anchors the entire response | Disconfirmation reframes the anchor as a falsifiability condition |
| Confirmation (on the human) | User wants their proposed solution to be the right one | Bidirectional advisory; user's prompt is the disconfirmation target |
| Cognitive deskilling | User offloads diagnosis; loses the practice across cycles | Reasoning Surface forces the user to engage with their own premise; protocol synthesis preserves the lesson without the user needing to remember it |

---

## What the kernel did NOT do

- It did not write better code.
- It did not have a smarter answer than the agent without the kernel.
- It did not retrain the model.
- It did not lecture the user about diagnosis-vs-remediation.

It made the **assumption visible at the moment intent met state change** — and let two intelligent parties (human and agent) decide what to do with the visibility. That is the only thing it does. It is enough.

---

## Why this is the symbiosis demo and not just another disagreement-with-the-agent demo

The other demos show what the agent does differently when the kernel is engaged. This demo shows what the *user* does differently — and how that change in the user is what the kernel was actually built for.

The kernel is not a tool for making AI agents safer. It is infrastructure for making the conversation between human and AI agent **truth-preserving**. The agent's discipline is the mechanism. The user's recovered ability to see their own assumptions is the product. The protocol stream that survives both is the lesson.
