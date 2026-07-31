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

    print(rule("5/6  detecting the cast"))
    code, out = run("detect_cast.py", str(ref_text), "--profile", str(project / "profile.json"),
                    "--append", str(project / "GLOSSARY.md"), "--top", "30")
    print("\n".join(out.rstrip().split("\n")[:12]))
    if code:
        print("  (cast detection failed — fill the Characters section by hand)")
        return 0

    # Voice profiles must be measured on the reference, never on a draft:
    # the point is to record what the canon does, so a draft can be held to it.
    print(rule("6/6  measuring the voices"))
    code, out = run("split_dialogue.py", str(ref_text), "--profile", str(project / "profile.json"),
                    "--glossary", str(project / "GLOSSARY.md"),
                    "--out", str(project / "reference-voices"), "--glob", "*.txt", "--blind", "80")
    print("  " + out.strip().split("\n")[1] if len(out.strip().split("\n")) > 1 else out.strip())
    if code == 0:
        shutil.rmtree(project / "voices", ignore_errors=True)
        shutil.copytree(project / "reference-voices", project / "voices")
        code, out = run("profile_voices.py", "--project", str(project))
        shutil.rmtree(project / "voices", ignore_errors=True)
        print("\n".join(out.rstrip().split("\n")[2:]))

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


ENGINES = {
    # name: (executable, argv builder taking the prompt file)
    "claude": lambda p: ["claude", "-p", "--permission-mode", "bypassPermissions"],
    "ollama": lambda p: ["ollama", "run", "llama3.1"],
}


def execute_prompt(engine: str, prompt_file: Path, out_file: Path) -> tuple[int, str]:
    """Pipe a prompt through a locally installed CLI. No API keys, no SDK."""
    exe = shutil.which(engine)
    if not exe:
        return 2, f"{engine} not found on PATH"
    argv = ENGINES[engine](prompt_file)
    argv[0] = exe
    prompt = prompt_file.read_text(encoding="utf-8")
    try:
        proc = subprocess.run(argv, input=prompt, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=1800)
    except subprocess.TimeoutExpired:
        return 2, "timed out after 30 minutes"
    if proc.returncode:
        return proc.returncode, (proc.stderr or proc.stdout or "").strip()[:2000]
    text = (proc.stdout or "").strip()
    if not text:
        return 2, "engine returned nothing"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(text, encoding="utf-8")
    return 0, text


def cmd_translate(args) -> int:
    project: Path = args.project
    if not (project / "profile.json").exists():
        print(f"error: {project} is not a project — run `init` first", file=sys.stderr)
        return 2

    suffix = "-repair" if args.draft else ""
    out = args.out or (project / "prompts" / f"{args.source.stem}{suffix}.md")
    cmd = ["--project", str(project), "--source", str(args.source), "--out", str(out)]

    if args.lang:
        target = HERE / "references" / "targets" / f"{args.lang}.md"
        if target.exists():
            cmd += ["--target-file", str(target)]
        else:
            available = sorted(p.stem for p in (HERE / "references" / "targets").glob("*.md")
                               if not p.stem.startswith("_"))
            print(f"note: no reference file for {args.lang!r}. Available: {', '.join(available)}")

    if args.draft:
        cmd += ["--draft", str(args.draft)]
        lint = project / "lint.txt"
        code, lint_out = run("lint.py", str(args.draft), "--profile", str(project / "profile.json"),
                             "--glossary", str(project / "GLOSSARY.md"), "--level", "warning",
                             "--glob", "*")
        lint.write_text(lint_out, encoding="utf-8")
        cmd += ["--lint", str(lint)]

    print(rule("repair prompt" if args.draft else "translation prompt"))
    code, output = run("make_translation.py", *cmd)
    print(output.rstrip())
    if code:
        return code

    if not args.execute:
        print(f"""
{'═' * 70}
The prompt carries what the project measured: typography, the canonical
terms this passage actually needs, and the register profiles.

Round trip:
  1. hand {out.name} to a translator or model
     (or rerun with --execute to pipe it through a local CLI)
  2. save the result
  3. python tsm.py check --project {project} --draft <result>
  4. if it fails, rerun with --draft <result> for a repair prompt
     targeting only what broke
{'═' * 70}""")
        return 0

    # -- execute -----------------------------------------------------------
    engine = args.engine or next((e for e in ENGINES if shutil.which(e)), None)
    if not engine:
        print(f"error: no engine found. Install one of: {', '.join(ENGINES)}, "
              f"or drop --execute and hand the prompt over yourself", file=sys.stderr)
        return 2

    result = project / "output" / f"{args.source.stem}.md"
    print(rule(f"running through {engine}"))
    print(f"  this may take a while for a long passage")
    code, text = execute_prompt(engine, out, result)
    if code:
        print(f"  failed: {text}", file=sys.stderr)
        print(f"\n  the prompt is still at {out} — hand it over manually")
        return code
    print(f"  {len(text):,} chars -> {result}")

    # -- check what came back ---------------------------------------------
    print(rule("checking the result"))
    code, lint_out = run("lint.py", str(result), "--profile", str(project / "profile.json"),
                         "--glossary", str(project / "GLOSSARY.md"), "--level", "warning",
                         "--glob", "*")
    (project / "lint.txt").write_text(lint_out, encoding="utf-8")
    tail = lint_out.strip().split("\n")
    print("\n".join(tail[-4:]))

    print(f"\n{'═' * 70}")
    if code == 1:
        print(f"""Mechanical defects found. Build a repair prompt targeting only
what broke:

  python tsm.py translate --project {project} \\
      --source {args.source} --draft {result} --execute
""")
    else:
        print("No mechanical defects.")
    print(f"""Still unmeasured: register, voice, calques, verse. Those need reading:

  python tsm.py review --project {project} --draft {result.parent}

A clean lint means the typography and terms are right. It says nothing
about whether the voice matches — that is the axis that decides it, and no
script reaches it.
{'═' * 70}""")
    return 0


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

    t = sub.add_parser("translate", help="build a translation prompt carrying the project's conventions")
    t.add_argument("--project", type=Path, required=True)
    t.add_argument("--source", type=Path, required=True, help="source-language passage")
    t.add_argument("--out", type=Path, help="defaults to <project>/prompts/<name>.md")
    t.add_argument("--lang", help="target language code, to include references/targets/<lang>.md")
    t.add_argument("--draft", type=Path, help="existing draft — builds a repair prompt instead")
    t.add_argument("--execute", action="store_true",
                   help="pipe the prompt through a local CLI and check what comes back")
    t.add_argument("--engine", choices=sorted(ENGINES), help="which CLI (default: first found)")
    t.set_defaults(fn=cmd_translate)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
