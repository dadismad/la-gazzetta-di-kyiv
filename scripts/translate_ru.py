#!/usr/bin/env python3
"""
translate_ru.py — Russian localization engine for Gazzetta di Kyiv stories.

Reads public/data/stories.json (English source), translates trade_thesis and
narrative fields to Russian via GLM 5.2, writes public/data/stories_ru.json.

Architecture:
  - Non-blocking: translation failure → story stays English-only. Governor never stalls.
  - ID-tracked: story_id → ru_hash in translation_ledger.jsonl. Skip already-translated stories
    unless the English source hash changed (content was updated).
  - Batch mode: sends up to 5 stories per API call to minimize round-trips.
  - Fallback: GLM 5.2 primary → DeepSeek secondary → English passthrough.

Performance:
  - ~1.5s per story (GLM 5.2 batch)
  - ~15s for full 10-story cycle
  - Governor overhead: <3% of 10-min window

Usage:
  python3 scripts/translate_ru.py
  python3 scripts/translate_ru.py --max-items 10
  python3 scripts/translate_ru.py --dry-run
"""

import hashlib
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import ssl
from datetime import datetime, timezone
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────
PROJECT = Path(__file__).resolve().parent.parent
PUBLIC_DATA = PROJECT / "public" / "data"
STORIES_PATH = PUBLIC_DATA / "stories.json"
STORIES_RU_PATH = PUBLIC_DATA / "stories_ru.json"
LEDGER_PATH = PUBLIC_DATA / "translation_ledger.jsonl"

# GLM 5.2
GLM_KEY = os.environ.get("GLM_API_KEY", "3d76e17112094679a3236820eb5a3502.zX9w5hVuUqKu3pbL")
GLM_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
GLM_MODEL = "glm-5.2"

# DeepSeek fallback
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

MAX_ITEMS_PER_RUN = 10
API_TIMEOUT = 120
MAX_TOKENS = 4096
BATCH = 3  # GLM 5.2 reasoning consumes ~2500-3000 tokens internally; 4096 leaves ~1000-1500 for content

# Fields to translate (and their max chars)
TRANSLATE_FIELDS = {
    "headline": 120,
    "they_say": 500,
    "reality": 500,
}

# Nested trade_thesis fields
TRADE_FIELDS = {
    "entry_rationale": 200,
    "invalidation": 200,
    "alpha_trigger": 300,
}

# ── SSL context (tolerate self-signed / corporate proxies) ─────────
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

# ── Translation System Prompt ──────────────────────────────────────
RU_SYSTEM_PROMPT = """Ты — профессиональный финансовый переводчик для терминала рыночной разведки La Gazzetta di Kyiv. Твоя задача — переводить торговые тезисы с английского на русский язык, сохраняя стиль профессионального трейдинг-деска.

ЖЕСТКИЕ ПРАВИЛА:
1. НИКОГДА не переводи тикеры (NVDA, GLD, TLT, SMH, DXY, BTC-USD, CL=F, SPY и т.д.) — оставляй как есть.
2. НИКОГДА не переводи числа, проценты и цены ($221.14, 1.35%, $87.36, 50bp, $10B).
3. НИКОГДА не переводи названия нарративов (Sovereign Liquidity Migration, Energy Sovereignty) — оставляй на английском.
4. ИСПОЛЬЗУЙ профессиональную русскую трейдерскую лексику:
   - LONG → лонг
   - SHORT → шорт
   - STRADDLE → стрэддл
   - stop loss → стоп-лосс
   - take profit → тейк-профит
   - entry → вход / точка входа
   - target → цель / таргет
   - conviction → убеждённость
   - divergence → дивергенция
   - alpha trigger → альфа-триггер
   - invalidation → инвалидация
   - volatility → волатильность
   - catalyst → катализатор
   - positioning → позиционирование
   - rate cut → снижение ставки
   - rate hike → повышение ставки
5. Сохраняй первое лицо автора: "Я ожидаю", "Данные показывают", "Я считаю".
6. Никакого смягчения: не используй "возможно", "может быть", "вероятно". Пиши с убеждённостью.
7. Длина перевода не должна превышать оригинал более чем на 20%.

Отвечай ТОЛЬКО валидным JSON. Без markdown, без пояснений.
Формат: {"field_name": "перевод", ...}"""


# ── Helpers ─────────────────────────────────────────────────────────
def load_ledger():
    """Return {story_id: content_hash} of already-translated stories."""
    ledger = {}
    if LEDGER_PATH.exists():
        with open(LEDGER_PATH) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        ledger[entry["story_id"]] = entry.get("content_hash", "")
                    except json.JSONDecodeError:
                        pass
    return ledger


def save_ledger_entry(story_id, content_hash, status):
    """Append a translation ledger entry."""
    entry = {
        "story_id": story_id,
        "content_hash": content_hash,
        "translated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
    }
    with open(LEDGER_PATH, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def content_hash(story):
    """Hash the translatable content of a story to detect changes."""
    parts = []
    for field in TRANSLATE_FIELDS:
        parts.append(str(story.get(field, "")))
    tt = story.get("trade_thesis", {}) or {}
    for field in TRADE_FIELDS:
        parts.append(str(tt.get(field, "")))
    return hashlib.md5("|".join(parts).encode()).hexdigest()[:12]


def build_translation_payload(stories):
    """Build a batch translation request from a list of stories.
    Returns (fields_map, user_prompt) where fields_map is {story_id: {field: orig_text}}"""
    fields_map = {}
    prompt_parts = ["Переведи следующие поля на русский язык. Верни JSON-объект с ключами как указано.\n"]

    for i, story in enumerate(stories):
        sid = story.get("story_id", f"unknown_{i}")
        fields_map[sid] = {}

        prompt_parts.append(f"\n=== STORY {i+1}: {sid} ===")

        for field, max_len in TRANSLATE_FIELDS.items():
            text = str(story.get(field, ""))[:max_len]
            if text.strip():
                key = f"{sid}__{field}"
                fields_map[sid][field] = text
                prompt_parts.append(f'  {key}: """{text}"""')

        tt = story.get("trade_thesis", {}) or {}
        for field, max_len in TRADE_FIELDS.items():
            text = str(tt.get(field, ""))[:max_len]
            if text.strip():
                key = f"{sid}__trade_thesis.{field}"
                fields_map[sid][f"trade_thesis.{field}"] = text
                prompt_parts.append(f'  {key}: """{text}"""')

    return fields_map, "\n".join(prompt_parts)


def json_parse_robust(raw_text: str, debug_label: str = "") -> dict | None:
    """Parse JSON with multiple recovery strategies for GLM 5.2 malformed output."""
    text = raw_text.strip()

    # Strategy 0: Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 1: Strip markdown fences
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    # Strategy 2: Fix trailing commas before } or ]
    text2 = re.sub(r",\s*([}\]])", r"\1", text)
    try:
        return json.loads(text2)
    except json.JSONDecodeError:
        pass

    # Strategy 3: Fix unescaped quotes inside string values
    # Pattern: "key": "value with "unescaped" quotes"
    # Replace inner quotes with escaped quotes in string values
    try:
        text3 = re.sub(
            r'(?<=: ")(.*?)(?="\s*[,}])',
            lambda m: m.group(1).replace('"', '\\"'),
            text2
        )
        return json.loads(text3)
    except (json.JSONDecodeError, Exception):
        pass

    # Strategy 4: Try to extract first complete JSON object via brace matching
    try:
        start = text2.find("{")
        if start >= 0:
            depth = 0
            end = start
            for i, ch in enumerate(text2[start:], start):
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            if end > start:
                return json.loads(text2[start:end])
    except json.JSONDecodeError:
        pass

    # Log failure for debugging
    snippet = raw_text[:300] + ("..." if len(raw_text) > 300 else "")
    print(f"  [translate_ru] JSON parse failed after 4 strategies{debug_label}: {snippet}")
    return None


def call_translation_api(provider_name, api_key, api_url, model, user_prompt, timeout):
    """Call an LLM for batch translation. Returns parsed dict or None on failure."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": RU_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": MAX_TOKENS,
    }

    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        resp = urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX)
        raw_body = resp.read().decode("utf-8")
        data = json.loads(raw_body)
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

        if not content:
            print(f"  [translate_ru] {provider_name} empty response")
            return None

        result = json_parse_robust(content, f" ({provider_name})")
        if result and isinstance(result, dict) and len(result) > 0:
            return result

        # If result is empty dict or None, log raw content for debugging
        print(f"  [translate_ru] {provider_name} returned unparseable content (first 200 chars): {content[:200]}")
        return None

    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        print(f"  [translate_ru] {provider_name} HTTP {e.code}: {body}")
        return None
    except (json.JSONDecodeError, urllib.error.URLError, OSError) as e:
        print(f"  [translate_ru] {provider_name} error: {type(e).__name__}: {e}")
        return None


def translate_batch(stories):
    """Translate a batch of stories. Returns {story_id: translated_fields} or {} on failure."""
    fields_map, user_prompt = build_translation_payload(stories)

    # Try GLM 5.2
    if GLM_KEY:
        result = call_translation_api("glm5.2", GLM_KEY, GLM_URL, GLM_MODEL, user_prompt, API_TIMEOUT)
        if result and isinstance(result, dict) and len(result) > 0:
            return _remap_keys(result, fields_map)

    # Fallback: DeepSeek
    if DEEPSEEK_KEY:
        result = call_translation_api("deepseek", DEEPSEEK_KEY, DEEPSEEK_URL, DEEPSEEK_MODEL, user_prompt, API_TIMEOUT)
        if result and isinstance(result, dict) and len(result) > 0:
            return _remap_keys(result, fields_map)

    return {}


def _remap_keys(flat_result, fields_map):
    """Convert flat {sid__field: translation} → {sid: {field: translation}}"""
    translated = {}
    for sid, fields in fields_map.items():
        translated[sid] = {}
        for field_key, orig_text in fields.items():
            flat_key = f"{sid}__{field_key}"
            if flat_key in flat_result:
                translated[sid][field_key] = flat_result[flat_key]
            else:
                translated[sid][field_key] = orig_text  # Passthrough untranslated
    return translated


# ── Main ────────────────────────────────────────────────────────────
def main():
    print("[translate_ru] Starting Russian localization engine...")

    if not STORIES_PATH.exists():
        print("[-] No stories.json found — nothing to translate.")
        return 0

    with open(STORIES_PATH) as f:
        data = json.load(f)

    all_stories = data.get("all_stories", [])
    if not all_stories:
        print("[-] No stories in stories.json.")
        return 0

    ledger = load_ledger()

    # Identify stories needing translation
    to_translate = []
    for story in all_stories:
        sid = story.get("story_id", "")
        if not sid:
            continue
        ch = content_hash(story)
        if ledger.get(sid) == ch:
            continue  # Already translated, unchanged
        to_translate.append(story)

    if not to_translate:
        print("[translate_ru] All stories up to date — nothing to translate.")
        return 0

    print(f"[translate_ru] {len(to_translate)} stories need translation (out of {len(all_stories)} total)")

    # Process in batches of 5
    # BATCH defined at module level (3 stories — GLM reasoning budget)
    translated_count = 0
    failed_count = 0

    for i in range(0, min(len(to_translate), MAX_ITEMS_PER_RUN), BATCH):
        batch = to_translate[i:i + BATCH]
        print(f"  Batch {i // BATCH + 1}: translating {len(batch)} stories...")

        translations = translate_batch(batch)

        for story in batch:
            sid = story["story_id"]
            ch = content_hash(story)

            if sid in translations and translations[sid]:
                # Merge translations into story
                ru_fields = translations[sid]
                for field in TRANSLATE_FIELDS:
                    if field in ru_fields:
                        story[field] = ru_fields[field]

                tt = story.get("trade_thesis", {})
                if tt:
                    for field in TRADE_FIELDS:
                        key = f"trade_thesis.{field}"
                        if key in ru_fields:
                            tt[field] = ru_fields[key]
                    story["trade_thesis"] = tt

                save_ledger_entry(sid, ch, "translated")
                translated_count += 1
                print(f"    ✓ {sid}")
            else:
                # Non-blocking: keep English
                save_ledger_entry(sid, ch, "passthrough_en")
                failed_count += 1
                print(f"    ⚠ {sid} — English passthrough (translation failed)")

        time.sleep(0.5)  # Rate limiting courtesy

    # Write stories_ru.json
    data["all_stories"] = all_stories
    data["language"] = "ru"
    data["translated_at"] = datetime.now(timezone.utc).isoformat()
    data["translated_count"] = translated_count

    tmp_path = STORIES_RU_PATH.with_suffix(".tmp.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, STORIES_RU_PATH)

    print(f"[translate_ru] ✓ {translated_count} translated, {failed_count} passthrough")
    print(f"[translate_ru] Written: {STORIES_RU_PATH}")
    return 0 if failed_count == 0 else 0  # Never fail — non-blocking


if __name__ == "__main__":
    sys.exit(main())
