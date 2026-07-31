#!/usr/bin/env python3
"""Assemble everything the project knows into a translation prompt.

    python make_translation.py --project myproject/ --source ch01.txt \
        --out myproject/prompts/ch01.md

    # after checking a draft, build a repair prompt from what failed
    python make_translation.py --project myproject/ --source ch01.txt \
        --draft draft/ch01.md --lint myproject/lint.txt \
        --out myproject/prompts/ch01-repair.md

The tool has no model access and makes no network calls, so it writes the
prompt rather than the translation. That keeps the architecture honest: the
project's job is to know the conventions, not to own a model.

What makes this more than a wrapper is **pre-resolution**. The source
passage is scanned against the glossary, and only the terms actually
present are included, with their canonical renderings and the note that
they are binding. A translator — human or model — gets the six terms this
page needs rather than a four-hundred-row table it will skim.

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def read(path: Path, limit: int = 0) -> str:
    if not path or not path.exists():
        return ""
    t = path.read_text(encoding="utf-8", errors="replace")
    return t[:limit] + "\n…(truncated)" if limit and len(t) > limit else t


def parse_glossary(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s.startswith("|") or set(s) <= set("|- :"):
            continue
        c = [x.strip() for x in s.strip("|").split("|")]
        if len(c) < 2 or c[0].lower() in ("source", "исходник", "термин"):
            continue
        if c[1] and c[1] not in ("—", "-"):
            rows.append({"source": c[0], "canonical": c[1],
                         "status": (c[3].upper() if len(c) > 3 else "")})
    return rows


def relevant_terms(source: str, glossary: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split the glossary into terms present in this passage and the rest."""
    low = source.lower()
    present, absent = [], []
    for row in glossary:
        needle = (row["source"] or row["canonical"]).lower()
        (present if needle and needle in low else absent).append(row)
    return present, absent


def dialogue_rules(cfg: dict) -> str:
    d = cfg.get("dialogue", {})
    fl = cfg.get("foreign_layer", {})
    out = []
    if d.get("marker"):
        out.append(f"- Speech paragraphs open with `{d['marker']}` "
                   f"(U+{ord(d['marker'][0]):04X}). Never "
                   f"{', '.join(repr(m) for m in d.get('forbidden_markers', [])) or 'any other dash'}.")
    if not d.get("quotes_in_speech", True) and d.get("quote_pair"):
        out.append(f"- No {d['quote_pair'][0]}{d['quote_pair'][1]} inside speech. Those marks are "
                   f"for genuine quotation only — titles, inscriptions, a character quoting "
                   f"someone verbatim.")
    if d.get("no_dash_on_continuation"):
        out.append("- When one speaker's turn runs across paragraphs, later paragraphs take "
                   "**no** opening marker. A marker there reads as a second speaker.")
    out.append("- A new speaker requires a new paragraph. Narration about someone else may not "
               "share a speech paragraph.")
    for seq in cfg.get("typography", {}).get("forbidden_sequences", []):
        out.append(f"- Never write `{seq}`.")
    for q in cfg.get("typography", {}).get("forbidden_quotes", []):
        out.append(f"- Never use `{q}` (U+{ord(q):04X}).")
    if fl.get("allowlist"):
        shown = ", ".join(f"`{w}`" for w in fl["allowlist"][:40])
        out.append(f"- The reference keeps some words untranslated, in their original script. "
                   f"Confirmed in this corpus: {shown}. Keep them in that script and do **not** "
                   f"give them target-language endings — a word combining both scripts is always "
                   f"an error.")
    return "\n".join(out)


HARD_RULES = """\
## Rules that override everything else

1. **Never invent a term that the glossary already settles.** The renderings
   below are canon. A reader of the earlier volumes spots a changed name
   immediately, and it is the loudest possible signal that a different hand
   is at work.

2. **Where you are unsure of a term, mark it** as `[?term]` in the output and
   list it at the end. Do not guess silently. A marked uncertainty costs one
   lookup; a silent guess costs a reader's trust.

3. **Match the register, not the dictionary.** Where a character's profile is
   given below, their voice outranks the most natural phrasing. If a line
   could belong to any character, it is wrong.

4. **Do not improve the source.** Awkwardness, repetition and strangeness in
   the original are the author's, and they survive translation.

5. **Report what you could not do.** If a pun, a verse form or a register
   effect did not survive, say so at the end with the location. Silent loss
   is the failure mode that makes a translation untrustworthy.
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--source", type=Path, required=True, help="source-language passage")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--target-file", type=Path, help="references/targets/<lang>.md to include")
    ap.add_argument("--draft", type=Path, help="existing draft, for a repair prompt")
    ap.add_argument("--lint", type=Path, help="lint output to repair against")
    args = ap.parse_args()

    project = args.project
    profile_path = project / "profile.json"
    if not profile_path.exists():
        print(f"error: {profile_path} not found — run `init` first", file=sys.stderr)
        return 2

    cfg = json.loads(profile_path.read_text(encoding="utf-8"))
    source = read(args.source)
    if not source.strip():
        print(f"error: {args.source} is empty", file=sys.stderr)
        return 2

    glossary = parse_glossary(project / "GLOSSARY.md")
    present, _ = relevant_terms(source, glossary)
    styleguide = read(project / "STYLEGUIDE.md", 14000)
    repair = bool(args.draft or args.lint)

    parts = [
        f"# {'Repair' if repair else 'Translate'}: `{args.source.name}`",
        "",
        "You are continuing an existing translation. The goal is not a good",
        "translation in the abstract — it is a passage indistinguishable from",
        "the reference translation of the earlier volumes.",
        "",
        HARD_RULES,
        "## Typography and conventions",
        "",
        "Measured from the reference corpus, not assumed:",
        "",
        dialogue_rules(cfg),
        "",
    ]

    if args.target_file and args.target_file.exists():
        parts += ["## Target-language conventions", "",
                  read(args.target_file, 10000), ""]

    if present:
        parts += ["## Canonical terms in this passage", "",
                  "Binding. These are how the reference renders them.", "",
                  "| Source | Use | Status |", "|---|---|---|"]
        for r in present:
            parts.append(f"| {r['source'] or '—'} | **{r['canonical']}** | {r['status'] or 'REVIEW'} |")
        parts.append("")
        unconfirmed = [r for r in present if r["status"] in ("REVIEW", "NEW", "OPEN", "")]
        if unconfirmed:
            parts += [f"{len(unconfirmed)} of these are not yet confirmed against the corpus. "
                      f"Use them, but flag any that look wrong.", ""]
    else:
        parts += ["## Canonical terms", "",
                  "No glossary terms matched this passage. Either the glossary is unfilled or "
                  "the passage introduces nothing already established — check which before "
                  "inventing anything.", ""]

    if styleguide.strip() and "<" not in styleguide[:200]:
        parts += ["## Register and voice", "", styleguide, ""]
    else:
        parts += ["## Register and voice", "",
                  "**The style guide is unfilled.** Without it the register axis cannot be "
                  "matched, and this passage will read as competent, neutral, and wrong. Fill "
                  "`STYLEGUIDE.md` before relying on the output.", ""]

    if repair:
        parts += ["## What failed", "",
                  "Fix these specifically. Do not retranslate what already passes.", ""]
        if args.lint and args.lint.exists():
            parts += ["```", read(args.lint, 12000).strip(), "```", ""]
        if args.draft and args.draft.exists():
            parts += ["## Current draft", "", "```", read(args.draft, 60000).strip(), "```", ""]

    parts += ["## Source", "", "```", source.strip(), "```", "",
              "---", "",
              "Output the translation only, then a short list headed "
              "**Uncertainties** and, if anything was lost, **Not carried over**."]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(parts), encoding="utf-8")

    words = len(re.findall(r"[^\W\d_]+", source, re.UNICODE))
    print(f"{'repair' if repair else 'translation'} prompt -> {args.out}")
    print(f"  source            {words:,} words")
    print(f"  glossary terms    {len(present)} of {len(glossary)} matched this passage")
    print(f"  style guide       {'included' if styleguide.strip() and '<' not in styleguide[:200] else 'UNFILLED — register cannot be matched'}")
    print(f"  target file       {args.target_file.name if args.target_file and args.target_file.exists() else 'none'}")
    print("\nHand this to a model or translator. Then check the result:")
    print(f"  python tsm.py check --project {project} --draft <result>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
