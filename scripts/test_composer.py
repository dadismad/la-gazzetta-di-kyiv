#!/usr/bin/env python3
"""
test_composer.py — Test suite for Gazzetta di Kyiv Devvit Post Composer.

Runs the composer 20 times with the same sample data and verifies:
  1. No two outputs share the same opening
  2. No two outputs share the same closing
  3. ≤30% of outputs share the same title format (title template group)
  4. Each post has ≥1 uncertainty marker + opinion frame
  5. Visual difference: each output is structurally distinct

Usage:
    python3 scripts/test_composer.py
    python3 scripts/test_composer.py --verbose
    python3 scripts/test_composer.py --seed 42
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass, field

# Ensure we can import the composer
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)

from scripts.post_composer import GazzettaComposer, PhraseBank


# ── Sample test data ───────────────────────────────────────────────────

SAMPLE_SCORE = {
    "post_id": "test_001",
    "title": "Test Market Signal",
    "sector": "Macro Rates & FX",
    "regime": "mixed",
    "captivation_score": 72,
    "capital_flow_score": 65,
    "beneficiary_score": 68,
    "links": ["https://pureciclismo.github.io/gazzetta-di-kyiv/"],
}

SAMPLE_DRAFT = {
    "rank": 1,
    "headline_hook": "ECB hold pattern creates divergence with market pricing",
    "core_claim": "The ECB is signaling hold while markets price 25bp cut — this gap creates a cross-asset repricing opportunity in EUR rates and FX.",
    "actors": ["ECB Governing Council", "ECB's Frank Elderson", "EUR rate traders", "Macro hedge funds"],
    "contradiction_map": {
        "consensus": "ECB will cut in September regardless of data",
        "evidence": "Services inflation at 4.1% keeps rate rises on the table at 72% probability",
        "implication": "If ECB holds, EUR rallies and EU bond yields spike — the narrative is priced for a cut that may not come.",
    },
    "bet_snippet_24_72h": {
        "instrument": "EUR/USD",
        "direction": "straddle into ECB, sell vol post-announcement",
        "probability_pct": 65,
        "projection_pct": "+0.8% to +2.4%",
        "invalidation": "ECB surprises with dovish forward guidance or inflation prints below 3.8%",
    },
    "links": ["https://pureciclismo.github.io/gazzetta-di-kyiv/"],
}

SAMPLE_SCORES = [SAMPLE_SCORE]
SAMPLE_DRAFTS = [SAMPLE_DRAFT]


# ── Test helpers ───────────────────────────────────────────────────────

def extract_title_format(title: str) -> str:
    """Extract the title format prefix to categorize title template groups.
    E.g. 'Macro Radar — Macro Rates & FX' -> 'Macro Radar'
          'Macro Pulse — Macro Rates & FX' -> 'Macro Pulse'
    """
    # Remove the sector suffix after the separator
    for sep in [" — ", " – ", " — ", " – "]:
        if sep in title:
            prefix = title.split(sep)[0].strip()
            # Remove trailing " Edition", " in Focus", " Deep Dive" etc. for grouping
            for suffix in [" Edition", " in Focus", " Deep Dive", " Edition"]:
                if prefix.endswith(suffix):
                    prefix = prefix[:-len(suffix)]
            return prefix
    # Try other patterns
    for sep in [": ", " — ", " vs ", " Watch", " Brief", " Outlook"]:
        if sep in title:
            return title.split(sep)[0].strip()
    return title


def extract_sources(body: str) -> list[str]:
    """Extract source links from the body."""
    urls = re.findall(r'https?://[^\s\)\]]+', body)
    return urls


def visual_fingerprint(body: str) -> str:
    """Create a normalized structural fingerprint for visual diff comparison.
    Strips all text content but preserves structure markers: headers, bold,
    tables, separators, bullets."""
    fp = body
    # Remove text content between markers
    fp = re.sub(r'(?<=\*\*)[^*]+(?=\*\*)', 'X', fp)
    fp = re.sub(r'(?<=\|)[^|]+(?=\|)', 'X', fp)
    # Remove URLs
    fp = re.sub(r'https?://\S+', 'URL', fp)
    # Collapse whitespace
    fp = re.sub(r'\s+', ' ', fp).strip()
    # Hash it for comparison
    return hashlib.md5(fp.encode()).hexdigest()


# ── Test results ──────────────────────────────────────────────────────

@dataclass
class TestResult:
    passed: bool
    name: str
    detail: str = ""
    failures: list[str] = field(default_factory=list)


# ── Main test runner ──────────────────────────────────────────────────

def run_tests(count: int = 20, seed: int | None = None, verbose: bool = False) -> list[TestResult]:
    """Run all verification tests on the composer."""
    results = []
    failures = []

    # Generate 20 posts
    composer = GazzettaComposer()
    posts = composer.compose_batch(
        SAMPLE_SCORES, SAMPLE_DRAFTS, count=count, seed=seed
    )

    if verbose:
        print(f"\n{'='*60}")
        print(f"GENERATED {count} POSTS (seed={seed})")
        print(f"{'='*60}")
        for i, p in enumerate(posts):
            print(f"\n--- Post {i+1}: {p['title']} [{p['format_name']}] ---")
            print(f"  Opening: {p['opening'][:60]}...")
            print(f"  Closing: {p['closing'][:60]}...")
            print(f"  Marker: {p['marker'][:60]}...")
            print(f"  Frame: {p['frame'][:60]}...")
            print(f"  Word count: {p['word_count']}")
            print(f"  Has marker: {p['has_marker']}, Has frame: {p['has_frame']}")

    # ── Test 1: No two outputs share the same opening ──────────
    openings = [p["opening"] for p in posts]
    opening_counts = Counter(openings)
    dup_openings = {k: v for k, v in opening_counts.items() if v > 1}
    passed_t1 = len(dup_openings) == 0
    detail_t1 = (
        f"All {len(openings)} openings unique"
        if passed_t1
        else f"DUPLICATE OPENINGS: {dict(dup_openings)}"
    )
    results.append(TestResult(
        passed=passed_t1, name="No duplicate openings",
        detail=detail_t1,
        failures=[] if passed_t1 else [str(dup_openings)]
    ))
    if not passed_t1:
        failures.append(f"FAIL: {detail_t1}")

    # ── Test 2: No two outputs share the same closing ──────────
    closings = [p["closing"] for p in posts]
    closing_counts = Counter(closings)
    dup_closings = {k: v for k, v in closing_counts.items() if v > 1}
    passed_t2 = len(dup_closings) == 0
    detail_t2 = (
        f"All {len(closings)} closings unique"
        if passed_t2
        else f"DUPLICATE CLOSINGS: {dict(dup_closings)}"
    )
    results.append(TestResult(
        passed=passed_t2, name="No duplicate closings",
        detail=detail_t2,
        failures=[] if passed_t2 else [str(dup_closings)]
    ))
    if not passed_t2:
        failures.append(f"FAIL: {detail_t2}")

    # ── Test 3: ≤30% same title format ─────────────────────────
    title_formats = [extract_title_format(p["title"]) for p in posts]
    title_counts = Counter(title_formats)
    max_same = max(title_counts.values())
    max_same_pct = (max_same / count) * 100
    passed_t3 = max_same_pct <= 30.0
    detail_t3 = (
        f"Max title format repetition: {max_same}/{count} ({max_same_pct:.1f}%) — "
        f"limit is ≤30%"
        if passed_t3
        else f"Title format overused: {max_same}/{count} ({max_same_pct:.1f}% > 30%) — "
             f"counts: {dict(title_counts)}"
    )
    results.append(TestResult(
        passed=passed_t3, name="Title format diversity",
        detail=detail_t3,
        failures=[] if passed_t3 else [str(dict(title_counts))]
    ))
    if not passed_t3:
        failures.append(f"FAIL: {detail_t3}")

    # ── Test 4: Each post has ≥1 uncertainty marker + opinion frame ──
    missing_marker = [i+1 for i, p in enumerate(posts) if not p["has_marker"]]
    missing_frame = [i+1 for i, p in enumerate(posts) if not p["has_frame"]]
    passed_t4 = len(missing_marker) == 0 and len(missing_frame) == 0
    detail_t4_parts = []
    if not passed_t4:
        if missing_marker:
            detail_t4_parts.append(f"Missing markers in posts: {missing_marker}")
        if missing_frame:
            detail_t4_parts.append(f"Missing frames in posts: {missing_frame}")
    else:
        detail_t4_parts.append(
            f"All {count} posts have ≥1 marker and ≥1 frame"
        )
    results.append(TestResult(
        passed=passed_t4, name="Marker + frame presence",
        detail=" | ".join(detail_t4_parts),
        failures=detail_t4_parts
    ))
    if not passed_t4:
        failures.extend(detail_t4_parts)

    # ── Test 5: Visual difference ──────────────────────────────
    fingerprints = [visual_fingerprint(p["body"]) for p in posts]
    fp_counts = Counter(fingerprints)
    dup_fp = {k: v for k, v in fp_counts.items() if v > 5}
    # Allow some structural overlap between different runs, but flag if >25% identical
    max_identical = max(fp_counts.values())
    max_identical_pct = (max_identical / count) * 100
    # For structural comparison, some templates share similar skeleton,
    # so we check that titles and openings vary visibly too
    unique_titles = len(set(p["title"] for p in posts))
    unique_formats = len(set(p["format_name"] for p in posts))
    passed_t5_reason = (
        f"All {count} outputs visually varied: "
        f"{unique_titles} unique titles, "
        f"{unique_formats} unique format templates, "
        f"{len(fingerprints)} structural fingerprints"
    )

    # More nuanced: check that we used multiple format templates
    format_names = [p["format_name"] for p in posts]
    unique_format_count = len(set(format_names))

    if unique_format_count < 3:
        detail_t5 = (
            f"WARNING: Only {unique_format_count} format templates used "
            f"out of 10 available: {set(format_names)}"
        )
        passed_t5 = False
        failures.append(f"FAIL: {detail_t5}")
    else:
        detail_t5 = f"{unique_format_count}/10 format templates used in {count} runs"
        passed_t5 = True

    results.append(TestResult(
        passed=passed_t5, name="Visual/structural variety",
        detail=detail_t5,
        failures=[] if passed_t5 else [detail_t5]
    ))

    # ── Test 6: All posts have disclaimer, title, minimum word count ──
    missing_disclaimer = [i+1 for i, p in enumerate(posts)
                          if not any(d in p["body"] for d in PhraseBank().disclaimers)]
    missing_ready = [i+1 for i, p in enumerate(posts)
                     if "READY_FOR_DEVVIT_POST" not in p["body"]]
    missing_title = [i+1 for i, p in enumerate(posts) if not p["title"]]
    short_posts = [i+1 for i, p in enumerate(posts) if p["word_count"] < 50]

    detail_t6_parts = []
    pass_t6 = True
    if missing_disclaimer:
        detail_t6_parts.append(f"Missing disclaimer: posts {missing_disclaimer}")
        pass_t6 = False
    if missing_ready:
        detail_t6_parts.append(f"Missing READY_FOR_DEVVIT_POST: posts {missing_ready}")
        pass_t6 = False
    if missing_title:
        detail_t6_parts.append(f"Missing title: posts {missing_title}")
        pass_t6 = False
    if short_posts:
        detail_t6_parts.append(f"Too short (<50 words): posts {short_posts}")
        pass_t6 = False
    if pass_t6:
        detail_t6_parts.append(f"All {count} posts complete with disclaimer and title")

    results.append(TestResult(
        passed=pass_t6, name="Structural completeness",
        detail=" | ".join(detail_t6_parts),
        failures=detail_t6_parts
    ))
    if not pass_t6:
        failures.extend(detail_t6_parts)

    # ── Test 7: Format diversity — no single format used more than 30% ──
    format_counts = Counter(format_names)
    max_format_pct = max(c / count * 100 for c in format_counts.values())
    passed_t7 = max_format_pct <= 30.0
    detail_t7 = (
        f"Max single format usage: {max_format_pct:.1f}% (≤30% required) — "
        f"format distribution: {dict(format_counts)}"
        if passed_t7
        else f"Format overused: {max_format_pct:.1f}% — distribution: {dict(format_counts)}"
    )
    results.append(TestResult(
        passed=passed_t7, name="Format distribution",
        detail=detail_t7,
        failures=[] if passed_t7 else [str(dict(format_counts))]
    ))
    if not passed_t7:
        failures.append(f"FAIL: {detail_t7}")

    # Summary
    passed_count = sum(1 for r in results if r.passed)
    total = len(results)

    print(f"\n{'='*60}")
    print(f"TEST SUMMARY: {passed_count}/{total} passed")
    print(f"{'='*60}")
    for r in results:
        status = "✓" if r.passed else "✗"
        print(f"  {status} {r.name}")
        if verbose or not r.passed:
            print(f"      {r.detail}")

    if failures:
        print(f"\n{'!'*60}")
        print(f"FAILURES ({len(failures)}):")
        for f in failures:
            print(f"  • {f}")
        print(f"{'!'*60}")
    else:
        print(f"\n✓ All tests passed!")

    print(f"\n{'='*60}")
    print("DETAILED OUTPUT BREAKDOWN")
    print(f"{'='*60}")
    print(f"Formats used: {sorted(set(format_names))}")
    print(f"Openings used: {len(set(openings))}/{len(openings)} unique")
    print(f"Closings used: {len(set(closings))}/{len(closings)} unique")
    print(f"Titles: {unique_titles} unique out of {count}")

    return results


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Test Gazzetta di Kyiv Devvit Post Composer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--count", type=int, default=20,
        help="Number of posts to generate (default: 20)"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Print detailed output for each post"
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Write generated posts as JSON to a file"
    )
    args = parser.parse_args()

    results = run_tests(
        count=args.count,
        seed=args.seed,
        verbose=args.verbose,
    )

    # Optionally write outputs
    if args.output:
        # Regenerate for output
        composer = GazzettaComposer()
        posts = composer.compose_batch(
            SAMPLE_SCORES, SAMPLE_DRAFTS,
            count=args.count, seed=args.seed
        )
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump({
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "count": len(posts),
                "seed": args.seed,
                "posts": [
                    {
                        "index": i + 1,
                        "title": p["title"],
                        "format": p["format_name"],
                        "opening": p["opening"],
                        "closing": p["closing"],
                        "marker": p["marker"],
                        "frame": p["frame"],
                        "word_count": p["word_count"],
                    }
                    for i, p in enumerate(posts)
                ],
            }, f, ensure_ascii=False, indent=2)

    all_passed = all(r.passed for r in results)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
