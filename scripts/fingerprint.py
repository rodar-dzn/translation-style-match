#!/usr/bin/env python3
"""Stylometric fingerprint of a text, and comparison against a reference.

    python fingerprint.py work/ref/ --out work/ref-fingerprint.json
    python fingerprint.py draft/   --compare work/ref-fingerprint.json

Measures whole-text habits that a chapter-by-chapter reading pass cannot
see: dialogue density, sentence length, punctuation rates, foreign-token
density, lexical variety.

These are signals, not verdicts. A divergence points at a category of
problem worth reading for; it does not by itself mean anything is wrong.

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import unicodedata
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

WORD = re.compile(r"[^\W\d_]+", re.UNICODE)
SENT_END = re.compile(r"[.!?…]+[\"'»”)\]]*\s+")
DIALOGUE_OPENERS = ("–", "—", "―", '"', "«", "„", "-")

_SCRIPT: dict[str, str] = {}


def script_of(ch: str) -> str:
    if ch not in _SCRIPT:
        try:
            first = unicodedata.name(ch).split()[0]
        except ValueError:
            first = "OTHER"
        _SCRIPT[ch] = first if first in ("LATIN", "CYRILLIC", "GREEK", "ARABIC", "HEBREW") else "OTHER"
    return _SCRIPT[ch]


def dominant_script(words: list[str]) -> str:
    counts: dict[str, int] = {}
    for w in words[:20000]:
        for ch in w:
            s = script_of(ch)
            if s != "OTHER":
                counts[s] = counts.get(s, 0) + 1
    return max(counts, key=counts.get) if counts else "OTHER"


def read_text(target: Path, glob: str) -> str:
    if target.is_file():
        return target.read_text(encoding="utf-8", errors="replace")
    parts = [p.read_text(encoding="utf-8", errors="replace")
             for p in sorted(target.rglob(glob)) if p.is_file()]
    if not parts:
        parts = [p.read_text(encoding="utf-8", errors="replace")
                 for p in sorted(target.rglob("*.txt")) if p.is_file()]
    return "\n\n".join(parts)


def measure(text: str) -> dict:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n|\n", text) if p.strip()]
    words = WORD.findall(text)
    if not words or not paragraphs:
        return {}

    sentences = [s for s in SENT_END.split(text) if s.strip()]
    sent_lengths = [len(WORD.findall(s)) for s in sentences]
    sent_lengths = [n for n in sent_lengths if n > 0]

    dialogue = [p for p in paragraphs if p.startswith(DIALOGUE_OPENERS)]
    main = dominant_script(words)
    foreign = [w for w in words if len(w) > 1 and main not in {script_of(c) for c in w}]

    per_1k = lambda n: round(n / len(words) * 1000, 2)  # noqa: E731
    lower = [w.lower() for w in words]

    return {
        "words": len(words),
        "paragraphs": len(paragraphs),
        "sentences": len(sent_lengths),
        "dominant_script": main,
        "dialogue_paragraph_ratio": round(len(dialogue) / len(paragraphs), 4),
        "mean_sentence_words": round(statistics.mean(sent_lengths), 2) if sent_lengths else 0,
        "sentence_words_stdev": round(statistics.pstdev(sent_lengths), 2) if len(sent_lengths) > 1 else 0,
        "median_sentence_words": round(statistics.median(sent_lengths), 2) if sent_lengths else 0,
        "mean_paragraph_words": round(len(words) / len(paragraphs), 2),
        "foreign_tokens_per_1k": per_1k(len(foreign)),
        "distinct_foreign_tokens": len({w.lower() for w in foreign}),
        "type_token_ratio": round(len(set(lower)) / len(words), 4),
        "punctuation_per_1k": {
            "en_dash": per_1k(text.count("–")),
            "em_dash": per_1k(text.count("—")),
            "ellipsis_char": per_1k(text.count("…")),
            "ellipsis_dots": per_1k(len(re.findall(r"\.\.\.", text))),
            "semicolon": per_1k(text.count(";")),
            "colon": per_1k(text.count(":")),
            "question": per_1k(text.count("?")),
            "exclamation": per_1k(text.count("!")),
            "guillemets": per_1k(text.count("«")),
            "straight_quote": per_1k(text.count('"')),
        },
    }


FLAT = [
    ("dialogue_paragraph_ratio", 0.25, "dialogue density"),
    ("mean_sentence_words", 0.20, "mean sentence length"),
    ("sentence_words_stdev", 0.30, "sentence-length variance"),
    ("mean_paragraph_words", 0.30, "mean paragraph length"),
    ("foreign_tokens_per_1k", 0.40, "foreign-token density"),
    ("type_token_ratio", 0.20, "lexical variety"),
]

HINTS = {
    "dialogue density": "check paragraph splitting — narration glued to speech lines collapses this",
    "mean sentence length": "sentences may be tracing source syntax instead of the target's",
    "sentence-length variance": "uniform sentence length is a signature of flattened register",
    "mean paragraph length": "check that speaker changes start new paragraphs",
    "foreign-token density": "the foreign layer is being applied at a different rate than the corpus",
    "lexical variety": "lower variety suggests vocabulary is collapsing toward the neutral stratum",
}


def compare(draft: dict, ref: dict) -> int:
    print(f"{'metric':<28} {'reference':>12} {'draft':>12} {'delta':>10}")
    print("-" * 66)
    flagged = []

    for key, tol, label in FLAT:
        a, b = ref.get(key), draft.get(key)
        if a in (None, 0) or b is None:
            continue
        delta = (b - a) / a
        mark = "  <-- " if abs(delta) > tol else ""
        print(f"{label:<28} {a:>12} {b:>12} {delta:>+9.0%}{mark}")
        if abs(delta) > tol:
            flagged.append(label)

    print()
    rp, dp = ref.get("punctuation_per_1k", {}), draft.get("punctuation_per_1k", {})
    for key in sorted(set(rp) | set(dp)):
        a, b = rp.get(key, 0), dp.get(key, 0)
        if a == 0 and b == 0:
            continue
        if a == 0:
            print(f"{key:<28} {a:>12} {b:>12} {'absent in ref':>10}  <-- ")
            flagged.append(key)
            continue
        delta = (b - a) / a
        mark = "  <-- " if abs(delta) > 0.5 else ""
        print(f"{key:<28} {a:>12} {b:>12} {delta:>+9.0%}{mark}")
        if abs(delta) > 0.5:
            flagged.append(key)

    if flagged:
        print("\ndivergent:")
        for label in flagged:
            hint = HINTS.get(label, "compare against the corpus directly")
            print(f"  - {label}: {hint}")
        print("\nThese are signals, not verdicts. Read the relevant axis before acting.")
    else:
        print("\nno metric diverges beyond tolerance")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", type=Path)
    ap.add_argument("--out", type=Path, help="write fingerprint JSON here")
    ap.add_argument("--compare", type=Path, help="reference fingerprint JSON to diff against")
    ap.add_argument("--glob", default="*.txt")
    args = ap.parse_args()

    if not args.target.exists():
        print(f"error: {args.target} not found", file=sys.stderr)
        return 1

    fp = measure(read_text(args.target, args.glob))
    if not fp:
        print("error: no measurable text found", file=sys.stderr)
        return 1

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(fp, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"fingerprint -> {args.out}")

    if args.compare:
        if not args.compare.exists():
            print(f"error: {args.compare} not found", file=sys.stderr)
            return 1
        return compare(fp, json.loads(args.compare.read_text(encoding="utf-8")))

    if not args.out:
        print(json.dumps(fp, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
