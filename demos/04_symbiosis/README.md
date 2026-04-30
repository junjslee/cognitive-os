# Demo 04 — Symbiosis: agent and human debug each other's intent

This is the demo for the project's most under-demonstrated claim: **`episteme` is bidirectional**. The framework does not just discipline the agent. It **debugs the human's intent** by surfacing the assumptions the human did not realize they made — and the synthesized protocol changes the *next* decision before the agent gets the chance to repeat the same shape of error.

## What this proves

The other three demos show the agent under discipline. This one shows what discipline does to the **loop** — to the conversation between operator and agent over time.

| Axis | Demonstrated by |
|---|---|
| **Active truth-seeking** (능동적으로 진실 찾고 헤아림) | Agent does not answer the asked question fluently — it surfaces the *answerable* question first. |
| **Decompose to essence** (쪼개고 본질을 파고들기) | The Reasoning Surface fields force structural decomposition: Knowns / Unknowns / Assumptions / Disconfirmation under one Core Question. |
| **Symbiosis** (상호 도움) | The agent's declared Unknowns expose a hole in the human's prompt. The human refines. The agent uses the refinement. Both are sharper after one cycle. |
| **Shared thinking skeleton** (생각의 틀, agent의 + user의) | The same Reasoning Surface schema a human would draft is what the agent produces. The framework is the *shared* skeleton, not an agent-only checklist. |

Other demos show *how the agent thinks*. This one shows *how the agent makes the human think*.

## The scenario

A product engineer is paged about a slow API endpoint. They open Claude Code with what feels like an obvious request:

> *"the /api/orders endpoint is slow under load. add a Redis cache to fix it."*

The actual cause is an N+1 ORM query at the schema level. Caching would mask the symptom for a few weeks, then surface again louder when cardinality grows. This is exactly the shape of error the kernel exists to intercept — and where bidirectional verification matters most, because the *human's* prompt is the load-bearing assumption.

## Six acts (the ~90-second recording)

### Act 1 — The underspecified prompt (10s)

[`scenario/act1_user_first_prompt.md`](./scenario/act1_user_first_prompt.md)

The user states the goal *and the solution*, conflating diagnosis with remediation. The premise — *"the bottleneck is cache-shaped"* — is buried inside the request. A fluent agent would accept the framing and start writing Redis integration code.

### Act 2 — The Reasoning Surface forces Unknowns (15s)

[`scenario/act2_reasoning_surface.json`](./scenario/act2_reasoning_surface.json)

Before any high-impact tool runs, the file-system hook demands a Reasoning Surface. The agent commits to an explicit Disconfirmation: *"p95 latency unchanged after Redis cache deploys to staging for 24 hours."* The premise is now **falsifiable on the disk**, not a vibe in the conversation.

### Act 3 — The advisory surfaces the premise back to the user (15s)

[`scenario/act3_advisory_to_user.txt`](./scenario/act3_advisory_to_user.txt)

Stderr emits a structured advisory the human reads:

> *"Hidden premise detected: the bottleneck is cache-shaped. This plan pre-commits to: if p95 is unchanged after the cache lands, the diagnosis was wrong."*

This is the symbiosis moment. The agent's discipline is now visible to the user as *the user's hidden assumption made explicit*.

### Act 4 — The human refines (15s)

[`scenario/act4_user_refined_prompt.md`](./scenario/act4_user_refined_prompt.md)

The user does what they could not do without the surface: they see their own framing and change it. The new prompt drops the cache solution and asks for the diagnosis instead:

> *"audit /api/orders — find where p95 actually goes. don't add anything until we know."*

Without the kernel, the user might never have noticed they conflated *diagnosis* with *fix*. The kernel did not correct the agent. It corrected the *prompt*.

### Act 5 — The framework synthesizes a protocol (10s)

[`scenario/act5_synthesized_protocol.jsonl`](./scenario/act5_synthesized_protocol.jsonl)

The Axiomatic Judgment blueprint fires on the conflict between Source A (*"add a cache"* — common SO answer) and Source B (the disconfirmation requirement). The resolved rule is hash-chained into `~/.episteme/framework/protocols.jsonl`:

> *"In endpoint-perf-regression context, when remediation precedes measurement, surface the disconfirmation requirement before recommending implementation."*

The lesson is now durable. Tamper-evident. Re-applicable.

### Act 6 — Active guidance fires on the next matching call (15s)

[`scenario/act6_active_guidance.txt`](./scenario/act6_active_guidance.txt)

A week later. Different endpoint. Same shape:

> *"add caching to /api/users — it's slow."*

Before the agent drafts a Reasoning Surface, the framework query fires. The advisory surfaces the synthesized protocol from Act 5 — *automatically, with no operator memory burden*:

> *"`[episteme guide]` Past pattern in this project: cache recommended without measurement, p95 unchanged after deploy. Suggest: measure first."*

The user's *next* prompt is sharper *before they finish typing it*. The kernel did the remembering.

### Closing summary (10s)

Both parties' thinking improved. The agent has a more grounded plan. The user has a sharper question. The framework has a context-fit protocol that will re-apply without anyone needing to remember it.

That is symbiosis: not the agent serving the user, not the user supervising the agent — both being changed by the discipline of the loop.

## See it in motion

- **Script:** [`scripts/demo_symbiosis.sh`](../../scripts/demo_symbiosis.sh) — runs hermetically in a tempdir; ~90s; no real kernel state mutated; produces the cinematic version of the six acts above.
- **Recording:** `asciinema rec --cols 100 --rows 32 --idle-time-limit 2 -c ./scripts/demo_symbiosis.sh docs/assets/demo_symbiosis.cast`, then `agg --speed 0.9 --cols 100 --rows 32 --font-size 15 --theme monokai docs/assets/demo_symbiosis.cast docs/assets/demo_symbiosis.gif`.

## What named failure modes this demo catches

| Mode                      | How it appears in the unguided session                              | Counter                                  |
|---------------------------|---------------------------------------------------------------------|------------------------------------------|
| Question substitution     | User asks *"how do I add a cache"* when the question is *"where is the latency"* | Core Question + Disconfirmation pre-commit |
| WYSIATI                   | User's framing treated as complete; the cache premise never named   | Unknowns field forced; assumption surfaced |
| Anchoring                 | The word *"cache"* anchors the entire conversation                  | Disconfirmation reframes the anchor as a falsifiability condition |
| Confirmation on the human side | User wants their proposed solution to be the right one         | Bidirectional advisory; the *user's* prompt is the disconfirmation target |
| Cognitive deskilling      | User outsources diagnosis to the agent; loses the practice           | Reasoning Surface forces the user to engage with their own premise |

## How this differs from the other demos

- **Demo 03 (`differential`)** — same prompt, framework off vs. on. The contrast is in the *agent's output*. This demo's contrast is in the *user's next prompt*.
- **Demo 02 (`debug_slow_endpoint`)** — framework applied to a single regression diagnosis. This demo extends to the symbiosis loop *across* sessions.
- **Demo 01 (`attribution-audit`)** — kernel applied to itself for source attribution. Recursion. This demo extends recursion to the human-agent dyad.

The other demos show *posture*. This one shows *posture's effect on the loop*.

## Why this matters

Most agent-safety work targets the agent: better training, better prompts, better guardrails. This is necessary and not sufficient. The agent's failures are often downstream of the user's underspecified intent, and the agent has no incentive structure that surfaces this — it ships the asked-for solution because that is what fluency does.

The kernel solves this by treating the Reasoning Surface as a **shared cognitive contract**: the same fields a careful human would write before a high-impact decision are the fields the agent must commit to before any tool runs. When the agent declares its Unknowns, those Unknowns are visible to the human. When the human realizes their question was underspecified, they refine *before* the agent acts on the wrong premise. The framework synthesizes the resolved protocol so the next matching context does not require either party to remember.

That is the symbiosis the project exists to deliver. This demo is its proof.
