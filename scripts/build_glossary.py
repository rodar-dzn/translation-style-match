#!/usr/bin/env python3
"""Surface candidate terms and, given a bitext, the target spans that
probably render them.

    python build_glossary.py --source work/src/ --target work/ref/ \
        --out work/candidates.md

    # monolingual mode: candidates only, no aligned spans
    python build_glossary.py --source work/src/ --out work/candidates.md

    # confirm one suspected rendering against the corpus
    python build_glossary.py --target work/ref/ --confirm "term"

The script does NOT decide renderings. It narrows the search to a handful
of paragraph pairs so a person can read them and decide. Alignment is
positional and approximate — treat every pair as a lead, not a result.

Stdlib only.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

WORD = re.compile(r"[^\W\d_]+", re.UNICODE)

# A capitalized word not at sentence start, or a run of them. re.M matters:
# without it, ^ anchors to the whole string and every paragraph-initial word
# is reported as a proper noun.
PROPER = re.compile(
    r"(?<![.!?…»\"'”]\s)(?<!^)\b([A-ZÀ-ÞŠŽ][\w'’-]+(?:\s+[A-ZÀ-ÞŠŽ][\w'’-]+)*)",
    re.M,
)

STOP = {
    "the", "and", "but", "for", "with", "from", "that", "this", "have", "has",
    "was", "were", "been", "would", "could", "should", "there", "their", "what",
    "when", "where", "which", "while", "will", "your", "you", "not", "are",
    "his", "her", "him", "she", "they", "them", "then", "than", "into", "upon",
    "said", "one", "all", "out", "who", "him", "its", "our", "him",
}


def load(target: Path, glob: str = "*.txt") -> list[tuple[str, str]]:
    """Return (chapter_name, text) in sorted order."""
    if target.is_file():
        return [(target.stem, target.read_text(encoding="utf-8", errors="replace"))]
    return [
        (p.stem, p.read_text(encoding="utf-8", errors="replace"))
        for p in sorted(target.rglob(glob)) if p.is_file()
    ]


def paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n|\n", text) if p.strip()]


def candidates(texts: list[str], min_count: int, max_count: int) -> list[tuple[str, int]]:
    """Proper nouns and coinages: capitalized mid-sentence, or rare long words."""
    counter: Counter[str] = Counter()
    for text in texts:
        for m in PROPER.finditer(text):
            phrase = m.group(1).strip()
            if len(phrase) < 3:
                continue
            if phrase.lower() in STOP:
                continue
            counter[phrase] += 1

    # hyphenated and unusually long lowercase words are often coinages
    for text in texts:
        for w in WORD.findall(text):
            if len(w) > 9 and w.islower():
                counter[w] += 1
        for w in re.findall(r"\b[a-z]+-[a-z]+\b", text):
            counter[w] += 1

    return sorted(
        ((t, n) for t, n in counter.items() if min_count <= n <= max_count),
        key=lambda kv: (-kv[1], kv[0].lower()),
    )


def build_index(chapters: list[tuple[str, str]]) -> list[tuple[str, int, str]]:
    """Flat list of (chapter, paragraph_index, paragraph_text)."""
    flat = []
    for name, text in chapters:
        for i, p in enumerate(paragraphs(text)):
            flat.append((name, i, p))
    return flat


def aligned_window(src_pos: int, n_src: int, n_tgt: int, width: int) -> tuple[int, int]:
    """Proportional alignment with a fixed window.

    Deliberately crude. Chapter counts differ, translations merge and split
    paragraphs, and front matter shifts everything. The window exists so a
    reader can find the real match nearby, not so the script can claim one.
    """
    if n_src == 0:
        return 0, 0
    centre = int(src_pos * n_tgt / n_src)
    return max(0, centre - width), min(n_tgt, centre + width + 1)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", type=Path, help="extracted source-language text")
    ap.add_argument("--target", type=Path, help="extracted reference-translation text")
    ap.add_argument("--out", type=Path, help="write candidate report here")
    ap.add_argument("--confirm", help="search the target corpus for this string and quit")
    ap.add_argument("--min-count", type=int, default=2, help="ignore terms rarer than this")
    ap.add_argument("--max-count", type=int, default=400, help="ignore terms commoner than this")
    ap.add_argument("--limit", type=int, default=150, help="max candidates to report")
    ap.add_argument("--window", type=int, default=12, help="alignment window, in paragraphs")
    args = ap.parse_args()

    # ---- confirm mode ----------------------------------------------------
    if args.confirm:
        if not args.target:
            print("error: --confirm needs --target", file=sys.stderr)
            return 2
        needle = args.confirm.lower()
        hits = 0
        for name, idx, par in build_index(load(args.target)):
            if needle in par.lower():
                hits += 1
                print(f"{name} ¶{idx}: {par[:200]}")
                if hits >= 40:
                    print("… (truncated)")
                    break
        print(f"\n{hits} hit(s) for {args.confirm!r}")
        if not hits:
            print("not found — try morphological variants before recording this as NEW")
        return 0

    if not args.source:
        print("error: --source is required unless using --confirm", file=sys.stderr)
        return 2

    src_chapters = load(args.source)
    if not src_chapters:
        print(f"error: no .txt files under {args.source}", file=sys.stderr)
        return 1

    terms = candidates([t for _, t in src_chapters], args.min_count, args.max_count)[: args.limit]
    src_index = build_index(src_chapters)
    tgt_index = build_index(load(args.target)) if args.target else []

    lines = [
        "# Glossary candidates",
        "",
        f"Source: `{args.source}` — {len(src_index)} paragraphs, {len(terms)} candidates shown.",
    ]
    if tgt_index:
        lines.append(
            f"Target: `{args.target}` — {len(tgt_index)} paragraphs. "
            f"Aligned spans are positional guesses within a ±{args.window}-paragraph window; "
            "read them, do not trust them."
        )
    else:
        lines.append("No target corpus given — candidates only. Use `--confirm` to check renderings one by one.")
    lines += [
        "",
        "For each term: find the rendering in the aligned spans, then record it in "
        "`GLOSSARY.md` as CANON with its citation. Only mark NEW after searching "
        "for plausible variants and finding nothing.",
        "",
        "---",
        "",
    ]

    for term, count in terms:
        lines.append(f"## {term}  \n`{count}` occurrences")
        lines.append("")

        first = next(((n, i, p) for n, i, p in src_index if term in p), None)
        if first:
            name, idx, par = first
            lines.append(f"**source** · {name} ¶{idx}")
            lines.append(f"> {par[:300]}{'…' if len(par) > 300 else ''}")
            lines.append("")

            if tgt_index:
                pos = next((k for k, (n, i, _) in enumerate(src_index) if n == name and i == idx), 0)
                lo, hi = aligned_window(pos, len(src_index), len(tgt_index), args.window)
                lines.append(f"**target ¶{lo}–{hi}**")
                lines.append("")
                for n, i, p in tgt_index[lo:hi]:
                    lines.append(f"> `{n} ¶{i}` {p[:200]}{'…' if len(p) > 200 else ''}")
                lines.append("")
        lines.append("---")
        lines.append("")

    report = "\n".join(lines)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
        print(f"{len(terms)} candidates -> {args.out}")
        if not tgt_index:
            print("no target corpus: run again with --target for aligned spans")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
