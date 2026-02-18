# internext

Work prioritization for Claude Code.

## What This Does

internext reads your project's beads state and recommends what to work on next. Not a neutral menu of options — an opinionated recommendation with explicit tradeoff analysis.

Each candidate gets scored on three axes: impact (does it unblock other work? does it build capability?), effort (30 minutes or multi-session?), and risk (mechanical task or rabbit hole?). Items that block other items get an impact bonus — a P2 that unblocks three P1s is worth more than a standalone P1.

There's a built-in completion bias: finishing in-progress work almost always beats starting new work, because the switching cost of abandoned context is real and consistently underestimated.

## Installation

```bash
/plugin install internext
```

## Usage

```
/internext:next-work
```

Or ask naturally:

```
"what should I work on next?"
"prioritize my backlog for this session"
```

The skill reads from `bd ready`, `bd list`, and `bd stats` to build its picture of the project state, then delivers 3-5 scored options with a clear recommendation.
