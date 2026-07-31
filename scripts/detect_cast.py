#!/usr/bin/env python3
"""Find the recurring cast by reading dialogue tags.

    python detect_cast.py work/ref/ --profile profile.json --out cast.md
    python detect_cast.py work/ref/ --profile profile.json --append GLOSSARY.md

A name that appears in the narration half of a dialogue paragraph is almost
always a speaker. That holds regardless of language, given the speech
marker, so no list of speech verbs is needed.

This unblocks `split_dialogue.py`, which needs a cast and previously had to
be handed one by hand. It finds who speaks; it does not settle how their
names should be rendered — that is glossary work, and every row it writes
is marked for review.

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# A capitalized word, optionally hyphenated or apostrophised: compound
# names are single names, and splitting them yields two half-people who
# each look like a minor character.
CAP = re.compile(r"\b([^\W\d_]+(?:[-'’][^\W\d_]+)*)", re.UNICODE)

# Sentence-initial words are capitalized for grammatical reasons, not
# because they are names, so they are excluded by position rather than by
# a stop-list — which would have to be per-language.
SENTENCE_START = re.compile(r"(?:^|[.!?…]\s+|[:;]\s+)$")


def is_upper(word: str) -> bool:
    return bool(word) and word[0].isupper() and not word.isupper()


def split_paragraph(par: str, marker: str) -> list[str]:
    """Narration segments of a dialogue paragraph."""
    parts = par.split(marker)
    return [p.strip() for i, p in enumerate(parts) if i >= 2 and i % 2 == 0 and p.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", type=Path)
    ap.add_argument("--profile", type=Path, default=Path("profile.json"))
    ap.add_argument("--glob", default="*.txt")
    ap.add_argument("--top", type=int, default=30, help="cast size to report (default 30)")
    ap.add_argument("--min-count", type=int, default=5, help="ignore names rarer than this")
    ap.add_argument("--out", type=Path, help="write a glossary table here")
    ap.add_argument("--append", type=Path, help="append rows to an existing GLOSSARY.md")
    args = ap.parse_args()

    if not args.profile.exists():
        print(f"error: profile {args.profile} not found", file=sys.stderr)
        return 2
    cfg = json.loads(args.profile.read_text(encoding="utf-8"))
    marker = cfg.get("dialogue", {}).get("marker", "")
    if not marker:
        print("error: profile has no dialogue.marker", file=sys.stderr)
        return 2

    files = [args.target] if args.target.is_file() else [p for p in sorted(args.target.rglob(args.glob)) if p.is_file()]
    if not files:
        print(f"error: no files matching {args.glob!r} under {args.target}", file=sys.stderr)
        return 2

    in_tags: Counter[str] = Counter()
    anywhere: Counter[str] = Counter()
    dialogue_paragraphs = 0

    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        for par in (p.strip() for p in re.split(r"\n\s*\n|\n", text) if p.strip()):
            for m in CAP.finditer(par):
                if is_upper(m.group(1)) and not SENTENCE_START.search(par[: m.start()][-3:]):
                    anywhere[m.group(1)] += 1
            if not par.startswith(marker):
                continue
            dialogue_paragraphs += 1
            for seg in split_paragraph(par, marker):
                for m in CAP.finditer(seg):
                    w = m.group(1)
                    if is_upper(w) and not SENTENCE_START.search(seg[: m.start()][-3:]):
                        in_tags[w] += 1

    if not in_tags:
        print("no names found in dialogue tags — check that the marker is right", file=sys.stderr)
        return 1

    # A speaker is a name that turns up in tags disproportionately often.
    cast = []
    for name, tag_count in in_tags.most_common(args.top * 4):
        if tag_count < args.min_count:
            continue
        total = anywhere.get(name, tag_count)
        cast.append((name, tag_count, total, tag_count / total if total else 0))
    cast.sort(key=lambda r: -r[1])
    cast = cast[: args.top]

    rows = ["| Source | Canonical | Reject | Status | Citation / pattern |",
            "|---|---|---|---|---|"]
    for name, tag_count, total, ratio in cast:
        rows.append(f"|  | {name} |  | REVIEW | {tag_count} in tags / {total} total |")
    table = "\n".join(rows)

    print(f"{dialogue_paragraphs:,} dialogue paragraphs from {len(files)} files\n")
    print(f"{'name':<24}{'in tags':>9}{'total':>8}{'share':>8}")
    print("-" * 49)
    for name, tag_count, total, ratio in cast:
        print(f"{name:<24}{tag_count:>9}{total:>8}{ratio:>7.0%}")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(f"## Characters\n\n{table}\n", encoding="utf-8")
        print(f"\n-> {args.out}")

    if args.append:
        existing = args.append.read_text(encoding="utf-8") if args.append.exists() else ""
        if "<!-- detected cast -->" in existing:
            print(f"\n{args.append} already carries a detected cast — left alone")
        else:
            with args.append.open("a", encoding="utf-8") as fh:
                fh.write(f"\n\n<!-- detected cast -->\n## Characters (detected)\n\n"
                         f"Found by `detect_cast.py` from dialogue tags. Every row is "
                         f"`REVIEW`: the detector found who speaks, not how the name "
                         f"should be rendered. Confirm each against the corpus, fill the "
                         f"Source column, and change the status.\n\n{table}\n")
            print(f"\nappended {len(cast)} rows to {args.append}")

    print("\nWho speaks is detected. How each name should be rendered is not —")
    print("every row is marked REVIEW until a person confirms it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
