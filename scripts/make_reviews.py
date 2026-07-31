#!/usr/bin/env python3
"""Turn the briefs in references/reviewers.md into runnable prompts.

    python make_reviews.py --project myproject/ --draft draft/ --out reviews/

Reads the project's style guide, glossary and split voices, and writes one
self-contained prompt file per reviewer, with the project's own data
already in it. Each file can be handed to a fresh agent or model session
as-is.

Why files rather than dispatch: reviewers must be *independent*. Running
them in one session lets earlier findings colour later ones, which is the
correlated-blind-spot problem the swarm exists to avoid. Separate prompts
in separate sessions is the point, not an inconvenience.

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

GOVERNING = """\
## The rule that governs this review

**The corpus outranks your taste.**

Report only divergence *from the reference translation*. "I would have
phrased this differently" is not a finding. If you cannot point at what the
reference does instead, you have nothing to say — say nothing.

Do not report every line. If more than a third of what you read looks wrong,
stop and say the profile may be mis-specified. That is more useful than two
hundred findings.

For each finding give: the span, its location tag, which signal is wrong,
what the corpus does instead with a citation, and a specific replacement.

End your report by stating what you did **not** cover.
"""


def read(path: Path, limit: int = 0) -> str:
    if not path.exists():
        return ""
    t = path.read_text(encoding="utf-8", errors="replace")
    return t[:limit] + ("\n…(truncated)" if limit and len(t) > limit else "") if limit else t


def voice_brief(name: str, lines: str, styleguide: str) -> str:
    return f"""# Reviewer: voice — {name}

You are checking whether one character's speech is consistent with how the
reference translation renders that character.

{GOVERNING}
## Character profile

Taken from the project style guide. If the section for {name} is empty, say
so and stop — reviewing against an unwritten profile produces noise.

```
{styleguide}
```

## Lines to review

Every line attributed to {name} in the draft, with location tags.

```
{lines}
```

## What to look for

Stratum, sentence length, marker words and their frequency and placement,
forms of address, and anything this character never does in the reference.

Ask of each line only: *could this be another character?* Where the answer
is yes, you have a finding.
"""


def simple_brief(title: str, body: str) -> str:
    return f"# Reviewer: {title}\n\n{GOVERNING}\n{body}\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--draft", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--max-voices", type=int, default=8)
    ap.add_argument("--max-lines", type=int, default=40000, help="chars of speech per voice brief")
    args = ap.parse_args()

    project, out = args.project, args.out
    styleguide = read(project / "STYLEGUIDE.md", 12000)
    glossary = read(project / "GLOSSARY.md", 14000)
    voices = project / "voices" / "by-speaker"
    out.mkdir(parents=True, exist_ok=True)

    written, warnings = [], []
    if not styleguide.strip() or "<" in styleguide[:400]:
        warnings.append("STYLEGUIDE.md looks unfilled — voice reviewers will have no profile "
                        "to check against, and will correctly refuse to report")
    if not glossary.strip() or "|  |  |" in glossary:
        warnings.append("GLOSSARY.md looks unfilled — the drift reviewer has nothing to enforce")

    # -- voice reviewers, one per character --------------------------------
    if voices.exists():
        files = sorted((p for p in voices.glob("*.txt") if not p.name.startswith("_")),
                       key=lambda p: -p.stat().st_size)[: args.max_voices]
        for p in files:
            name = p.stem.replace("_", " ")
            path = out / f"voice-{p.stem}.md"
            path.write_text(voice_brief(name, read(p, args.max_lines), styleguide), encoding="utf-8")
            written.append(path)
    else:
        warnings.append(f"{voices} missing — run `tsm.py check` first; no voice reviewers written")

    # -- the rest ----------------------------------------------------------
    briefs = {
        "calques": ("calques", f"""\
Find constructions carried over from the source language that are
grammatical in the target but not idiomatic in it: literal renderings of
dead metaphors, idioms translated piece by piece, source word order kept
where the target would reorder, and wordplay translated literally.

Wordplay is the priority. When a pun is rendered literally, the surrounding
prose often still shows characters reacting to a joke that is no longer
there. Flag the joke **and** the orphaned reaction.

Do not flag phrasing that is merely striking. Literary prose is allowed to
be strange. Flag only what is strange *because of the source*.

## Draft

Read the files under `{args.draft}`."""),

        "verse": ("verse", f"""\
For each verse passage, check in this order: does it scan when read aloud;
does it follow the corpus's policy rather than the source's; stanza count
preserved; parallel openings and refrains preserved; do the surrounding
prose reactions still make sense; are performance artifacts (stutters,
breaks) in their original metrical positions.

A failure to scan, or prose reactions that no longer fit, outranks any
inaccuracy of imagery. Say which of the two you are reporting.

## Corpus verse policy

```
{styleguide}
```

## Draft

Read the files under `{args.draft}`."""),

        "glossary-drift": ("glossary drift", f"""\
Long drafts drift: a term rendered one way early quietly becomes something
else later, and no single-chapter read will catch it.

Across the whole draft, report a term rendered inconsistently between
chapters; a name whose declension pattern changes; two glossary entries
collapsed into one rendering; a coined term whose formation does not match
the recorded pattern.

Give locations for every instance and say which rendering the corpus
supports. Where the glossary itself is silent, say so — that is a gap to
fill, not an error to fix.

## Glossary

```
{glossary}
```

## Draft

Read the files under `{args.draft}`."""),

        "narration": ("narration", f"""\
Everything else here reviews dialogue. This reviews the narrator.

Check the narration against its profile: stratum, sentence length, whether
it carries the foreign layer, whether profanity survives into it. Where the
narrator is a character, check whether their written register differs from
their spoken one, and whether the reference maintains that gap.

## Narration profile

```
{styleguide}
```

## Draft

Read the files under `{args.draft}`."""),
    }

    for key, (title, body) in briefs.items():
        path = out / f"{key}.md"
        path.write_text(simple_brief(title, body), encoding="utf-8")
        written.append(path)

    # -- aggregation instructions -----------------------------------------
    (out / "_aggregate.md").write_text(f"""# Aggregating the reports

Run each brief in **its own session**. Independence is the point: reviewers
sharing a context inherit each other's blind spots, which is the failure the
swarm exists to avoid.

Then merge:

- **Deduplicate by span.** Two reviewers flagging one sentence for different
  reasons is one location, not two problems.
- **Rank by agreement.** A span flagged by three independent reviewers is
  almost certainly real; one flagged by a single reviewer on a subjective
  axis is a candidate. Report which is which — a merged report that presents
  both at the same confidence is not usable.
- **Group by axis, not by page.** Six findings on one axis mean one habit to
  change. Six across six axes mean six separate fixes.
- **Drop anything without a corpus citation.**
- **Record what was not covered**, per reviewer.

## Calibrating

Before trusting any of this, run the same briefs against a chapter of the
**reference translation** itself. Every finding will be a false positive by
construction, and the volume tells you which briefs over-fire.

## Reviewers written

{chr(10).join(f'- `{p.name}`' for p in written)}
""", encoding="utf-8")

    print(f"{len(written)} reviewer prompt(s) -> {out}")
    for p in written:
        print(f"  {p.name}")
    if warnings:
        print("\nwarnings:")
        for w in warnings:
            print(f"  ! {w}")
    print(f"\nRun each in a separate session. See {out / '_aggregate.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
