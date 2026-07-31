# translation-style-match

A Claude Code skill for making a new translation read as though the same
hand produced an existing one — by **measuring** that translation instead of
guessing at it.

Built for the situation where a translation already exists and something new
has to sit beside it: a series whose translator changed mid-run, a
localization split across several people, a draft that has to pass review
against a published house style.

**The skill ships a method, not a corpus.** No book text lives in this
repository. You point the tools at your own files locally; they stay
gitignored, and CI fails the build if anything book-shaped is ever
committed.

---

## Install

```bash
git clone https://github.com/<you>/translation-style-match \
  ~/.claude/skills/translation-style-match
```

Then invoke it in Claude Code as `/translation-style-match`, or just
describe the task — the skill's description triggers on style-matching,
translation-consistency and glossary work.

Python 3.9+, standard library only. No dependencies, no network calls.

---

## What it does

Style is not one thing. It decomposes into six axes that fail
independently, are fixed by different means, and need different amounts of
attention:

| Axis | Caught by | Effort |
|---|---|---|
| Dialogue typography | linter | trivial once profiled |
| Foreign layer | linter (partly) | low |
| Onomastics and coined terms | linter, via glossary | medium — the lookups |
| **Register and voice** | **reading only** | **most of the budget** |
| Calques | reading only | medium |
| Neologism formation | glossary review | low |

The tooling exists to clear the first three cheaply so that human attention
goes where it actually decides the outcome — voice.

---

## Workflow

**1. Profile.** Convert the reference translation to plain text, measure it,
and write down what it does.

```bash
python scripts/extract_corpus.py corpus/reference.epub --out work/ref/
python scripts/fingerprint.py work/ref/ --out work/ref-fingerprint.json
```

Then fill `templates/STYLEGUIDE.template.md` by reading the corpus. Every
claim cites a span you actually read.

**2. Glossary.** Names and coined terms are where mismatch shows first.

```bash
python scripts/build_glossary.py --source work/src/ --target work/ref/ \
    --out work/candidates.md

# check one suspected rendering
python scripts/build_glossary.py --target work/ref/ --confirm "term"
```

The rule the skill enforces: **verify before you invent.** Most apparent
gaps are terms the corpus does render, under a phrasing nobody predicted.

**3. Lint.** Clear the mechanical layer.

```bash
python scripts/lint.py draft/ --profile profile.json --glossary GLOSSARY.md
```

**4. Review.** Read for what tools cannot see, and diff the whole-draft
statistics.

```bash
python scripts/fingerprint.py draft/ --compare work/ref-fingerprint.json
```

---

## Tools

| Script | Does |
|---|---|
| `extract_corpus.py` | EPUB / FB2 / text → one plain file per chapter, spine order preserved |
| `build_glossary.py` | candidate terms from the source; aligned target spans when a bitext exists; `--confirm` to check a single rendering |
| `lint.py` | dash characters, quotes in speech, mixed-script words, unreviewed foreign tokens, glossary violations, typography |
| `fingerprint.py` | dialogue density, sentence length and variance, punctuation rates, foreign-token density, lexical variety — and a diff against a reference |

Alignment in `build_glossary.py` is positional and approximate on purpose.
It narrows the search to a readable handful of paragraph pairs; it does not
claim a match. Treat every pair as a lead.

Fingerprint divergences are signals, not verdicts. Uniform sentence length
is the classic signature of flattened register, and low lexical variety
suggests vocabulary collapsing toward the neutral stratum — but both need a
reading pass to confirm.

---

## Target languages

`references/targets/ru.md` covers Russian in detail: dialogue dashes and
which of the three confusable characters to use, quotation nesting,
vocabulary strata, and the traps specific to translating into Russian from
English.

`references/targets/_template.md` is the form for adding another. Pull
requests adding target languages are the most useful contribution — the
core is language-agnostic and only these files are not.

Every rule in a target file is a **default to check against**, never a
specification to impose. Published translations deviate deliberately, and
the corpus always wins.

---

## Scope

Use on text you have the right to produce: your own work, licensed or
commissioned work, public domain, or in-house localization. The skill is
built for consistency and review; it is not a pipeline for producing
unauthorized editions, and the corpus guards in `.gitignore` and CI are
there to keep it from drifting into one.

---

## License

MIT for the code. `references/` is CC-BY-4.0 — use the method, credit the
source.
