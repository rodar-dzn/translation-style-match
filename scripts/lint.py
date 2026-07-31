#!/usr/bin/env python3
"""Mechanical style checks against a profile and glossary.

    python lint.py draft/ --profile profile.json --glossary GLOSSARY.md

Checks only what is unambiguous: dash characters, quotation marks in
speech, mixed-script words, unreviewed foreign tokens, glossary
violations, straight quotes, three-dot ellipses.

Everything else — register, calques, verse — needs a reading pass.
Exit code 1 if any error-level finding is present.

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

# Windows consoles default to a legacy codepage; without this, any output
# outside Latin-1 arrives as mojibake.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# --------------------------------------------------------------------------
# script detection

_SCRIPT_CACHE: dict[str, str] = {}


def char_script(ch: str) -> str:
    if ch in _SCRIPT_CACHE:
        return _SCRIPT_CACHE[ch]
    try:
        name = unicodedata.name(ch)
    except ValueError:
        script = "OTHER"
    else:
        script = name.split()[0] if name.split()[0] in ("LATIN", "CYRILLIC", "GREEK", "ARABIC", "HEBREW") else "OTHER"
    _SCRIPT_CACHE[ch] = script
    return script


WORD = re.compile(r"[^\W\d_]+", re.UNICODE)


def word_scripts(word: str) -> set[str]:
    return {s for s in (char_script(c) for c in word) if s != "OTHER"}


# --------------------------------------------------------------------------
# glossary


def load_glossary(path: Path) -> list[dict]:
    """Parse the markdown table in GLOSSARY.md.

    Expected columns: Source | Canonical | Reject | Status | Citation
    """
    entries = []
    if not path or not path.exists():
        return entries
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---") or set(line) <= set("|- :"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0].lower() in ("source", "исходник", "термин"):
            continue
        canonical = cells[1]
        if not canonical or canonical in ("—", "-"):
            continue
        reject = []
        if len(cells) > 2 and cells[2] not in ("", "—", "-"):
            reject = [v.strip() for v in re.split(r"[,;/]", cells[2]) if v.strip()]
        entries.append(
            {
                "source": cells[0],
                "canonical": canonical,
                "reject": reject,
                "status": cells[3].upper() if len(cells) > 3 else "",
            }
        )
    return entries


# --------------------------------------------------------------------------
# findings

class Finding:
    __slots__ = ("path", "line", "level", "code", "message", "span")

    def __init__(self, path, line, level, code, message, span=""):
        self.path, self.line, self.level = path, line, level
        self.code, self.message, self.span = code, message, span

    def render(self, root: Path) -> str:
        try:
            rel = self.path.relative_to(root)
        except ValueError:
            rel = self.path
        head = f"{rel}:{self.line}: {self.level}: [{self.code}] {self.message}"
        return f"{head}\n    {self.span}" if self.span else head


def excerpt(line: str, at: int, width: int = 60) -> str:
    start = max(0, at - width // 2)
    frag = line[start : start + width]
    return ("…" if start else "") + frag.strip() + ("…" if start + width < len(line) else "")


# --------------------------------------------------------------------------
# checks


def check_paragraph(par: str, lineno: int, path: Path, cfg: dict, glossary: list[dict]) -> list[Finding]:
    out = []
    dlg = cfg.get("dialogue", {})
    marker = dlg.get("marker", "")
    forbidden_markers = dlg.get("forbidden_markers", [])
    stripped = par.lstrip()

    # -- dialogue marker ---------------------------------------------------
    is_dialogue = bool(marker) and stripped.startswith(marker)
    for bad in forbidden_markers:
        if bad and stripped.startswith(bad):
            out.append(
                Finding(
                    path, lineno, "error", "dash",
                    f"paragraph opens with {bad!r} (U+{ord(bad[0]):04X}); profile requires "
                    f"{marker!r} (U+{ord(marker[0]):04X})",
                    excerpt(stripped, 0),
                )
            )
            is_dialogue = True
            break

    # dash characters used mid-paragraph where the profile forbids them
    if not dlg.get("allow_forbidden_markers_inline", True):
        for bad in forbidden_markers:
            idx = par.find(f" {bad} ")
            if idx >= 0:
                out.append(
                    Finding(path, lineno, "warning", "dash-inline",
                            f"{bad!r} used mid-paragraph", excerpt(par, idx))
                )

    # -- quotes inside speech ---------------------------------------------
    if is_dialogue and not dlg.get("quotes_in_speech", False):
        for q in dlg.get("quote_pair", []):
            idx = par.find(q)
            if idx >= 0:
                out.append(
                    Finding(path, lineno, "warning", "quotes-in-speech",
                            f"{q!r} inside a dialogue paragraph — legitimate only for a "
                            f"genuine quotation; review",
                            excerpt(par, idx))
                )
                break

    # -- forbidden quote characters ---------------------------------------
    for q in cfg.get("typography", {}).get("forbidden_quotes", []):
        idx = par.find(q)
        if idx >= 0:
            out.append(
                Finding(path, lineno, "error", "quote-char",
                        f"{q!r} (U+{ord(q[0]):04X}) is not used in this target's typeset prose",
                        excerpt(par, idx))
            )

    # -- forbidden literal sequences --------------------------------------
    for seq in cfg.get("typography", {}).get("forbidden_sequences", []):
        idx = par.find(seq)
        if idx >= 0:
            out.append(
                Finding(path, lineno, "error", "typography",
                        f"{seq!r} found; profile specifies a different form",
                        excerpt(par, idx))
            )

    # -- script checks -----------------------------------------------------
    fl = cfg.get("foreign_layer", {})
    allow = {w.lower() for w in fl.get("allowlist", [])}
    main_script = fl.get("main_script", "").upper()

    for m in WORD.finditer(par):
        word = m.group()
        scripts = word_scripts(word)
        if len(scripts) > 1:
            out.append(
                Finding(path, lineno, "error", "mixed-script",
                        f"{word!r} mixes {' + '.join(sorted(scripts))} in one word",
                        excerpt(par, m.start()))
            )
        elif (
            fl.get("flag_unlisted_foreign", False)
            and main_script
            and scripts
            and main_script not in scripts
            and word.lower() not in allow
            and len(word) > 1
        ):
            out.append(
                Finding(path, lineno, "info", "foreign-token",
                        f"{word!r} is not in the profile allowlist — intentional, or an "
                        f"untranslated leftover?",
                        excerpt(par, m.start()))
            )

    # -- glossary ----------------------------------------------------------
    for entry in glossary:
        for variant in entry["reject"]:
            for m in re.finditer(re.escape(variant), par):
                # skip when the hit is really the canonical form containing it
                if entry["canonical"] and entry["canonical"] in par[max(0, m.start() - 5) : m.end() + 5]:
                    continue
                out.append(
                    Finding(path, lineno, "error", "glossary",
                            f"{variant!r} -> canonical is {entry['canonical']!r}",
                            excerpt(par, m.start()))
                )
                break
    return out


def lint_file(path: Path, cfg: dict, glossary: list[dict]) -> list[Finding]:
    text = path.read_text(encoding="utf-8", errors="replace")
    out = []
    dlg = cfg.get("dialogue", {})
    marker = dlg.get("marker", "")
    lineno = 0
    prev_was_dialogue = False

    for raw in text.split("\n"):
        lineno += 1
        par = raw.strip()
        if not par:
            continue
        out.extend(check_paragraph(par, lineno, path, cfg, glossary))

        # continuation paragraphs: a speaker's turn running on should not
        # re-open with the marker
        if dlg.get("no_dash_on_continuation", False) and marker:
            if prev_was_dialogue and par.startswith(marker) and len(par) > 1 and par[1:2].islower():
                out.append(
                    Finding(path, lineno, "info", "continuation",
                            "opens with the dialogue marker but continues lowercase — "
                            "continuation paragraphs take no marker",
                            excerpt(par, 0))
                )
        prev_was_dialogue = bool(marker) and par.startswith(marker)
    return out


# --------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", type=Path, help="file or directory to lint")
    ap.add_argument("--profile", type=Path, default=Path("profile.json"))
    ap.add_argument("--glossary", type=Path, default=Path("GLOSSARY.md"))
    ap.add_argument("--level", choices=("error", "warning", "info"), default="info",
                    help="minimum level to report (default: info)")
    args = ap.parse_args()

    if not args.profile.exists():
        print(f"error: profile {args.profile} not found — copy "
              f"templates/profile.template.json and fill it from the corpus", file=sys.stderr)
        return 2
    cfg = json.loads(args.profile.read_text(encoding="utf-8"))
    glossary = load_glossary(args.glossary)

    files = (
        sorted(p for p in args.target.rglob(cfg.get("chapter_glob", "*.md")) if p.is_file())
        if args.target.is_dir()
        else [args.target]
    )
    if not files:
        print(f"error: no files matching {cfg.get('chapter_glob', '*.md')!r} under {args.target}",
              file=sys.stderr)
        return 2

    findings = []
    for f in files:
        findings.extend(lint_file(f, cfg, glossary))

    rank = {"error": 0, "warning": 1, "info": 2}
    cutoff = rank[args.level]
    shown = [f for f in findings if rank[f.level] <= cutoff]
    root = args.target if args.target.is_dir() else args.target.parent
    for f in shown:
        print(f.render(root))

    counts = {lvl: sum(1 for f in findings if f.level == lvl) for lvl in rank}
    print(
        f"\n{len(files)} files | {counts['error']} errors, "
        f"{counts['warning']} warnings, {counts['info']} info"
        + (f" | glossary: {len(glossary)} entries" if glossary else " | no glossary loaded")
    )
    if not glossary:
        print("note: without a glossary, term consistency is unchecked")
    return 1 if counts["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
