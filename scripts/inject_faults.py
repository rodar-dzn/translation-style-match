#!/usr/bin/env python3
"""Negative controls: plant known defects, then measure how many were caught.

    # 1. corrupt a clean chapter and record what was done
    python inject_faults.py work/ref/ --profile profile.json \
        --glossary GLOSSARY.md --out work/faults/ --n 25 --seed 1

    # 2. run the checker against the corrupted copy
    python lint.py work/faults/ --profile profile.json \
        --glossary GLOSSARY.md > work/faults/lint.txt

    # 3. score recall
    python inject_faults.py --score work/faults/_key.json \
        --against work/faults/lint.txt

Calibration in `references/reviewers.md` measures **precision** — run the
reviewers on the reference translation, where every finding is a false
positive by construction. This measures the other half: **recall**. A
checker that never fires looks perfect until you ask what it missed.

Scope, stated plainly: only mechanical faults can be planted by script.
Register flattening, calques and broken wordplay have to be written by a
person or a model, and this harness cannot generate them. It measures
`lint.py` well and the reviewer swarm only partially. Use `--manual` to
reserve slots for hand-written defects and fold them into the same key.

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

WORD = re.compile(r"[^\W\d_]+", re.UNICODE)


def load_glossary(path: Path) -> list[dict]:
    entries = []
    if not path or not path.exists():
        return entries
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s.startswith("|") or set(s) <= set("|- :"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 3 or cells[0].lower() in ("source", "исходник", "термин"):
            continue
        reject = [v.strip() for v in re.split(r"[,;/]", cells[2]) if v.strip()]
        if cells[1] and reject:
            entries.append({"canonical": cells[1], "reject": reject})
    return entries


# --------------------------------------------------------------------------
# fault types. each returns (new_line, description) or None if inapplicable.

def f_dash(line: str, cfg: dict, rng, gloss) -> tuple[str, str] | None:
    dlg = cfg.get("dialogue", {})
    marker, bad = dlg.get("marker"), dlg.get("forbidden_markers") or []
    if not marker or not bad or not line.lstrip().startswith(marker):
        return None
    return line.replace(marker, rng.choice(bad), 1), "dialogue marker swapped"


def f_quotes(line: str, cfg: dict, rng, gloss) -> tuple[str, str] | None:
    dlg = cfg.get("dialogue", {})
    marker, pair = dlg.get("marker"), dlg.get("quote_pair") or []
    if not marker or len(pair) < 2 or not line.lstrip().startswith(marker):
        return None
    body = line.lstrip()[len(marker):].strip()
    if not body:
        return None
    head = body.split(marker)[0].strip().rstrip(",.!?")
    if len(head) < 4:
        return None
    return line.replace(head, f"{pair[0]}{head}{pair[1]}", 1), "speech wrapped in quotes"


def f_ellipsis(line: str, cfg: dict, rng, gloss) -> tuple[str, str] | None:
    if "…" not in line:
        return None
    return line.replace("…", "...", 1), "typographic ellipsis -> three dots"


def f_glossary(line: str, cfg: dict, rng, gloss) -> tuple[str, str] | None:
    hits = [e for e in gloss if e["canonical"] in line]
    if not hits:
        return None
    e = rng.choice(hits)
    wrong = rng.choice(e["reject"])
    return line.replace(e["canonical"], wrong, 1), f"canonical {e['canonical']!r} -> {wrong!r}"


LATIN_SPLICE = ("tion", "ing", "ment", "ous")


def f_mixed_script(line: str, cfg: dict, rng, gloss) -> tuple[str, str] | None:
    main = cfg.get("foreign_layer", {}).get("main_script", "").upper()
    if main != "CYRILLIC":
        return None
    words = [m for m in WORD.finditer(line) if len(m.group()) > 6]
    if not words:
        return None
    m = rng.choice(words)
    w = m.group()
    spliced = w[: len(w) // 2] + rng.choice(LATIN_SPLICE) + w[len(w) // 2 :]
    return line[: m.start()] + spliced + line[m.end() :], f"mixed-script word {spliced!r}"


def f_straight_quote(line: str, cfg: dict, rng, gloss) -> tuple[str, str] | None:
    pair = cfg.get("dialogue", {}).get("quote_pair") or []
    if len(pair) < 2 or pair[0] not in line:
        return None
    return line.replace(pair[0], '"', 1).replace(pair[1], '"', 1), "typographic -> straight quotes"


FAULTS = {
    "dash": (f_dash, "dialogue-typography"),
    "quotes-in-speech": (f_quotes, "dialogue-typography"),
    "typography": (f_ellipsis, "typography"),
    "glossary": (f_glossary, "onomastics"),
    "mixed-script": (f_mixed_script, "foreign-layer"),
    "quote-char": (f_straight_quote, "typography"),
}


# --------------------------------------------------------------------------


def inject(args) -> int:
    cfg = json.loads(args.profile.read_text(encoding="utf-8"))
    gloss = load_glossary(args.glossary)
    rng = random.Random(args.seed)

    glob = cfg.get("chapter_glob", "*.md")
    files = sorted(p for p in args.target.rglob(glob) if p.is_file()) if args.target.is_dir() else [args.target]
    if not files:
        print(f"error: no files matching {glob!r} under {args.target}", file=sys.stderr)
        return 2

    args.out.mkdir(parents=True, exist_ok=True)
    kinds = [k for k in FAULTS if k not in (args.exclude or "").split(",")]
    if not gloss and "glossary" in kinds:
        kinds.remove("glossary")
        print("note: no glossary rejections available — skipping glossary faults")

    key, planted = [], 0
    for f in files:
        lines = f.read_text(encoding="utf-8", errors="replace").split("\n")
        budget = max(1, args.n // len(files))
        candidates = [i for i, ln in enumerate(lines) if len(ln.strip()) > 20]
        rng.shuffle(candidates)

        used = 0
        for idx in candidates:
            if used >= budget:
                break
            rng.shuffle(kinds)
            for kind in kinds:
                fn, axis = FAULTS[kind]
                result = fn(lines[idx], cfg, rng, gloss)
                if result:
                    new, desc = result
                    key.append({
                        "file": f.name, "line": idx + 1, "code": kind,
                        "axis": axis, "description": desc,
                        "original": lines[idx].strip()[:120],
                    })
                    lines[idx] = new
                    used += 1
                    planted += 1
                    break

        (args.out / f.name).write_text("\n".join(lines), encoding="utf-8")

    for i in range(args.manual):
        key.append({
            "file": "MANUAL", "line": 0, "code": "manual",
            "axis": "register|calque|verse",
            "description": f"slot {i + 1}: write a defect by hand and record it here",
            "original": "",
        })

    (args.out / "_key.json").write_text(
        json.dumps({"planted": planted, "manual_slots": args.manual, "faults": key},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    by_axis: dict[str, int] = {}
    for k in key:
        if k["code"] != "manual":
            by_axis[k["axis"]] = by_axis.get(k["axis"], 0) + 1

    print(f"planted {planted} faults across {len(files)} files -> {args.out}")
    for axis, n in sorted(by_axis.items()):
        print(f"  {axis:24} {n}")
    if args.manual:
        print(f"  {args.manual} manual slot(s) reserved in _key.json")
    print("\nonly mechanical faults are scriptable; register and calque defects")
    print("must be written by hand into the manual slots")
    return 0


LINT_LINE = re.compile(r"^(?P<file>[^:]+):(?P<line>\d+):\s+\w+:\s+\[(?P<code>[\w-]+)\]")


def score(args) -> int:
    data = json.loads(args.score.read_text(encoding="utf-8"))
    faults = [f for f in data["faults"] if f["code"] != "manual"]
    if not faults:
        print("no scriptable faults in key", file=sys.stderr)
        return 2

    found = set()
    for raw in args.against.read_text(encoding="utf-8", errors="replace").split("\n"):
        m = LINT_LINE.match(raw.strip())
        if m:
            found.add((Path(m.group("file")).name, int(m.group("line"))))

    caught = [f for f in faults if (f["file"], f["line"]) in found]
    missed = [f for f in faults if (f["file"], f["line"]) not in found]

    by_axis: dict[str, list[int]] = {}
    for f in faults:
        hit = 1 if (f["file"], f["line"]) in found else 0
        by_axis.setdefault(f["axis"], [0, 0])
        by_axis[f["axis"]][0] += hit
        by_axis[f["axis"]][1] += 1

    print(f"recall: {len(caught)}/{len(faults)} = {len(caught) / len(faults):.0%}\n")
    print(f"{'axis':24} {'caught':>8} {'planted':>8}")
    print("-" * 42)
    for axis, (hit, total) in sorted(by_axis.items()):
        flag = "  <-- " if hit < total else ""
        print(f"{axis:24} {hit:>8} {total:>8}{flag}")

    if missed:
        print(f"\nmissed {len(missed)}:")
        for f in missed[:20]:
            print(f"  {f['file']}:{f['line']} [{f['code']}] {f['description']}")
        if len(missed) > 20:
            print(f"  … and {len(missed) - 20} more")

    if data.get("manual_slots"):
        print(f"\n{data['manual_slots']} manual slot(s) not scored — "
              f"register and calque recall must be judged by reading")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", type=Path, nargs="?", help="clean text to corrupt")
    ap.add_argument("--profile", type=Path, default=Path("profile.json"))
    ap.add_argument("--glossary", type=Path, default=Path("GLOSSARY.md"))
    ap.add_argument("--out", type=Path)
    ap.add_argument("--n", type=int, default=20, help="faults to plant (default 20)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--exclude", help="comma-separated fault codes to skip")
    ap.add_argument("--manual", type=int, default=0, help="reserve N slots for hand-written defects")
    ap.add_argument("--score", type=Path, help="_key.json to score")
    ap.add_argument("--against", type=Path, help="checker output to score against")
    args = ap.parse_args()

    if args.score:
        if not args.against:
            print("error: --score needs --against", file=sys.stderr)
            return 2
        return score(args)

    if not args.target or not args.out:
        print("error: give a target and --out, or use --score", file=sys.stderr)
        return 2
    if not args.profile.exists():
        print(f"error: profile {args.profile} not found", file=sys.stderr)
        return 2
    return inject(args)


if __name__ == "__main__":
    raise SystemExit(main())
