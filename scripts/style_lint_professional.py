#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

BANNED = [
    r"\bat its core\b",
    r"\bthe real question is\b",
    r"\bpivotal\b",
    r"\bobservers note\b",
    r"\bexperts say\b",
]

REQUIRED_PATTERNS = {
    "causal_phrase": r"\b(because|therefore|which means)\b",
    "time_window": r"\b(24–72h|24-72h|this week|next quarter|next month)\b",
}


def run(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    violations = []

    for pat in BANNED:
        if re.search(pat, text, flags=re.IGNORECASE):
            violations.append({"type": "banned_phrase", "pattern": pat})

    for name, pat in REQUIRED_PATTERNS.items():
        if not re.search(pat, text, flags=re.IGNORECASE):
            violations.append({"type": "missing_required", "pattern": name})

    actors = re.findall(r"## Actors\n([\s\S]*?)(\n##|$)", text)
    if actors:
        actor_lines = [ln for ln in actors[0][0].splitlines() if ln.strip().startswith("-")]
        if len(actor_lines) < 2:
            violations.append({"type": "actors", "detail": "fewer than 2 actor bullets"})

    return {
        "ok": len(violations) == 0,
        "violations": violations,
        "file": str(path),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "usage: style_lint_professional.py <file>"}))
        raise SystemExit(2)
    p = Path(sys.argv[1])
    if not p.exists():
        print(json.dumps({"ok": False, "error": f"missing file: {p}"}))
        raise SystemExit(2)
    result = run(p)
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["ok"] else 1)
