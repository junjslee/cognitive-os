# Act 4 — The human refines

The user reads the advisory. There is a moment — short but real — where the framing they did not realize they had imported becomes visible to them. The word *"cache"* in their first prompt was not a fact about the system. It was a hypothesis pattern-matched from the most common shape of the answer to *"slow endpoint."*

The user types again:

> *"audit /api/orders — find where p95 actually goes. don't add anything until we know."*

## What changed

The new prompt is structurally different from the first:

| First prompt | Refined prompt |
|---|---|
| Conflates diagnosis with fix | Separates diagnosis from fix |
| Names a remediation (Redis cache) | Names a *measurement* (where p95 goes) |
| Pre-commits to building | Pre-commits to *not* building yet |
| Treats the bottleneck shape as known | Treats the bottleneck shape as the question |

The agent did not coach the user to ask this question. The agent declared its own Unknowns — and those Unknowns surfaced the user's hidden assumption back to the user. The user changed their own prompt.

## Why this is the load-bearing moment of the demo

This is the symbiosis the project exists to deliver. Not a smarter agent serving an unchanging user. Not a careful user supervising a careless agent. Both parties' thinking changed because the loop forced the assumptions into the open where either party could see them.

The agent's Reasoning Surface is the artifact. The bidirectional verification is the property. The protocol about to be synthesized — *"when remediation precedes measurement, surface the disconfirmation requirement"* — is the durable lesson the framework will carry forward without either party needing to remember.

That synthesis happens in Act 5.

## What the agent does next

With the refined prompt, the agent's next Reasoning Surface is sharper:

- **Core Question** — *"What is the time decomposition of a single /api/orders request, and does the breakdown identify a cache-shaped, query-shaped, or contention-shaped bottleneck?"*
- **Knowns** — the same baseline (p95 over SLO, fans out to two tables) plus the new known: *"the user has explicitly de-prioritized writing remediation code until the bottleneck shape is named."*
- **Disconfirmation** — *"the diagnostic trace fails to identify a single dominant time component (> 50% of request budget)."*

The agent is now solving the *answerable* question. That is the question the kernel exists to surface.
