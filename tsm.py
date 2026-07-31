#!/usr/bin/env python3
"""translation-style-match — one command instead of six scripts.

    # set up a project from a reference translation
    python tsm.py init --reference book1.epub --project myproject/

    # check a draft against it
    python tsm.py check --project myproject/ --draft draft/

`init` extracts the reference, detects everything countable, derives
tolerances from the corpus's own chapter variation, and scaffolds the
glossary and style guide.

`check` runs every measurement and writes one report.

The scripts in `scripts/` remain usable on their own; this only spares you
the flags.

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE / "scripts"
TEMPLATES = HERE / "templates"


def run(script: str, *args: str) -> tuple[int, str]:
    """Run one of the scripts, returning (exit code, combined output)."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def rule(title: str) -> str:
    return f"\n{'─' * 70}\n{title}\n{'─' * 70}"


# --------------------------------------------------------------------------


def cmd_init(args) -> int:
    project: Path = args.project
    project.mkdir(parents=True, exist_ok=True)
    ref_text = project / "reference-text"

    print(rule("1/4  extracting the reference"))
    code, out = run("extract_corpus.py", str(args.reference), "--out", str(ref_text))
    print(out.rstrip())
    if code:
        return code

    print(rule("2/4  detecting conventions"))
    code, out = run("detect_profile.py", str(ref_text), "--out", str(project / "profile.json"))
    print(out.rstrip())
    if code:
        return code

    print(rule("3/4  deriving tolerances from chapter variation"))
    code, out = run("fingerprint.py", str(ref_text), "--out", str(project / "reference-fingerprint.json"))
    print(out.rstrip())
    if code:
        return code

    fp = json.loads((project / "reference-fingerprint.json").read_text(encoding="utf-8"))
    tol = fp.get("_tolerances")
    if tol:
        print(f"  {tol['chapters']} chapters used, {tol['skipped_fragments']} fragments skipped")
        for k, v in tol["flat"].items():
            print(f"    {k:<28} {v:.0%}")
    else:
        print("  too few chapters to derive tolerances — built-in fallbacks will be used")

    print(rule("4/5  scaffolding"))
    for src, dst in (("GLOSSARY.template.md", "GLOSSARY.md"),
                     ("STYLEGUIDE.template.md", "STYLEGUIDE.md")):
        target = project / dst
        if target.exists():
            print(f"  {dst} exists, left alone")
        else:
            shutil.copy(TEMPLATES / src, target)
            print(f"  {dst} created")

    print(rule("5/5  detecting the cast"))
    code, out = run("detect_cast.py", str(ref_text), "--profile", str(project / "profile.json"),
                    "--append", str(project / "GLOSSARY.md"), "--top", "30")
    print("\n".join(out.rstrip().split("\n")[:12]))
    if code:
        print("  (cast detection failed — fill the Characters section by hand)")

    print(f"""
{'═' * 70}
Project ready: {project}

Settled by counting:  profile.json, and the cast in GLOSSARY.md
What still needs you:

  1. STYLEGUIDE.md — register and voice. Read the corpus and fill it in.
     This is the axis no script reaches and the one that decides whether a
     draft passes as the same hand. Leave it empty and the voice reviewers
     will correctly refuse to report anything.

  2. GLOSSARY.md — the detected cast is marked REVIEW. Confirm each name
     against the corpus, then add coined terms:
       python scripts/build_glossary.py --source <src> --target {ref_text} --out cand.md

Then:
  python tsm.py check  --project {project} --draft <draft>
  python tsm.py review --project {project} --draft <draft>
{'═' * 70}""")
    return 0


# --------------------------------------------------------------------------


def cmd_check(args) -> int:
    project: Path = args.project
    ref_text = project / "reference-text"
    profile = project / "profile.json"
    glossary = project / "GLOSSARY.md"
    fp_ref = project / "reference-fingerprint.json"

    if not profile.exists():
        print(f"error: {profile} not found — run `init` first", file=sys.stderr)
        return 2

    report = [f"# Style check\n", f"Draft: `{args.draft}`  ",
              f"Reference: `{ref_text}`  ", f"Date: {date.today()}\n"]
    verdicts = []

    # -- 1. same hand? -----------------------------------------------------
    print(rule("1/4  same hand?  (Burrows's Delta)"))
    code, out = run("delta.py", "--reference", str(ref_text), "--test", str(args.draft),
                    "--glob", args.glob, "--out", str(project / "delta.json"))
    print(out.rstrip())
    report += ["## 1. Same hand?\n", "```", out.strip(), "```\n"]
    if (project / "delta.json").exists():
        d = json.loads((project / "delta.json").read_text(encoding="utf-8"))
        share = d["share_above"]
        verdicts.append(("same hand", "pass" if share < 0.20 else "mixed" if share < 0.5 else "FAIL",
                         f"{share:.0%} of chapters diverge"))

    # -- 2. which axis? ----------------------------------------------------
    print(rule("2/4  which axis diverges?  (diagnostic, not discriminative)"))
    if fp_ref.exists():
        code, out = run("fingerprint.py", str(args.draft), "--glob", args.glob,
                        "--compare", str(fp_ref))
        print(out.rstrip())
        report += ["## 2. Which axis\n", "```", out.strip(), "```\n"]
        flagged = out.count("<--")
        verdicts.append(("axes", "pass" if not flagged else "review", f"{flagged} metric(s) outside tolerance"))
    else:
        print("  no reference fingerprint — run `init` first")

    # -- 3. mechanical -----------------------------------------------------
    # The draft's file extension need not match the profile's chapter_glob,
    # which describes the *reference*. Override it so lint looks where the
    # draft actually is.
    print(rule("3/4  mechanical defects"))
    code, out = run("lint.py", str(args.draft), "--profile", str(profile),
                    "--glossary", str(glossary), "--level", "warning",
                    "--glob", args.glob)
    tail = out.strip().split("\n")
    print("\n".join(tail[-6:]) if len(tail) > 6 else out.rstrip())
    report += ["## 3. Mechanical\n", "```", out.strip()[:12000], "```\n"]
    # Exit 2 means the check could not run. Reporting that as "pass" would be
    # a silent false green — the exact failure this project warns about.
    verdicts.append((
        "mechanical",
        "not run" if code >= 2 else "FAIL" if code == 1 else "pass",
        next((l for l in reversed(tail) if "errors" in l), out.strip().split("\n")[-1]).strip(),
    ))

    # -- 4. voices ---------------------------------------------------------
    print(rule("4/4  splitting dialogue by speaker"))
    voices = project / "voices"
    code, out = run("split_dialogue.py", str(args.draft), "--profile", str(profile),
                    "--glossary", str(glossary), "--out", str(voices), "--glob", args.glob)
    print(out.rstrip())
    report += ["## 4. Voices\n", "```", out.strip(), "```\n"]
    if code >= 2:
        verdicts.append(("voices", "not run", "needs a cast in GLOSSARY.md"))

    report += ["## Still unmeasured\n",
               "Register, calques, verse and wordplay. No script reaches them.",
               "Dispatch the briefs in `references/reviewers.md` on the chapters",
               "flagged above, then record what was and was not reviewed.\n"]

    (project / "report.md").write_text("\n".join(report), encoding="utf-8")

    print(rule("summary"))
    marks = {"pass": "ok  ", "review": "?   ", "mixed": "?   ",
             "FAIL": "FAIL", "not run": " -- "}
    for name, verdict, detail in verdicts:
        print(f"  [{marks[verdict]}] {name:<14} {detail}")
    skipped = [n for n, v, _ in verdicts if v == "not run"]
    if skipped:
        print(f"\n  {len(skipped)} check(s) did not run: {', '.join(skipped)}")
        print("  A check that did not run is not a check that passed.")
    print(f"\n  report -> {project / 'report.md'}")
    print(f"  voices -> {voices}")
    print("\n  Not measured: register, calques, verse. Those need reading —")
    print("  see references/reviewers.md")
    return 1 if any(v == "FAIL" for _, v, _ in verdicts) else 0


# --------------------------------------------------------------------------


def cmd_review(args) -> int:
    project: Path = args.project
    if not (project / "profile.json").exists():
        print(f"error: {project} is not a project — run `init` first", file=sys.stderr)
        return 2

    print(rule("writing reviewer prompts"))
    code, out = run("make_reviews.py", "--project", str(project), "--draft", str(args.draft),
                    "--out", str(project / "reviews"), "--max-voices", str(args.max_voices))
    print(out.rstrip())
    if code:
        return code

    print(f"""
{'═' * 70}
Each prompt is self-contained. Run them in **separate sessions** — reviewers
sharing a context inherit each other's blind spots, which is the whole
reason for using several.

Before trusting the results, run the same prompts against a chapter of the
reference translation. Every finding there is a false positive by
construction, and the volume tells you which briefs over-fire.

Merging instructions: {project / 'reviews' / '_aggregate.md'}
{'═' * 70}""")
    return 0


# --------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init", help="set up a project from a reference translation")
    i.add_argument("--reference", type=Path, required=True, help="EPUB, FB2, or directory")
    i.add_argument("--project", type=Path, required=True)
    i.set_defaults(fn=cmd_init)

    c = sub.add_parser("check", help="check a draft against the project")
    c.add_argument("--project", type=Path, required=True)
    c.add_argument("--draft", type=Path, required=True)
    c.add_argument("--glob", default="*.txt", help="draft file pattern for delta/fingerprint")
    c.set_defaults(fn=cmd_check)

    r = sub.add_parser("review", help="write reviewer prompts for the axes no script reaches")
    r.add_argument("--project", type=Path, required=True)
    r.add_argument("--draft", type=Path, required=True)
    r.add_argument("--max-voices", type=int, default=8)
    r.set_defaults(fn=cmd_review)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
