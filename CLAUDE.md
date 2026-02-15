# internext

Work prioritization and next-task analysis for Claude Code — tradeoff-aware recommendations from project state.

## Overview

1 skill, 0 agents, 0 commands, 0 hooks. Companion plugin for Clavain.

## Quick Commands

```bash
python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"  # Manifest check
ls skills/*/SKILL.md | wc -l  # Should be 1
```

## Design Decisions (Do Not Re-Ask)

- Reads beads state (bd CLI) as the source of truth for work items
- Scores options on impact/effort/risk axes with explicit tradeoff prose
- Opinionated recommendations with completion bias — finishing > starting
- Extracted as a companion plugin because prioritization is a product concern, not core engineering discipline
