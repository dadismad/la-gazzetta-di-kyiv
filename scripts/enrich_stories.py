#!/usr/bin/env python3
"""
enrich_stories.py — T2 micro-update runner for Living Stories.

Reads current events and narrative setups, computes Jaccard-based evolution
scores against active stories in the registry, appends timeline entries for
matching evidence, spawns sub-threads at high evolution scores, and writes
the aggregate living_stories.json frontend payload.

Pure Python — no LLM calls. Runtime <10s.
"""
from __future__ import annotations
import json, os, re
from datetime import datetime, timezone, timedelta
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENTS_PATH = os.path.join(REPO, 'data', 'normalized', 'events_latest.json')
NARRATIVE_PATH = os.path.join(REPO, 'data', 'processed', 'narrative_intelligence_latest.json')
REGISTRY_PATH = os.path.join(REPO, 'data', 'story_registry.json')
ASSETS_PATH = os.path.join(REPO, 'data', 'publish', 'asset_claims_latest.json')
STORIES_DIR = os.path.join(REPO, 'data', 'stories')
PUBLISH_DIR = os.path.join(REPO, 'data', 'publish')
LIVING_OUT = os.path.join(PUBLISH_DIR, 'living_stories.json')
EDITORIAL_STATE_PATH = os.path.join(REPO, 'data', 'editorial_state.json')

# ── Geography keyword list for extraction ─────────────────────────────────
GEOGRAPHIES = {
    # Countries / regions
    'iran', 'kuwait', 'gulf', 'iraq', 'saudi arabia', 'uae', 'united arab emirates',
    'qatar', 'bahrain', 'oman', 'yemen', 'syria', 'russia', 'ukraine', 'china',
    'beijing', 'shanghai', 'taiwan', 'japan', 'tokyo', 'south korea', 'india',
    'united states', 'us', 'usa', 'america', 'washington', 'new york',
    'europe', 'eu', 'european union', 'brussels', 'germany', 'berlin',
    'france', 'paris', 'uk', 'united kingdom', 'london', 'italy', 'rome',
    'spain', 'madrid', 'netherlands', 'switzerland', 'zurich',
    'turkey', 'ankara', 'israel', 'tel aviv', 'palestine', 'gaza',
    'africa', 'south africa', 'nigeria', 'egypt', 'cairo',
    'brazil', 'brasilia', 'argentina', 'mexico', 'canada', 'ottawa',
    'australia', 'sydney', 'indonesia', 'malaysia', 'singapore',
    'afghanistan', 'pakistan', 'bangladesh', 'thailand', 'vietnam',
    'north korea', 'belarus', 'poland', 'warsaw', 'sweden', 'stockholm',
    'norway', 'denmark', 'finland', 'helsinki', 'kyiv', 'moscow',
    'strait of hormuz', 'persian gulf', 'middle east', 'asia',
    'latin america', 'european union', 'gulf states', 'baltic',
    'california', 'hong kong',
}

# ── Entity and geography extraction ──────────────────────────────────────

def _extract_entities(text: str) -> list[str]:
    """Simple named-entity extraction: grab capitalized phrases (matching
    collect_multisource.py pattern)."""
    entities = []
    # Multi-word capitalized phrases (preferred)
    for m in re.finditer(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', text):
        entities.append(m.group(1).strip())
    # Single-word capitalized nouns (fallback if no multi-word found)
    if not entities:
        for m in re.finditer(r'\b([A-Z][a-z]{3,})\b', text):
            entities.append(m.group(1))
    return entities


def extract_geographies(text: str) -> list[str]:
    """Extract known geography terms from text."""
    lower = text.lower()
    found = []
    for geo in GEOGRAPHIES:
        if geo in lower:
            found.append(geo)
    return found


def jaccard_similarity(a: list[str], b: list[str]) -> float:
    """Jaccard similarity between two lists of strings."""
    if not a and not b:
        return 0.0
    set_a, set_b = set(a), set(b)
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def parse_timestamp(ts: str | None) -> datetime | None:
    """Parse various timestamp formats to datetime."""
    if not ts:
        return None
    # Try ISO format
    try:
        return datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        pass
    # Try RSS pubDate format
    for fmt in [
        '%a, %d %b %Y %H:%M:%S %Z',
        '%a, %d %b %Y %H:%M:%S %z',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S%z',
    ]:
        try:
            return datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc)
        except (ValueError, AttributeError):
            continue
    return None


# ── Story ID generation ──────────────────────────────────────────────────

def derive_story_id(setup_id: str) -> str:
    """Derive a stable story_id from a setup_id."""
    return setup_id  # setup_ids are already stable (n21_oil, n21_macro, etc.)


def derive_sector(setup: dict) -> str:
    """Derive sector from a setup."""
    pid = setup.get('paradigm_pillar', 'multi_pillar')
    sector_map = {
        'china_ascendancy': 'geopolitics',
        'dollar_decline': 'macro',
        'eu_fragmentation': 'geopolitics',
        'abundance_tech': 'tech',
        'blockchain_agentic': 'markets',
    }
    # Also check setup title for sector clues
    title = (setup.get('title', '') + ' ' + ' '.join(setup.get('evidence_titles', []))).lower()
    if 'oil' in title or 'energy' in title or 'drone' in title or 'kuwait' in title:
        return 'geopolitics'
    if 'inflation' in title or 'rates' in title or 'fed' in title or 'ecb' in title:
        return 'macro'
    if 'ai' in title or 'tech' in title or 'google' in title or 'meta' in title:
        return 'tech'
    if 'crypto' in title or 'bitcoin' in title or 'ethereum' in title:
        return 'markets'
    return sector_map.get(pid, 'geopolitics')


# ── Loading helpers ──────────────────────────────────────────────────────

def load_json(path: str) -> dict | None:
    """Load a JSON file (dict only), returning None if it doesn't exist."""
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            result = json.load(f)
            return result if isinstance(result, dict) else None
    except (json.JSONDecodeError, OSError):
        return None


def save_json(path: str, data) -> None:
    """Save data as pretty-printed JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_or_create_registry() -> dict:
    """Load story_registry.json or create an empty one."""
    reg = load_json(REGISTRY_PATH)
    if reg is None:
        reg = {
            'version': 1,
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'story_count': 0,
            'active_count': 0,
            'stories': {},
        }
    return reg


def load_timeline(story_id: str) -> dict:
    """Load a story's timeline file, or create an empty one."""
    path = os.path.join(STORIES_DIR, story_id, 'timeline.json')
    data = load_json(path)
    if data is None:
        data = {'story_id': story_id, 'updates': []}
    return data


def save_timeline(story_id: str, data: dict) -> None:
    """Save a story's timeline file."""
    path = os.path.join(STORIES_DIR, story_id, 'timeline.json')
    save_json(path, data)


# ── Evolution scoring ────────────────────────────────────────────────────

def compute_evolution_score(
    event_titles: list[str],
    story_actors: list[str],
    story_geography: list[str],
    story_pillar: str,
    event_timestamps: list[datetime | None],
    now: datetime,
) -> dict:
    """
    Compute evolution score components.

    Returns dict with:
      - score: float (0-1)
      - actor_match: float
      - geography_match: float
      - pillar_match: float
      - recency: float
    """
    # Extract all entities + geography from event titles
    all_event_entities = set()
    all_event_geos = set()
    for title in event_titles:
        for e in _extract_entities(title):
            all_event_entities.add(e.lower())
        for g in extract_geographies(title):
            all_event_geos.add(g)

    # Actor match: Jaccard between event entities and story actors
    story_actor_set = set(a.lower() for a in story_actors)
    actor_match = jaccard_similarity(list(all_event_entities), list(story_actor_set))

    # Geography match: Jaccard between event geographies and story geographies
    story_geo_set = set(g.lower() for g in story_geography)
    geography_match = jaccard_similarity(list(all_event_geos), list(story_geo_set))

    # Pillar match: 1.0 if story pillar matches (we use best match from event pillar tags)
    # For simplicity, we check if the event pillar aligns — always 0.5 as neutral
    pillar_match = 0.5

    # Recency: highest recency score among events
    recency = 0.0
    for ts in event_timestamps:
        if ts:
            age_hours = (now - ts).total_seconds() / 3600
            r = 1.0 if age_hours < 2 else max(0.0, 1.0 - (age_hours / 48))
            recency = max(recency, r)

    score = (
        actor_match * 0.4
        + geography_match * 0.3
        + pillar_match * 0.2
        + recency * 0.1
    )

    return {
        'score': round(score, 4),
        'actor_match': round(actor_match, 4),
        'geography_match': round(geography_match, 4),
        'pillar_match': round(pillar_match, 4),
        'recency': round(recency, 4),
        'matching_entities': list(all_event_entities & story_actor_set),
        'matching_geographies': list(all_event_geos & story_geo_set),
    }


def generate_update_id(story_id: str, timeline: dict) -> str:
    """Generate a unique, sequential update_id."""
    existing = len(timeline.get('updates', []))
    return f'{story_id}__ev_{existing + 1:03d}'


def age_in_hours(ts_str: str | None, now: datetime) -> float:
    """Calculate age in hours of a timestamp string."""
    ts = parse_timestamp(ts_str)
    if ts is None:
        return 999.0
    return (now - ts).total_seconds() / 3600


# ── Main enrichment logic ────────────────────────────────────────────────

def enrich() -> dict:
    """Main enrichment routine. Returns a summary dict."""
    now = datetime.now(timezone.utc)
    result = {
        'ok': True,
        'stories_updated': 0,
        'sub_threads_spawned': 0,
        'new_stories_created': 0,
        'stories_tagged_stale': 0,
        'errors': [],
    }

    # ── Load all inputs ──────────────────────────────────────────────
    events_data = load_json(EVENTS_PATH)
    narrative_data = load_json(NARRATIVE_PATH)
    asset_claims = load_json(ASSETS_PATH)
    registry = load_or_create_registry()
    editorial_state = load_json(EDITORIAL_STATE_PATH) or {}

    if not events_data or not events_data.get('items'):
        result['ok'] = False
        result['errors'].append('No events data available — skipping enrichment.')
        return result

    if not narrative_data or not narrative_data.get('setups'):
        result['ok'] = False
        result['errors'].append('No narrative setups available — skipping enrichment.')
        return result

    events = events_data['items']
    setups = narrative_data['setups']
    claims = (asset_claims or {}).get('claims', [])

    # Build a lookup from ticker to claim metadata
    claim_by_ticker = {}
    for c in claims:
        ticker = c.get('ticker', '')
        if ticker:
            claim_by_ticker[ticker] = c

    # ── Build event pools per topic ──────────────────────────────────
    # Group events by their tags / topic to match against setups
    events_by_topic = {}
    for ev in events:
        tags = ev.get('tags', []) or []
        topic = (ev.get('topic') or '').lower().strip()
        for t in tags + ([topic] if topic else []):
            if t not in events_by_topic:
                events_by_topic[t] = []
            events_by_topic[t].append(ev)

    # Build a map of existing setups by setup_id for quick lookup
    setup_by_id = {s.get('setup_id'): s for s in setups}

    # ── Ensure data/stories/ directory exists ────────────────────────
    os.makedirs(STORIES_DIR, exist_ok=True)

    # ── Process each active story in the registry ────────────────────
    stories = registry.get('stories', {})
    updated_story_ids = set()

    for story_id, story in list(stories.items()):
        if story.get('status') == 'resolved':
            continue  # Skip resolved stories

        setup_id = story.get('original_setup_id', '')
        setup = setup_by_id.get(setup_id, {})

        # Gather current event pool for this story's topic
        topic = setup_id.replace('n21_', '') if setup_id else ''
        relevant_events = events_by_topic.get(topic, [])
        if not relevant_events:
            # Fall back to matching by any entity overlap
            for ev in events:
                ev_text = f"{ev.get('title', '')} {ev.get('text', '')}"
                for actor in story.get('actors', []):
                    if actor.lower() in ev_text.lower():
                        relevant_events.append(ev)
                        break

        if not relevant_events:
            # Check staleness — if no relevant events found for 48h
            last_updated = story.get('last_updated')
            if last_updated and age_in_hours(last_updated, now) >= 48:
                story['status'] = 'stable'
                story['status_reason'] = 'No new evidence for 48 hours — marked stable'
                result['stories_tagged_stale'] += 1
                updated_story_ids.add(story_id)
            continue

        # Extract event titles and timestamps
        event_titles = [ev.get('title', '') for ev in relevant_events if ev.get('title')]
        event_pub_times = [
            parse_timestamp(ev.get('published_at')) for ev in relevant_events
        ]

        # Compute evolution score
        evo = compute_evolution_score(
            event_titles=event_titles,
            story_actors=story.get('actors', []),
            story_geography=story.get('geography', []),
            story_pillar=story.get('paradigm_pillar', 'multi_pillar'),
            event_timestamps=event_pub_times,
            now=now,
        )

        score = evo['score']
        timeline = load_timeline(story_id)
        existing_updates = timeline.get('updates', [])

        # Determine if there's genuinely novel evidence not already in timeline
        existing_summaries = set(
            u.get('summary', '') for u in existing_updates
        )
        novel_events = [
            ev for ev in relevant_events
            if ev.get('title', '') not in existing_summaries
        ]

        if score >= 0.6 and novel_events:
            # ── Append timeline entry ────────────────────────────
            best_event = novel_events[0]
            update_id = generate_update_id(story_id, timeline)

            # Build summary from matching events
            matched_titles = [ev.get('title', '') for ev in novel_events[:3]]
            summary = f"Evolution match (score={score:.2f}): {'; '.join(matched_titles[:2])}"

            entry = {
                'update_id': update_id,
                'timestamp': now.isoformat(),
                'type': 'evidence',
                'summary': summary[:300],
                'source_url': best_event.get('url', ''),
                'source_id': best_event.get('source_id', ''),
                'evolution_score': score,
                'actor_match': evo['actor_match'],
                'geography_match': evo['geography_match'],
            }

            # Attach asset delta if we have a matching claim
            asset_claim = story.get('asset_claim', {})
            if asset_claim and asset_claim.get('ticker'):
                ticker = asset_claim['ticker']
                claim_info = claim_by_ticker.get(ticker)
                if claim_info:
                    entry['asset_delta'] = {
                        'ticker': ticker,
                        'price_before': asset_claim.get('current_price', ''),
                        'price_after': claim_info.get('price_target', ''),
                        'change_pct': claim_info.get('narrative_driven_pct', ''),
                    }

            existing_updates.append(entry)
            timeline['updates'] = existing_updates
            save_timeline(story_id, timeline)

            # Update story registry fields
            story['last_updated'] = now.isoformat()
            story['update_count'] = story.get('update_count', 0) + 1
            story['evidence_count'] = story.get('evidence_count', 0) + len(novel_events)
            story['source_count'] = story.get('source_count', 0) + len(
                set(ev.get('source_id', '') for ev in novel_events if ev.get('source_id'))
            )
            story['status'] = 'evolving'
            story['status_reason'] = f'New evidence: {summary[:120]}'
            story['evolution_score_current'] = score
            if not story.get('evolution_score_peak') or score > story['evolution_score_peak']:
                story['evolution_score_peak'] = score

            # Update current_headline if we have a better one
            if best_event.get('title'):
                story['current_headline'] = best_event['title']

            updated_story_ids.add(story_id)
            result['stories_updated'] += 1

            # ── Spawn sub-thread if score >= 0.85 ───────────────
            if score >= 0.85:
                spawn_angle = matched_titles[0][:60] if matched_titles else 'new_angle'
                # Sanitize spawn_angle for thread_id
                safe_angle = re.sub(r'[^a-z0-9_]', '_', spawn_angle.lower().replace(' ', '_'))
                thread_id = f'{story_id}__{safe_angle}'

                # Check if this thread already exists
                existing_threads = story.get('thread_ids', [])
                if thread_id not in existing_threads:
                    existing_threads.append(thread_id)
                    story['thread_ids'] = existing_threads

                    # Mark the parent update as spawning a sub-thread
                    entry['type'] = 'thesis_update'  # Upgrade type
                    entry['thread_id'] = thread_id
                    entry['summary'] = (
                        f"Sub-thread spawned (score={score:.2f}): {matched_titles[0][:120]}"
                    )

                    # Create an initial entry in the sub-thread's timeline
                    sub_timeline_path = os.path.join(
                        STORIES_DIR, story_id, f'thread_{safe_angle}.json'
                    )
                    sub_timeline = {
                        'story_id': story_id,
                        'thread_id': thread_id,
                        'updates': [{
                            'update_id': f'{thread_id}__init',
                            'timestamp': now.isoformat(),
                            'type': 'subtopic_spawn',
                            'summary': f'Sub-thread spawned from {story_id}: {matched_titles[0][:200]}',
                            'source_url': best_event.get('url', ''),
                        }],
                    }
                    os.makedirs(os.path.join(STORIES_DIR, story_id), exist_ok=True)
                    save_json(sub_timeline_path, sub_timeline)

                    result['sub_threads_spawned'] += 1

                    # Save timeline again with updated entry
                    save_timeline(story_id, timeline)

            # Update last_updated in the entry (it was already added)
            # Re-save timeline with potentially updated entry
            save_timeline(story_id, timeline)

        elif score < 0.6:
            # Check time since last meaningful update
            last_updated = story.get('last_updated')
            if last_updated and age_in_hours(last_updated, now) >= 48:
                story['status'] = 'stable'
                story['status_reason'] = f'Evolution score {score:.2f} (below 0.6 threshold) for 48h — marked stable'
                updated_story_ids.add(story_id)
                result['stories_tagged_stale'] += 1

    # ── Seed new stories from setups that don't exist in registry ──
    for setup in setups:
        setup_id = setup.get('setup_id', '')
        if not setup_id:
            continue
        sid = derive_story_id(setup_id)
        if sid not in stories:
            # Extract actor entities and geographies from evidence
            actors = setup.get('actors', [])
            all_text = ' '.join(setup.get('evidence_titles', []) + [setup.get('title', '')])
            geos = extract_geographies(all_text)

            headline = setup.get('title', '') or 'New story'
            # Truncate headline for readability
            if len(headline) > 120:
                headline = headline[:117] + '...'

            stories[sid] = {
                'story_id': sid,
                'first_seen': now.isoformat(),
                'last_updated': now.isoformat(),
                'status': 'new',
                'status_reason': 'Seeded from narrative intelligence setup',
                'update_count': 1,
                'original_setup_id': setup_id,
                'original_headline': setup.get('title', '')[:200],
                'current_headline': headline,
                'sector': derive_sector(setup),
                'paradigm_pillar': setup.get('paradigm_pillar', 'multi_pillar'),
                'actors': actors,
                'geography': geos,
                'thread_ids': [f'{sid}__main'],
                'primary_thread_id': f'{sid}__main',
                'evidence_count': len(setup.get('evidence_titles', [])),
                'source_count': 1,
                'invalidation_triggers': setup.get('invalidation_triggers', []),
                'confidence': setup.get('confidence', 0.5),
                'paradigm_implications': [],
                'capital_flow_implication': '',
                'asset_claim': {},
                'image_url': setup.get('image_url') or None,
                'evolution_score_current': 0.0,
                'evolution_score_peak': 0.0,
            }

            # Create initial timeline entry
            timeline = {'story_id': sid, 'updates': [{
                'update_id': f'{sid}__ev_001',
                'timestamp': now.isoformat(),
                'type': 'evidence',
                'summary': f'Initial broadcast — {headline[:200]}',
                'source_url': '',
                'evolution_score': 0.0,
            }]}
            save_timeline(sid, timeline)

            updated_story_ids.add(sid)
            result['new_stories_created'] += 1

            # Link asset claim if available
            # Try to find a matching claim by looking at the setup title
            setup_text = (setup.get('title', '') + ' ' + ' '.join(setup.get('evidence_titles', []))).lower()
            for claim in claims:
                ticker = claim.get('ticker', '')
                direction = claim.get('direction', '')
                price_target = claim.get('price_target', '')
                ndp = claim.get('narrative_driven_pct', 0)
                story_text = (claim.get('story_headline', '') + ' ' + claim.get('crowd_belief', '')).lower()
                # Check if there's any keyword overlap between the setup and claim
                overlap_keywords = set(setup_text.split()) & set(story_text.split())
                if len(overlap_keywords) >= 3:
                    stories[sid]['asset_claim'] = {
                        'ticker': ticker,
                        'direction': direction,
                        'price_target': price_target,
                        'initial_price': price_target,  # Simplified
                        'current_price': price_target,
                        'narrative_driven_pct': ndp,
                        'last_updated': now.isoformat(),
                    }
                    break

    # ── Update registry metadata ────────────────────────────────────
    updated_count = sum(
        1 for s in stories.values() if s.get('status') not in ('resolved',)
    )
    registry['version'] = 1
    registry['updated_at'] = now.isoformat()
    registry['story_count'] = len(stories)
    registry['active_count'] = updated_count
    registry['stories'] = stories
    save_json(REGISTRY_PATH, registry)

    # ── Build living_stories.json ───────────────────────────────────
    living = {
        'version': 1,
        'generated_at': now.isoformat(),
        'last_full_cycle': editorial_state.get('last_full_cycle', ''),
        'next_micro_update': '',
        'next_full_cycle': '',
        'active_stories': [],
        'archived_stories': [],
    }

    for sid, story in stories.items():
        timeline_data = load_timeline(sid)
        updates = timeline_data.get('updates', [])
        latest = updates[-1] if updates else {}
        latest_summary = latest.get('summary', story.get('current_headline', ''))[:200]

        entry = {
            'story_id': sid,
            'headline': story.get('current_headline', ''),
            'one_line_summary': story.get('status_reason', '')[:200],
            'sector': story.get('sector', ''),
            'paradigm_pillar': story.get('paradigm_pillar', ''),
            'status': story.get('status', 'new'),
            'last_updated': story.get('last_updated', ''),
            'update_count': story.get('update_count', 0),
            'evidence_count': story.get('evidence_count', 0),
            'thread_count': len(story.get('thread_ids', [])),
            'actors': story.get('actors', [])[:4],
            'geography': story.get('geography', []),
            'evolution_score_current': story.get('evolution_score_current', 0.0),
            'latest_update_summary': latest_summary,
            'image_url': story.get('image_url'),
            'has_live_updates': story.get('status') == 'evolving',
        }

        # Add asset claim if present
        ac = story.get('asset_claim', {})
        if ac and ac.get('ticker'):
            entry['asset_claim'] = {
                'ticker': ac['ticker'],
                'target': ac.get('price_target', ''),
                'narrative_driven_pct': ac.get('narrative_driven_pct', 0),
            }

        if story.get('status') == 'resolved':
            living['archived_stories'].append(entry)
        else:
            living['active_stories'].append(entry)

    # Sort active stories by last_updated desc
    living['active_stories'].sort(
        key=lambda s: s.get('last_updated', ''), reverse=True
    )
    save_json(LIVING_OUT, living)

    # ── Update editorial_state ──────────────────────────────────────
    if result['stories_updated'] > 0 or result['new_stories_created'] > 0:
        editorial_state['last_micro_update'] = now.isoformat()
        editorial_state['micro_update_skips'] = editorial_state.get('micro_update_skips', 0)
        editorial_state['active_story_ids'] = list(stories.keys())
        editorial_state['story_registry_version'] = 1
        save_json(EDITORIAL_STATE_PATH, editorial_state)

    return result


def main():
    result = enrich()
    print(json.dumps(result, indent=2))
    # Exit with error code if enrichment failed
    if not result.get('ok'):
        import sys
        sys.exit(1)


if __name__ == '__main__':
    main()
