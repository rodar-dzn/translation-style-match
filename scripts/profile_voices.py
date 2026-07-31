#!/usr/bin/env python3
"""Derive per-character voice profiles by measuring their speech.

    python profile_voices.py --project myproject/ --out myproject/STYLEGUIDE.md

Reads the speech `split_dialogue.py` grouped by speaker and computes, per
character: sentence length and its spread, punctuation habits, foreign-token
density, address forms, and — the useful part — **keyness**: the words this
character uses at rates the other characters do not.

Keyness is what finds a marker word. A particle or oath that belongs to one
speaker shows up as statistically overrepresented in their lines, by log-
likelihood against the pooled speech of everyone else. No semantic
judgment, no word lists, no per-language configuration.

What it cannot do is *name* the stratum — whether a character's distinctive
vocabulary is elevated, coarse or archaic is a semantic call. But it surfaces
the words themselves, so that call becomes a glance rather than an
investigation.

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import math
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
SENT = re.compile(r"[.!?…]+")
LOCATION = re.compile(r"^\S+\s+¶\d+\t")

# Second-person forms worth reporting per target language. Address is one of
# the strongest voice signals and one English gives no signal for.
ADDRESS = {
    "CYRILLIC": {"ты": "informal", "тебя": "informal", "тебе": "informal", "тобой": "informal",
                 "вы": "formal", "вас": "formal", "вам": "formal", "вами": "formal"},
    "LATIN": {"tu": "informal", "toi": "informal", "vous": "formal",
              "du": "informal", "dich": "informal", "dir": "informal",
              "sie": "formal", "ihnen": "formal",
              "usted": "formal", "ustedes": "formal", "vos": "informal"},
}


def load_voice(path: Path) -> list[str]:
    lines = []
    for raw in path.read_text(encoding="utf-8", errors="replace").split("\n"):
        if raw.startswith("#") or not raw.strip():
            continue
        lines.append(LOCATION.sub("", raw).strip())
    return [l for l in lines if l]


def keyness(target: Counter, reference: Counter, top: int, min_count: int) -> list[tuple[str, float, int]]:
    """Dunning log-likelihood: words overrepresented in target vs reference."""
    c, d = sum(target.values()), sum(reference.values())
    if not c or not d:
        return []
    out = []
    for word, a in target.items():
        if a < min_count:
            continue
        b = reference.get(word, 0)
        e1 = c * (a + b) / (c + d)
        e2 = d * (a + b) / (c + d)
        g2 = 2 * (a * math.log(a / e1) + (b * math.log(b / e2) if b else 0))
        # only over-use, not under-use
        if a / c > (b / d if d else 0):
            out.append((word, g2, a))
    out.sort(key=lambda r: -r[1])
    return out[:top]


def measure_voice(lines: list[str]) -> dict:
    text = " ".join(lines)
    words = WORD.findall(text.lower())
    sents = [s for s in SENT.split(text) if WORD.search(s)]
    lengths = [len(WORD.findall(s)) for s in sents] or [0]
    per_1k = (lambda n: round(n / max(len(words), 1) * 1000, 1))
    return {
        "lines": len(lines),
        "words": len(words),
        "mean_sentence": round(statistics.mean(lengths), 1),
        "sentence_spread": round(statistics.pstdev(lengths), 1) if len(lengths) > 1 else 0.0,
        "questions_per_1k": per_1k(text.count("?")),
        "exclamations_per_1k": per_1k(text.count("!")),
        "ellipsis_per_1k": per_1k(text.count("…")),
        "counter": Counter(words),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--out", type=Path, help="defaults to <project>/STYLEGUIDE.md")
    ap.add_argument("--top-keywords", type=int, default=18)
    ap.add_argument("--min-count", type=int, default=4)
    ap.add_argument("--min-lines", type=int, default=25, help="skip characters with fewer lines")
    ap.add_argument("--max-voices", type=int, default=10)
    args = ap.parse_args()

    project = args.project
    voices = project / "voices" / "by-speaker"
    if not voices.exists():
        print(f"error: {voices} not found — run `tsm.py check` first", file=sys.stderr)
        return 2

    profile = json.loads((project / "profile.json").read_text(encoding="utf-8")) \
        if (project / "profile.json").exists() else {}
    script = profile.get("foreign_layer", {}).get("main_script", "").upper()
    address_forms = ADDRESS.get(script, {})

    data = {}
    for p in sorted(voices.glob("*.txt")):
        if p.name.startswith("_"):
            continue
        lines = load_voice(p)
        if len(lines) >= args.min_lines:
            data[p.stem.replace("_", " ")] = measure_voice(lines)
    if not data:
        print(f"error: no character has {args.min_lines}+ lines", file=sys.stderr)
        return 1

    data = dict(sorted(data.items(), key=lambda kv: -kv[1]["lines"])[: args.max_voices])
    pooled = Counter()
    for v in data.values():
        pooled.update(v["counter"])

    out = args.out or (project / "STYLEGUIDE.md")
    doc = [
        "# Style guide", "",
        "Voice sections below are **derived by measurement** from the reference",
        "translation — sentence shape, punctuation habits, address, and keyness:",
        "the words each character uses at rates the others do not.",
        "",
        "What measurement cannot settle is what the distinctive vocabulary *means* —",
        "whether it is elevated, coarse or archaic. Read each keyword list and write",
        "the one-line stratum note. That is a glance, not an investigation, and it is",
        "the only handwork left.",
        "",
        "---", "",
        "## Narration", "",
        "_Not derived: narration is whatever is not dialogue, and separating it needs",
        "the corpus rather than the voice split. Fill by reading._", "",
        "- Stratum:",
        "- Carries the foreign layer:",
        "- Profanity survives into it:", "",
        "---", "",
    ]

    for name, v in data.items():
        others = Counter(pooled)
        others.subtract(v["counter"])
        others = Counter({w: n for w, n in others.items() if n > 0})
        keys = keyness(v["counter"], others, args.top_keywords, args.min_count)

        addr = {form: v["counter"].get(form, 0) for form in address_forms}
        addr = {k: n for k, n in addr.items() if n}
        addr_note = ", ".join(f"`{k}` ×{n} ({address_forms[k]})"
                              for k, n in sorted(addr.items(), key=lambda kv: -kv[1])[:6]) or "none detected"

        doc += [
            f"## {name}", "",
            f"`{v['lines']}` lines, `{v['words']:,}` words of speech", "",
            "| measure | value |",
            "|---|---|",
            f"| mean sentence | {v['mean_sentence']} words |",
            f"| sentence spread | {v['sentence_spread']} |",
            f"| questions | {v['questions_per_1k']} per 1000 words |",
            f"| exclamations | {v['exclamations_per_1k']} per 1000 words |",
            f"| ellipses | {v['ellipsis_per_1k']} per 1000 words |",
            "",
            f"**Address forms:** {addr_note}", "",
            "**Distinctive vocabulary** — used at rates the other characters do not, "
            "by log-likelihood:", "",
            "| word | keyness | uses |", "|---|---|---|",
        ]
        for word, g2, count in keys:
            doc.append(f"| {word} | {g2:.1f} | {count} |")
        doc += [
            "",
            "- **Stratum:** _(read the list above and name it — elevated? coarse? archaic?)_",
            "- **Collides with:** _(if the voice mixes two strata, that collision is the "
            "characterization)_",
            f"- **Marker word:** _(if one of the above is a particle or oath rather than a "
            f"topic word, it is a marker — note its placement)_",
            "- **Never does:**", "",
            "---", "",
        ]

    doc += [
        "## How to read the keyness column", "",
        "High keyness on a **topic** word (a place, an object) means the character talks",
        "about that thing — useful, but not voice.",
        "",
        "High keyness on a **particle, oath, or filler** is a marker word: it belongs to",
        "the speaker rather than the subject, and preserving its *rate and placement*",
        "matters as much as preserving the word.",
        "",
        "That distinction is the whole judgment being asked of you.", "",
    ]

    if out.exists() and "derived by measurement" not in out.read_text(encoding="utf-8", errors="replace"):
        backup = out.with_suffix(".md.bak")
        backup.write_text(out.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        print(f"existing {out.name} backed up to {backup.name}")

    out.write_text("\n".join(doc), encoding="utf-8")

    print(f"{len(data)} voices profiled -> {out}\n")
    print(f"{'character':<22}{'lines':>7}{'sent':>7}{'spread':>8}  top keywords")
    print("-" * 76)
    for name, v in data.items():
        others = Counter(pooled)
        others.subtract(v["counter"])
        others = Counter({w: n for w, n in others.items() if n > 0})
        keys = keyness(v["counter"], others, 4, args.min_count)
        print(f"{name[:21]:<22}{v['lines']:>7}{v['mean_sentence']:>7}{v['sentence_spread']:>8}  "
              f"{', '.join(w for w, _, _ in keys)}")

    print("\nMeasured: sentence shape, punctuation, address, distinctive vocabulary.")
    print("Left to you: one line per character naming the stratum. Read the keyword")
    print("lists — a particle among them is a marker word, and that is the finding.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
