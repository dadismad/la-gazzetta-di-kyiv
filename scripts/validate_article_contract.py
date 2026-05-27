#!/usr/bin/env python3
import json
import sys
from pathlib import Path

REQUIRED_KEYS = [
    "headline",
    "claim",
    "market_belief",
    "what_is_happening",
    "actors",
    "incentives",
    "second_order_effects",
    "cross_asset_effects",
    "retail_positioning",
    "invalidation_conditions",
    "confidence",
    "narrative_tags",
]


def fail(msg: str):
    print(json.dumps({"ok": False, "error": msg}))
    sys.exit(1)


def main() -> int:
    if len(sys.argv) < 2:
        fail("usage: validate_article_contract.py <article_json>")

    p = Path(sys.argv[1])
    if not p.exists():
        fail(f"file not found: {p}")

    obj = {}
    try:
        loaded = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            fail("article json must be an object")
        obj = loaded
    except Exception as e:
        fail(f"invalid json: {e}")

    missing = [k for k in REQUIRED_KEYS if k not in obj]
    if missing:
        fail(f"missing keys: {missing}")

    if obj.get("confidence") not in {"Low", "Medium", "High"}:
        fail("confidence must be one of Low/Medium/High")

    list_fields = [
        "actors",
        "incentives",
        "second_order_effects",
        "cross_asset_effects",
        "retail_positioning",
        "invalidation_conditions",
        "narrative_tags",
    ]
    for f in list_fields:
        if not isinstance(obj.get(f), list) or len(obj[f]) == 0:
            fail(f"field '{f}' must be a non-empty array")

    print(json.dumps({"ok": True, "validated": str(p)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
