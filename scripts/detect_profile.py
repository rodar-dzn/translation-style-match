#!/usr/bin/env python3
"""Read a reference translation and write profile.json from what it does.

    python detect_profile.py work/ref/ --out profile.json

Phase 1 used to mean counting dash variants by hand. This does the counting
and records the evidence alongside each decision, so the numbers behind a
choice stay visible and arguable.

It settles what is countable: script, dialogue marker, quote characters,
ellipsis form, foreign-token candidates. It cannot settle register, voice
or neologism formation — those still need a person and the style guide.

Every detection carries its counts. Where the margin is thin the tool says
so rather than picking silently.

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

WORD = re.compile(r"[^\W\d_]+", re.UNICODE)

DASHES = {"–": "U+2013 en dash", "—": "U+2014 em dash", "―": "U+2015 horizontal bar", "-": "U+002D hyphen"}
QUOTE_PAIRS = [("«", "»"), ("„", "“"), ("„", "”"), ("“", "”"), ("」", "「"), ('"', '"')]
OPENERS = ["«", "„", "“", "「", '"', "»"]

_SCRIPT: dict[str, str] = {}


def script_of(ch: str) -> str:
    if ch not in _SCRIPT:
        try:
            first = unicodedata.name(ch).split()[0]
        except ValueError:
            first = "OTHER"
        _SCRIPT[ch] = first if first in ("LATIN", "CYRILLIC", "GREEK", "ARABIC", "HEBREW", "CJK", "HIRAGANA", "KATAKANA") else "OTHER"
    return _SCRIPT[ch]


def detect(paragraphs: list[str], text: str, top_foreign: int) -> dict:
    ev: dict = {}

    # -- script ------------------------------------------------------------
    words = WORD.findall(text)
    sc: Counter[str] = Counter()
    for w in words[:60000]:
        for c in w:
            s = script_of(c)
            if s != "OTHER":
                sc[s] += 1
    main_script = sc.most_common(1)[0][0] if sc else "LATIN"
    ev["script"] = {"detected": main_script, "counts": dict(sc.most_common(4))}

    # -- dialogue marker ---------------------------------------------------
    starts = Counter()
    for p in paragraphs:
        for d in DASHES:
            if p.startswith(d):
                starts[d] += 1
                break
        else:
            for o in OPENERS:
                if p.startswith(o):
                    starts[o] += 1
                    break

    marker, marker_note = "", ""
    if starts:
        ranked = starts.most_common()
        marker = ranked[0][0]
        top = ranked[0][1]
        second = ranked[1][1] if len(ranked) > 1 else 0
        if second and top / max(second, 1) < 3:
            marker_note = (f"thin margin: {marker!r}={top} vs {ranked[1][0]!r}={second} — "
                           f"confirm by reading before trusting this")
    ev["dialogue_marker"] = {
        "detected": marker,
        "counts": {f"{k} ({DASHES.get(k, 'quote')})": v for k, v in starts.most_common(6)},
        "note": marker_note,
    }

    # -- quote pair --------------------------------------------------------
    pair_counts = {f"{a}{b}": text.count(a) for a, b in QUOTE_PAIRS if text.count(a)}
    quote_pair: list[str] = []
    for a, b in QUOTE_PAIRS:
        if text.count(a) and (a, b) != ('"', '"'):
            quote_pair = [a, b]
            break
    ev["quote_pair"] = {"detected": quote_pair, "counts": pair_counts}

    # -- quotes inside speech ---------------------------------------------
    quotes_in_speech = False
    if marker and quote_pair:
        dlg = [p for p in paragraphs if p.startswith(marker)]
        with_q = sum(1 for p in dlg if quote_pair[0] in p)
        share = with_q / len(dlg) if dlg else 0
        quotes_in_speech = share > 0.15
        ev["quotes_in_speech"] = {
            "detected": quotes_in_speech,
            "share_of_dialogue_paragraphs": round(share, 4),
            "note": "above 15% is treated as a convention rather than occasional quotation",
        }

    # -- ellipsis ----------------------------------------------------------
    uni, dots = text.count("…"), len(re.findall(r"(?<!\.)\.\.\.(?!\.)", text))
    ev["ellipsis"] = {"detected": "…" if uni >= dots else "...", "unicode": uni, "three_dots": dots}

    # -- foreign tokens ----------------------------------------------------
    foreign: Counter[str] = Counter()
    for w in words:
        if len(w) > 1 and main_script not in {script_of(c) for c in w}:
            foreign[w.lower()] += 1
    allowlist = [w for w, n in foreign.most_common(top_foreign) if n >= 3]
    ev["foreign_layer"] = {
        "distinct_tokens": len(foreign),
        "total_occurrences": sum(foreign.values()),
        "allowlist_size": len(allowlist),
        "top": dict(foreign.most_common(15)),
    }

    # -- assemble ----------------------------------------------------------
    # Every dash variant other than the chosen one is forbidden at paragraph
    # start — including those absent from the corpus, which are the most
    # forbidden of all. An earlier version only listed variants it had seen,
    # so a corpus using one dash consistently produced an empty list and the
    # linter had nothing to catch.
    forbidden_markers = [d for d in DASHES if d != marker] if marker in DASHES else []
    forbidden_quotes = ['"', "“", "”"]
    if quote_pair:
        forbidden_quotes = [q for q in forbidden_quotes if q not in quote_pair]

    profile = {
        "_generated": "detect_profile.py — counts in _evidence; confirm before trusting",
        "target_language": "",
        "source_language": "",
        "chapter_glob": "*.md",
        "dialogue": {
            "marker": marker,
            "forbidden_markers": forbidden_markers,
            "allow_forbidden_markers_inline": True,
            "quotes_in_speech": quotes_in_speech,
            "quote_pair": quote_pair,
            "no_dash_on_continuation": bool(marker) and marker in DASHES,
        },
        "typography": {
            "forbidden_quotes": forbidden_quotes,
            "forbidden_sequences": ["..."] if uni >= dots else [],
        },
        "foreign_layer": {
            "main_script": main_script,
            "flag_unlisted_foreign": len(foreign) > 0 and main_script != "LATIN",
            "allowlist": allowlist,
        },
        "glossary": "GLOSSARY.md",
        "_evidence": ev,
    }
    return profile


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("reference", type=Path, help="extracted reference translation")
    ap.add_argument("--out", type=Path, default=Path("profile.json"))
    ap.add_argument("--glob", default="*.txt")
    ap.add_argument("--top-foreign", type=int, default=120)
    args = ap.parse_args()

    files = [args.reference] if args.reference.is_file() else [p for p in sorted(args.reference.rglob(args.glob)) if p.is_file()]
    if not files:
        print(f"error: no files matching {args.glob!r} under {args.reference}", file=sys.stderr)
        return 2

    text = "\n\n".join(p.read_text(encoding="utf-8", errors="replace") for p in files)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n|\n", text) if p.strip()]
    prof = detect(paragraphs, text, args.top_foreign)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(prof, ensure_ascii=False, indent=2), encoding="utf-8")

    ev = prof["_evidence"]
    d = prof["dialogue"]
    print(f"read {len(files)} files, {len(paragraphs):,} paragraphs\n")
    print(f"  script            {ev['script']['detected']}")
    print(f"  dialogue marker   {d['marker']!r}  ({', '.join(f'{k}={v}' for k, v in list(ev['dialogue_marker']['counts'].items())[:3])})")
    if ev["dialogue_marker"]["note"]:
        print(f"                    ! {ev['dialogue_marker']['note']}")
    print(f"  quote pair        {d['quote_pair']}")
    print(f"  quotes in speech  {d['quotes_in_speech']}")
    print(f"  ellipsis          {ev['ellipsis']['detected']!r}  (… {ev['ellipsis']['unicode']} vs ... {ev['ellipsis']['three_dots']})")
    print(f"  foreign tokens    {ev['foreign_layer']['distinct_tokens']} distinct, "
          f"allowlist {ev['foreign_layer']['allowlist_size']}")
    print(f"\n-> {args.out}")
    print("\nThis settles what is countable. Register, voice and neologism")
    print("formation still need reading — see templates/STYLEGUIDE.template.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
