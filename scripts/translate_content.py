#!/usr/bin/env python3
"""translate_content.py — Generate Russian translations of stories.json.

Translates user-facing fields: headline, they_say, reality, thesis.
Uses DeepSeek API if key available, otherwise copies English as placeholder.
Output: data/stories_ru.json → synced to site/data/

Run as part of pipeline_chain.sh after build_site.py.
"""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(PROJECT, "data")

FIELDS_TO_TRANSLATE = [
    "headline", "they_say", "reality", "thesis",
    "actionable_trade", "portfolio_implication",
]

FLOW_FIELDS = ["headline", "projected", "positioning"]


def get_api_key():
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if key:
        return key
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith("DEEPSEEK_API_KEY="):
                return line.strip().split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def translate_via_api(texts):
    """Batch translate via DeepSeek API."""
    api_key = get_api_key()
    if not api_key:
        print("  [translate] No API key, using English as fallback", file=sys.stderr)
        return {}

    items = "\n\n---\n\n".join(f"[{i}] {t[:400]}" for i, t in enumerate(texts))
    prompt = (
        "Translate these financial/market texts from English to Russian. "
        "Keep tickers ($SPX, $NVDA), numbers, and % unchanged. "
        "Return ONLY a JSON array: [\"translation1\", \"translation2\", ...]\n\n" + items
    )

    try:
        payload = json.dumps({
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 4000,
        }).encode()

        req = urllib.request.Request(
            "https://api.deepseek.com/v1/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            content = result["choices"][0]["message"]["content"]
            match = re.search(r"\[.*\]", content, re.DOTALL)
            if match:
                return {i: t for i, t in enumerate(json.loads(match.group()))}
    except Exception as e:
        print(f"  [translate] API error: {e}", file=sys.stderr)

    return {}


def translate_story(story, trans):
    """Apply translations to a story dict."""
    ru = dict(story)
    sid = story.get("story_id", "")
    for field in FIELDS_TO_TRANSLATE:
        key = f"{sid}:{field}"
        if key in trans and ru.get(field):
            ru[field] = trans[key]
    cf = ru.get("capital_flow", {})
    if isinstance(cf, dict):
        for field in FLOW_FIELDS:
            key = f"{sid}:cf:{field}"
            if key in trans and cf.get(field):
                cf[field] = trans[key]
        ru["capital_flow"] = cf
    return ru


def main():
    stories_path = os.path.join(DATA, "stories.json")
    if not os.path.exists(stories_path):
        print(json.dumps({"ok": False, "error": "no stories.json"}))
        return

    with open(stories_path) as f:
        src = json.load(f)

    all_stories = []
    if src.get("lead"):
        all_stories.append(src["lead"])
    all_stories.extend(src.get("stories", []))

    # Collect texts
    texts, keys = [], []
    for s in all_stories:
        sid = s.get("story_id", "")
        for field in FIELDS_TO_TRANSLATE:
            if s.get(field):
                texts.append(str(s[field])[:400])
                keys.append(f"{sid}:{field}")
        cf = s.get("capital_flow", {})
        if isinstance(cf, dict):
            for field in FLOW_FIELDS:
                if cf.get(field):
                    texts.append(str(cf[field])[:400])
                    keys.append(f"{sid}:cf:{field}")

    # Translate
    translations = translate_via_api(texts) if texts else {}
    trans_map = {keys[i]: translations[i] for i in translations if i < len(keys)}

    # Build RU version
    ru = dict(src)
    if ru.get("lead"):
        ru["lead"] = translate_story(ru["lead"], trans_map)
    ru["stories"] = [translate_story(s, trans_map) for s in ru.get("stories", [])]
    ru["generated_at"] = datetime.now(timezone.utc).isoformat()
    ru["language"] = "ru"

    # Write
    for subdir in ["", "site/"]:
        out = os.path.join(PROJECT, subdir, "data", "stories_ru.json")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w") as f:
            json.dump(ru, f, indent=2, ensure_ascii=False)

    # Copy flows as RU (same structure, just mark language)
    flows_path = os.path.join(DATA, "flows.json")
    ru_flows = None
    if os.path.exists(flows_path):
        with open(flows_path) as f:
            ru_flows = dict(json.load(f))
        ru_flows["language"] = "ru"
        for subdir in ["", "site/"]:
            out = os.path.join(PROJECT, subdir, "data", "flows_ru.json")
            with open(out, "w") as f:
                json.dump(ru_flows, f, indent=2, ensure_ascii=False)

    result = {
        "ok": True,
        "texts": len(texts),
        "translated": len(translations),
        "stories_ru": os.path.join(DATA, "stories_ru.json"),
        "flows_ru": os.path.join(DATA, "flows_ru.json") if ru_flows else None,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
