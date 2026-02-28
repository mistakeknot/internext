# internext — Vision and Philosophy

**Version:** 0.1.0
**Last updated:** 2026-02-28

## What internext Is

internext is a work prioritization skill for Claude Code. It reads live beads state (the `bd` CLI) as the authoritative source of open work, scores each candidate on impact, effort, and risk axes, and produces an opinionated recommendation — one clear answer, not a menu. It is not a project management tool. It does not create or modify work items. It reads, scores, and recommends.

The core output is a structured tradeoff analysis: what you gain and what you defer by choosing each option, plus a single recommended next action backed by an explicit rationale. The scoring is numeric (1-5 per axis) so the reasoning is auditable, not a narrative that hides the calculation.

## Why This Exists

Agents pick the wrong work. They default to whatever is at the top of the backlog, whatever is most recently mentioned in context, or whatever feels like forward progress without checking whether something else has more leverage. internext exists to inject a structured review phase before execution — to force the question "is this actually the best use of this session?" before any code is written. It is a companion to Clavain's review-phase discipline, applied to the prioritization decision specifically.

## Design Principles

1. **Evidence over narrative.** Scores come from beads state — open items, blocked status, recency of completions, dependency chains. Not from guesses or vibes.
2. **Opinionated by design.** A recommendation with a clear rationale beats a balanced menu. The user can override; the skill should not hedge by default.
3. **Completion bias.** Finishing in-progress work almost always beats starting new work. The analysis weights this explicitly: unfinished work carries context-loss risk that a raw priority score misses.
4. **Unblocking multiplies value.** An item that unblocks three downstream beads is scored higher than a standalone item at the same priority tier. Dependency leverage is a first-class factor.
5. **Strong defaults, replaceable weights.** The 1-5 scoring axes and the impact-to-effort ratio heuristic are defaults. Users can tune what matters (e.g., prefer lower-risk items near a release).

## Scope

**Does:**
- Read beads state via the `bd` CLI as ground truth
- Score open work items on impact, effort, and risk
- Surface blocked items and dependency chains
- Produce one recommendation per invocation with explicit tradeoff prose
- Acknowledge in-progress work and momentum context

**Does not:**
- Create, modify, or close beads
- Manage sprints, velocity, or estimation
- Integrate with external trackers (GitHub Issues, Linear, Jira)
- Make multi-session plans or roadmaps
- Substitute for strategic planning — it answers "what next in this session," not "where is the project going"

## Direction

- Add configurable scoring weights so teams near a release can dial down risk tolerance without changing the skill logic.
- Surface stale in-progress beads (open but no recent activity) as a distinct warning class — these are the highest-priority invisible tax.
- Explore a compact summary mode for use inside other skills or hooks where only the top recommendation is needed, not the full tradeoff analysis.
