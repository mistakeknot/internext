#!/usr/bin/env python3
"""Rank top skills by recent usage from ~/.claude/audit.log.

Reads the PostToolUse invocation log (schema v1 — see
Sylveste/docs/contracts/audit-log-schema.md) and emits the top N most
frequently used skills, optionally filtered by project type.

Usage:
  top-skills.py [--n=3] [--days=30] [--project-type=<type>]

Project-type detection (when --project-type is omitted):
  - pyproject.toml in CWD          → python
  - package.json in CWD            → typescript|javascript
  - Cargo.toml in CWD              → rust
  - go.mod in CWD                  → go
  - .beads/ + multiple plugin.json → sylveste
  - else                           → generic

When a project type is set, ranking is weighted toward skills observed
in past sessions where the CWD matched that project type. Currently
that's a heuristic: we just emphasize the most-recent N days harder
since project-type-tagged history isn't in the v1 schema yet.

If the audit log doesn't exist (PostToolUse hook not installed), exits
with a one-line stderr message and a non-zero status. Callers should
treat that as "no recommendation available" rather than an error.
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

AUDIT_LOG = Path.home() / ".claude" / "audit.log"
AUDIT_ROTATED = Path.home() / ".claude" / "audit.log.1.gz"


def detect_project_type(cwd: Path) -> str:
    if (cwd / "pyproject.toml").exists():
        return "python"
    if (cwd / "Cargo.toml").exists():
        return "rust"
    if (cwd / "go.mod").exists():
        return "go"
    if (cwd / "package.json").exists():
        return "typescript"
    if (cwd / ".beads").exists():
        # Heuristic: a project with .beads/ AND interverse/ subdir is sylveste
        if (cwd / "interverse").exists():
            return "sylveste"
        return "beads-project"
    return "generic"


def stream_entries(cutoff_ms: float):
    """Yield JSON entries from current + rotated logs that are after cutoff."""
    for source in (AUDIT_LOG, AUDIT_ROTATED):
        if not source.exists():
            continue
        opener = gzip.open if source.suffix == ".gz" else open
        try:
            with opener(source, "rt", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        e = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    ts_iso = e.get("ts", "")
                    if not ts_iso:
                        continue
                    try:
                        ts_ms = (
                            time.mktime(time.strptime(ts_iso[:19], "%Y-%m-%dT%H:%M:%S"))
                            * 1000
                        )
                    except (ValueError, TypeError):
                        continue
                    if ts_ms < cutoff_ms:
                        continue
                    yield e
        except OSError:
            continue


def rank_skills(days: int, recency_weight: float = 2.0) -> list[tuple[str, float]]:
    """Return [(skill_name, score), ...] sorted by score desc.

    Score = invocation count, with a recency multiplier — invocations
    in the last `days/4` days count for `recency_weight` extra. This
    favors skills that have been used *recently*, not just heavily in
    the distant past.
    """
    now_ms = time.time() * 1000
    cutoff_ms = now_ms - days * 86400 * 1000
    recent_cutoff_ms = now_ms - (days / 4) * 86400 * 1000

    counts: dict[str, float] = defaultdict(float)
    for e in stream_entries(cutoff_ms):
        if e.get("tool") != "Skill":
            continue
        name = e.get("name") or ""
        if not name:
            continue
        try:
            ts_ms = time.mktime(time.strptime(e["ts"][:19], "%Y-%m-%dT%H:%M:%S")) * 1000
        except (KeyError, ValueError):
            continue
        weight = recency_weight if ts_ms >= recent_cutoff_ms else 1.0
        counts[name] += weight

    return sorted(counts.items(), key=lambda kv: -kv[1])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", type=int, default=3, help="number of skills to surface")
    ap.add_argument("--days", type=int, default=30, help="window for ranking")
    ap.add_argument(
        "--project-type",
        default="",
        help="override project-type detection (currently informational only)",
    )
    ap.add_argument(
        "--json",
        action="store_true",
        help="emit JSON instead of human-readable text",
    )
    args = ap.parse_args()

    cwd = Path.cwd()
    project_type = args.project_type or detect_project_type(cwd)

    if not AUDIT_LOG.exists():
        msg = (
            "no audit log at ~/.claude/audit.log — install the PostToolUse "
            "hook via Sylveste-xn5 to start recording skill invocations"
        )
        if args.json:
            print(json.dumps({"error": msg, "project_type": project_type}))
        else:
            print(f"top-skills: {msg}", file=sys.stderr)
        return 1

    ranked = rank_skills(args.days)
    top = ranked[: args.n]

    if args.json:
        print(
            json.dumps(
                {
                    "project_type": project_type,
                    "window_days": args.days,
                    "skills": [{"name": n, "score": round(s, 1)} for n, s in top],
                }
            )
        )
        return 0

    if not top:
        print(f"top-skills: no Skill invocations recorded in the last {args.days} days")
        return 0

    line = f"top skills for {project_type} (last {args.days}d): " + ", ".join(
        f"{n} ({int(s)})" for n, s in top
    )
    print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
