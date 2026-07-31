#!/usr/bin/env python3
"""Split dialogue out of prose and group it by speaker.

    python split_dialogue.py draft/ --profile profile.json \
        --glossary GLOSSARY.md --out work/voices/

    # explicit cast, when the glossary has no Characters section
    python split_dialogue.py draft/ --profile profile.json \
        --characters "Name One,Name Two" --out work/voices/

Two jobs:

1. Give each per-character reviewer a compact input — one file of that
   character's speech — instead of the whole book. This is what makes a
   swarm of narrow reviewers affordable.

2. Produce the blind attribution test described in
   `references/register.md`: shuffled, de-attributed lines plus a key.
   The share you can assign correctly is a rough measure of how much
   voice survived. Run it on the reference corpus too, for a baseline.

Attribution is heuristic and deliberately conservative. It reads the
narration tag inside a dialogue paragraph and looks for a known name.
Anything it cannot settle goes to `_unattributed.txt` with context, for
a person to assign. Never treat the attribution rate as an accuracy
figure for the draft — it measures this script, not the prose.

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def load_profile(path: Path) -> dict:
    if not path.exists():
        print(f"error: profile {path} not found", file=sys.stderr)
        raise SystemExit(2)
    return json.loads(path.read_text(encoding="utf-8"))


def characters_from_glossary(path: Path) -> list[str]:
    """Pull canonical names from the glossary's Characters table."""
    if not path or not path.exists():
        return []
    names, in_section = [], False
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("#"):
            in_section = "character" in s.lower() or "персонаж" in s.lower()
            continue
        if not in_section or not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 2 or cells[0].lower() in ("source", "исходник", "термин"):
            continue
        if set(s) <= set("|- :"):
            continue
        canonical = cells[1]
        if canonical and canonical not in ("—", "-"):
            names.append(canonical)
    return names


def stem(name: str, trim: int) -> str:
    """Crude stem so inflected forms of a name still match."""
    head = name.split()[0] if " " in name else name
    return head[: max(4, len(head) - trim)].lower()


def split_paragraph(par: str, marker: str) -> tuple[list[str], list[str]]:
    """Return (speech segments, narration segments) of a dialogue paragraph.

    Assumes the convention `<marker> speech <marker> tag <marker> speech`,
    i.e. odd segments are spoken and even ones from index 2 are narration.
    """
    parts = par.split(marker)
    speech = [p.strip() for i, p in enumerate(parts) if i % 2 == 1 and p.strip()]
    narration = [p.strip() for i, p in enumerate(parts) if i >= 2 and i % 2 == 0 and p.strip()]
    return speech, narration


def attribute(narration: list[str], context: str, cast: dict[str, str]) -> tuple[str | None, str]:
    """Find the speaker. Returns (name or None, confidence)."""
    def hits(text: str) -> set[str]:
        low = text.lower()
        return {full for st, full in cast.items() if st in low}

    tag_hits = hits(" ".join(narration))
    if len(tag_hits) == 1:
        return tag_hits.pop(), "tag"
    if len(tag_hits) > 1:
        return None, "ambiguous-tag"

    ctx_hits = hits(context)
    if len(ctx_hits) == 1:
        return ctx_hits.pop(), "context"
    return None, "none"


def safe(name: str) -> str:
    return re.sub(r"[^\w\-. ]", "", name).strip().replace(" ", "_") or "unnamed"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", type=Path, help="file or directory of prose")
    ap.add_argument("--profile", type=Path, default=Path("profile.json"))
    ap.add_argument("--glossary", type=Path, default=Path("GLOSSARY.md"))
    ap.add_argument("--characters", help="comma-separated cast, overrides the glossary")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--trim", type=int, default=2, help="chars trimmed for stem matching (default 2)")
    ap.add_argument("--blind", type=int, default=60, help="lines in the blind test (0 to skip)")
    ap.add_argument("--seed", type=int, default=0, help="shuffle seed for a reproducible blind test")
    ap.add_argument("--glob", help="file pattern, overriding the profile's chapter_glob")
    args = ap.parse_args()

    cfg = load_profile(args.profile)
    marker = cfg.get("dialogue", {}).get("marker", "")
    if not marker:
        print("error: profile has no dialogue.marker", file=sys.stderr)
        return 2

    names = (
        [n.strip() for n in args.characters.split(",") if n.strip()]
        if args.characters
        else characters_from_glossary(args.glossary)
    )
    if not names:
        print("error: no cast — fill the glossary's Characters section or pass --characters",
              file=sys.stderr)
        return 2
    cast = {stem(n, args.trim): n for n in names}

    glob = args.glob or cfg.get("chapter_glob", "*.md")
    files = sorted(p for p in args.target.rglob(glob) if p.is_file()) if args.target.is_dir() else [args.target]
    if not files:
        print(f"error: no files matching {glob!r} under {args.target}", file=sys.stderr)
        return 2

    by_speaker: dict[str, list[str]] = {n: [] for n in names}
    unattributed: list[str] = []
    blind_pool: list[tuple[str, str]] = []
    counts = {"tag": 0, "context": 0, "ambiguous-tag": 0, "none": 0}
    total = 0

    for f in files:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n|\n", f.read_text(encoding="utf-8", errors="replace")) if p.strip()]
        for i, par in enumerate(paragraphs):
            if not par.startswith(marker):
                continue
            speech, narration = split_paragraph(par, marker)
            if not speech:
                continue
            total += 1
            context = " ".join(paragraphs[max(0, i - 2) : i] + paragraphs[i + 1 : i + 2])
            who, how = attribute(narration, context, cast)
            counts[how] = counts.get(how, 0) + 1
            line = " / ".join(speech)
            loc = f"{f.stem} ¶{i}"

            if who:
                by_speaker[who].append(f"{loc}\t{line}")
                blind_pool.append((line, who))
            else:
                ctx = f"\n    before: {paragraphs[i-1][:120]}" if i else ""
                nxt = f"\n    after:  {paragraphs[i+1][:120]}" if i + 1 < len(paragraphs) else ""
                unattributed.append(f"{loc}\t[{how}]\t{line}{ctx}{nxt}")

    out = args.out
    (out / "by-speaker").mkdir(parents=True, exist_ok=True)
    written = 0
    for name, lines in sorted(by_speaker.items(), key=lambda kv: -len(kv[1])):
        if not lines:
            continue
        (out / "by-speaker" / f"{safe(name)}.txt").write_text(
            f"# {name} — {len(lines)} lines\n\n" + "\n".join(lines) + "\n", encoding="utf-8"
        )
        written += 1
    if unattributed:
        (out / "by-speaker" / "_unattributed.txt").write_text(
            f"# unattributed — {len(unattributed)} lines\n"
            f"# assign these by hand; the script would only be guessing\n\n"
            + "\n".join(unattributed) + "\n",
            encoding="utf-8",
        )

    if args.blind and blind_pool:
        rng = random.Random(args.seed)
        sample = rng.sample(blind_pool, min(args.blind, len(blind_pool)))
        (out / "blind-test.txt").write_text(
            "# Blind attribution test\n"
            "# Assign a speaker to each line without looking at the key.\n"
            "# Run this on the reference corpus too — the gap between the two\n"
            "# scores is the size of the flattening problem.\n\n"
            + "\n".join(f"{i:3d}. {line}" for i, (line, _) in enumerate(sample, 1)) + "\n",
            encoding="utf-8",
        )
        (out / "blind-test-key.txt").write_text(
            "\n".join(f"{i:3d}. {who}" for i, (_, who) in enumerate(sample, 1)) + "\n",
            encoding="utf-8",
        )

    summary = {
        "files": len(files),
        "dialogue_paragraphs": total,
        "attributed": counts["tag"] + counts["context"],
        "attribution_rate": round((counts["tag"] + counts["context"]) / total, 3) if total else 0,
        "by_method": counts,
        "speakers_with_lines": written,
        "cast_size": len(names),
    }
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{total} dialogue paragraphs from {len(files)} files")
    print(f"attributed {summary['attributed']} ({summary['attribution_rate']:.0%}) "
          f"across {written} speakers -> {out / 'by-speaker'}")
    if unattributed:
        print(f"{len(unattributed)} unattributed -> by-speaker/_unattributed.txt")
    if args.blind and blind_pool:
        print(f"blind test of {min(args.blind, len(blind_pool))} lines -> {out / 'blind-test.txt'}")
    print("\nattribution is heuristic — it measures this script, not the prose")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
