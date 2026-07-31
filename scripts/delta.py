#!/usr/bin/env python3
"""Burrows's Delta: does this text come from the same hand as the reference?

    python delta.py --reference work/ref/ --test draft/
    python delta.py --reference work/ref/ --test draft/ --out work/delta.json

Builds a profile from the most frequent words of the reference — function
words, mostly — expresses each chapter as z-scores against the reference's
own distribution, and measures distance from the reference centroid.

**Why this and not fingerprint.py.** Surface statistics (sentence length,
paragraph length, dialogue ratio) largely track the *source* text's
structure, which survives translation regardless of who translated it.
Measured on a real two-volume pair, they failed to separate a different
translator's draft from the genuine second volume — on several metrics the
foreign draft scored *closer* to the reference than the real continuation
did. Function-word frequencies do separate them: 13% of same-translator
chapters crossed the threshold against 97% of the other translator's.

Use `fingerprint.py` to find *which axis* diverges and by how much. Use
this to answer whether the text reads as the same hand at all.

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

WORD = re.compile(r"[^\W\d_]+", re.UNICODE)

# Short fragments — title pages, dividers, epigraphs — have unstable word
# distributions and distort both the profile and the scores.
MIN_WORDS = 500


def load(target: Path, glob: str) -> list[tuple[str, list[str]]]:
    files = [target] if target.is_file() else [p for p in sorted(target.rglob(glob)) if p.is_file()]
    if not files and target.is_dir():
        files = [p for p in sorted(target.rglob("*.txt")) if p.is_file()]
    out = []
    for p in files:
        words = [w.lower() for w in WORD.findall(p.read_text(encoding="utf-8", errors="replace"))]
        if len(words) >= MIN_WORDS:
            out.append((p.stem, words))
    return out


def profile(chapters: list[tuple[str, list[str]]], n_mfw: int) -> list[str]:
    counter: Counter[str] = Counter()
    for _, words in chapters:
        counter.update(words)
    return [w for w, _ in counter.most_common(n_mfw)]


def freqs(words: list[str], mfw: list[str]) -> list[float]:
    n = len(words)
    c = Counter(words)
    return [c[w] / n for w in mfw]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reference", type=Path, required=True, help="the translation to match")
    ap.add_argument("--test", type=Path, required=True, help="the text under examination")
    ap.add_argument("--mfw", type=int, default=150, help="most frequent words to profile on (default 150)")
    ap.add_argument("--sigma", type=float, default=2.0, help="threshold in sigmas of reference spread")
    ap.add_argument("--glob", default="*.txt")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    ref = load(args.reference, args.glob)
    test = load(args.test, args.glob)
    if len(ref) < 5:
        print(f"error: need 5+ reference chapters of {MIN_WORDS}+ words, found {len(ref)}",
              file=sys.stderr)
        return 2
    if not test:
        print(f"error: no test chapters of {MIN_WORDS}+ words found", file=sys.stderr)
        return 2

    mfw = profile(ref, args.mfw)
    ref_freqs = [freqs(w, mfw) for _, w in ref]
    mu = [statistics.mean(col) for col in zip(*ref_freqs)]
    sd = [statistics.pstdev(col) or 1e-9 for col in zip(*ref_freqs)]

    def distance(words: list[str]) -> float:
        f = freqs(words, mfw)
        return statistics.mean(abs((f[i] - mu[i]) / sd[i]) for i in range(len(mfw)))

    ref_d = [distance(w) for _, w in ref]
    threshold = statistics.mean(ref_d) + args.sigma * statistics.pstdev(ref_d)
    scored = sorted(((distance(w), name) for name, w in test), reverse=True)
    over = [(d, n) for d, n in scored if d > threshold]

    print(f"profiled on {len(mfw)} most frequent words of {len(ref)} reference chapters\n")
    print(f"{'':<26}{'mean':>8}{'median':>9}")
    print("-" * 43)
    print(f"{'reference (itself)':<26}{statistics.mean(ref_d):>8.3f}{statistics.median(ref_d):>9.3f}")
    print(f"{'test':<26}{statistics.mean(d for d, _ in scored):>8.3f}"
          f"{statistics.median([d for d, _ in scored]):>9.3f}")
    print(f"\nthreshold (reference mean + {args.sigma}σ): {threshold:.3f}")
    print(f"test chapters above it: {len(over)} of {len(scored)} ({len(over) / len(scored):.0%})")

    if over:
        print("\nfurthest from the reference:")
        for d, name in over[:12]:
            print(f"  {d:6.3f}  {name}")
        if len(over) > 12:
            print(f"  … and {len(over) - 12} more")

    share = len(over) / len(scored)
    print()
    if share < 0.20:
        print("reads as the same hand — a same-translator volume scores in this range")
    elif share < 0.50:
        print("mixed: some chapters diverge. Inspect the listed ones individually")
    else:
        print("reads as a different hand")
    print("\nThis is one measurement on function-word frequency. It says nothing")
    print("about accuracy, only about whose habits the prose carries.")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps({
            "mfw": len(mfw),
            "reference_chapters": len(ref),
            "reference_mean": round(statistics.mean(ref_d), 4),
            "threshold": round(threshold, 4),
            "test_chapters": len(scored),
            "test_mean": round(statistics.mean(d for d, _ in scored), 4),
            "above_threshold": len(over),
            "share_above": round(share, 4),
            "per_chapter": [{"chapter": n, "delta": round(d, 4)} for d, n in scored],
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n-> {args.out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
