#!/usr/bin/env python3
"""Convert EPUB / FB2 / plain text into one plain-text file per chapter.

Corpus files stay wherever the user put them; output goes to a working
directory that should be gitignored.

    python extract_corpus.py corpus/book.epub --out work/ref/
    python extract_corpus.py corpus/book.fb2  --out work/src/
    python extract_corpus.py corpus/chapters/ --out work/src/

Stdlib only.
"""

from __future__ import annotations

import argparse
import html
import os
import posixpath
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

BLOCK_END = re.compile(
    r"</(p|div|h[1-6]|li|tr|blockquote|section|br|title|subtitle)\s*>|<br\s*/?>",
    re.I,
)
TAG = re.compile(r"<[^>]+>")
DROP = re.compile(r"<(script|style|head)\b.*?</\1\s*>", re.I | re.S)
WS_RUNS = re.compile(r"[ \t ]+")
BLANKS = re.compile(r"\n{3,}")


def html_to_text(markup: str) -> str:
    """Strip markup, preserving block boundaries as newlines."""
    markup = DROP.sub(" ", markup)
    markup = BLOCK_END.sub("\n", markup)
    text = TAG.sub("", markup)
    text = html.unescape(text)
    text = WS_RUNS.sub(" ", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    return BLANKS.sub("\n\n", text).strip()


def epub_spine(zf: zipfile.ZipFile) -> list[str]:
    """Document paths in reading order, per the OPF spine."""
    try:
        container = zf.read("META-INF/container.xml").decode("utf-8", "replace")
    except KeyError:
        return sorted(n for n in zf.namelist() if n.lower().endswith((".xhtml", ".html", ".htm")))

    m = re.search(r'full-path="([^"]+)"', container)
    if not m:
        return []
    opf_path = m.group(1)
    opf = zf.read(opf_path).decode("utf-8", "replace")
    base = posixpath.dirname(opf_path)

    ids = dict(re.findall(r'<item\b[^>]*?id="([^"]+)"[^>]*?href="([^"]+)"', opf))
    ids.update(
        (i, h) for h, i in re.findall(r'<item\b[^>]*?href="([^"]+)"[^>]*?id="([^"]+)"', opf)
    )

    order = re.findall(r'<itemref\b[^>]*?idref="([^"]+)"', opf)
    out = []
    for ref in order:
        href = ids.get(ref)
        if not href:
            continue
        href = html.unescape(href.split("#")[0])
        out.append(posixpath.normpath(posixpath.join(base, href)) if base else href)
    return out


def from_epub(path: Path) -> list[tuple[str, str]]:
    chapters = []
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        for i, doc in enumerate(epub_spine(zf), 1):
            if doc not in names:
                continue
            text = html_to_text(zf.read(doc).decode("utf-8", "replace"))
            if len(text) < 40:
                continue
            chapters.append((f"{i:04d}_{Path(doc).stem}", text))
    return chapters


def _fb2_text(node: ET.Element) -> str:
    """Flatten an FB2 element, one paragraph per <p>."""
    parts = []
    for el in node.iter():
        tag = el.tag.rsplit("}", 1)[-1]
        if tag in ("p", "v", "subtitle", "text-author"):
            parts.append("".join(el.itertext()).strip())
        elif tag in ("empty-line", "stanza"):
            parts.append("")
    return BLANKS.sub("\n\n", "\n\n".join(parts)).strip()


def from_fb2(path: Path) -> list[tuple[str, str]]:
    root = ET.fromstring(path.read_text(encoding="utf-8", errors="replace"))
    ns = {"f": root.tag.split("}")[0].strip("{")} if "}" in root.tag else {}
    body = root.find("f:body", ns) if ns else root.find("body")
    if body is None:
        return [(path.stem, _fb2_text(root))]

    sections = body.findall("f:section", ns) if ns else body.findall("section")
    if not sections:
        return [(path.stem, _fb2_text(body))]

    chapters = []
    for i, sec in enumerate(sections, 1):
        title_el = sec.find("f:title", ns) if ns else sec.find("title")
        title = " ".join("".join(title_el.itertext()).split()) if title_el is not None else ""
        slug = re.sub(r"[^\w\- ]", "", title)[:50].strip().replace(" ", "_") or "section"
        text = _fb2_text(sec)
        if len(text) >= 40:
            chapters.append((f"{i:04d}_{slug}", text))
    return chapters


def from_dir(path: Path) -> list[tuple[str, str]]:
    out = []
    for i, f in enumerate(sorted(path.iterdir()), 1):
        if f.suffix.lower() in (".txt", ".md") and f.is_file():
            out.append((f"{i:04d}_{f.stem}", f.read_text(encoding="utf-8", errors="replace").strip()))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path, help="EPUB, FB2, .txt/.md file, or directory")
    ap.add_argument("--out", type=Path, required=True, help="output directory")
    ap.add_argument("--joined", action="store_true", help="also write _all.txt")
    args = ap.parse_args()

    src: Path = args.input
    if not src.exists():
        print(f"error: {src} not found", file=sys.stderr)
        return 1

    suffix = src.suffix.lower()
    if src.is_dir():
        chapters = from_dir(src)
    elif suffix == ".epub":
        chapters = from_epub(src)
    elif suffix == ".fb2":
        chapters = from_fb2(src)
    elif suffix in (".txt", ".md"):
        chapters = [(src.stem, src.read_text(encoding="utf-8", errors="replace").strip())]
    else:
        print(f"error: unsupported format {suffix!r}", file=sys.stderr)
        return 1

    if not chapters:
        print("error: no chapters extracted", file=sys.stderr)
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    total = 0
    for name, text in chapters:
        (args.out / f"{name}.txt").write_text(text, encoding="utf-8")
        total += len(text)

    if args.joined:
        joined = "\n\n\n".join(t for _, t in chapters)
        (args.out / "_all.txt").write_text(joined, encoding="utf-8")

    print(f"{len(chapters)} chapters, {total:,} chars -> {args.out}")
    print("reminder: keep this directory out of version control")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
