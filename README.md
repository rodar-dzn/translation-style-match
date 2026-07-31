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
git clone https://github.com/rodar-dzn/translation-style-match \
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

**4. Review.** Diff the whole-draft statistics to find where to look, split
the dialogue by speaker, then dispatch narrow reviewers.

```bash
python scripts/fingerprint.py draft/ --compare work/ref-fingerprint.json
python scripts/split_dialogue.py draft/ --profile profile.json \
    --glossary GLOSSARY.md --out work/voices/
```

`references/reviewers.md` holds the briefs — one per character voice, plus
marker drift, calques, verse, glossary drift and narration. Narrow
independent reviewers find more than one reviewer with a long checklist, and
the overlap between them works as a confidence filter.

Three rules make this worth doing rather than expensive:

- **The corpus outranks the reviewer's taste.** A finding that cannot cite
  what the reference translation does instead is an opinion, and it goes in
  the bin however well argued.
- **Gate the swarm** behind a clean lint and a read fingerprint. Run it on
  the chapters that earned it, not on the whole book.
- **Calibrate** by running the briefs against the reference translation
  itself. Every finding is a false positive by construction, which tells you
  which briefs over-fire.

---

## Tools

| Script | Does |
|---|---|
| `extract_corpus.py` | EPUB / FB2 / text → one plain file per chapter, spine order preserved |
| `build_glossary.py` | candidate terms from the source; aligned target spans when a bitext exists; `--confirm` to check a single rendering |
| `lint.py` | dash characters, quotes in speech, mixed-script words, unreviewed foreign tokens, glossary violations, typography |
| `fingerprint.py` | dialogue density, sentence length and variance, punctuation rates, foreign-token density, lexical variety — and a diff against a reference |
| `split_dialogue.py` | groups speech by speaker so each reviewer reads one voice, not the whole book; also generates the blind attribution test |

Alignment in `build_glossary.py` is positional and approximate on purpose.
It narrows the search to a readable handful of paragraph pairs; it does not
claim a match. Treat every pair as a lead.

Fingerprint divergences are signals, not verdicts. Uniform sentence length
is the classic signature of flattened register, and low lexical variety
suggests vocabulary collapsing toward the neutral stratum — but both need a
reading pass to confirm.

Speaker attribution in `split_dialogue.py` is heuristic: it reads the
narration tag for a known name and sends anything it cannot settle to
`_unattributed.txt` with surrounding context, for a person to assign. The
attribution rate measures the script, not the prose.

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

Built by Darya Romanenkova.
