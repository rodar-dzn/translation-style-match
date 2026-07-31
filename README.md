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

## Two commands

```bash
python tsm.py init   --reference book1.epub --project myproject/
python tsm.py check  --project myproject/ --draft draft/
python tsm.py review --project myproject/ --draft draft/
```

`init` extracts the reference, detects everything countable, derives
tolerances from the corpus's own chapter variation, finds the cast, and
scaffolds the glossary and style guide.

`check` runs every measurement and writes one report.

`review` writes self-contained prompts for the axes no script reaches — one
per character voice, plus calques, verse, glossary drift and narration.

What `init` settles unaided, with its counts recorded as evidence: script,
dialogue marker, quote characters, ellipsis form, foreign-token allowlist,
and the recurring cast. On a real novel it picked the en dash from 5435
occurrences against 110 guillemets, determined that quotes are not used in
speech (1.3% of dialogue paragraphs), built a 34-word French allowlist, and
found 30 speakers from dialogue tags alone.

What it cannot settle, and says so: register, voice, neologism formation.
Leave the style guide empty and the voice reviewers will refuse to report
rather than invent findings.

The scripts in `scripts/` remain usable on their own; `tsm.py` only spares
you the flags.

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
| `detect_profile.py` | reads the reference and writes `profile.json` from what it counts, with the counts kept as evidence |
| `detect_cast.py` | finds the recurring cast from dialogue tags — a name in the narration half of a speech paragraph is almost always a speaker, in any language |
| `make_reviews.py` | writes self-contained reviewer prompts from the project's own data |
| `delta.py` | Burrows's Delta over function-word frequencies — whether the text reads as the same hand at all |
| `inject_faults.py` | plants known defects and scores what the checker caught — recall, the half that calibration does not measure |

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
attribution rate measures the script, not the prose — on real novel prose it
runs around 40%, against 80% on clean synthetic text.

Name matching is literal substring matching, which handles suffixing
languages by accident rather than by design: an inflected form usually
contains the nominative as a prefix, so it matches, but stem alternations
break it and inflected variants can register as separate speakers. Proper
morphological handling is an open contribution.

---

## Validation

Run on a real two-volume novel pair sharing one translator, with a
third-party rough translation of the same book as a negative control. The
profile was built from **volume 1 only**; volume 2 and the draft were then
scored against it.

| Target | Truth | `fingerprint.py` | `delta.py` |
|---|---|---|---|
| Volume 2 | same translator | passed | 13% of chapters flagged |
| Rough draft | different translator | **passed** | 97% of chapters flagged |

**`fingerprint.py` failed the discrimination test.** The draft came out
statistically indistinguishable from the reference, and on several metrics
it scored *closer* than the genuine second volume did. The diagnosis: mean
sentence length, paragraph length and dialogue ratio largely track the
**source** text's structure, which survives translation regardless of who
translated it. Those metrics were measuring the author, not the translator.

`delta.py` — Burrows's Delta over function-word frequencies — separates them
cleanly, 13% against 97%.

Use `fingerprint.py` to find *which axis* diverges and by how much. Use
`delta.py` to answer whether the text reads as the same hand at all. The
first is diagnostic, not discriminative, and the table above is why.

The same run surfaced a bug: extracted books carry title pages and section
dividers, whose unstable statistics inflated derived tolerances until
nothing could ever be flagged — the foreign-token tolerance came out at
890% before fragments under 500 words were excluded, and 103% after.

**This is one book pair in one language.** It is the difference between no
evidence and one data point, not between no evidence and a validated tool.

## Target languages

| File | Marks dialogue with | Notable |
|---|---|---|
| `ru.md` | dash — three confusable characters | Church Slavonic stratum; productive obscenity |
| `pl.md` | dash, **no comma** before the tag | seven cases incl. vocative; aspect pairs |
| `es.md` | raya, **no space** after it | `tú`/`vos`/`usted`/`vosotros`; inverted `¿¡` |
| `it.md` | caporali **or** dashes | passato remoto is regional as well as literary |
| `fr.md` | guillemets enclosing the exchange, **or** dashes | passé simple as register; narrow no-break spaces |
| `de.md` | **quotation marks**, not dashes | Konjunktiv I for reported speech; modal particles |
| `ja.md` | `「 」` | script mixing as register; pronouns as characterization |
| `mg.md` | typography **unverified** — see the file | VOS order; voice system and its extraction restriction; 1835 Bible as the elevated stratum |

The set is deliberately typologically mixed. German marks dialogue with
quotation marks, Japanese has no word spaces at all, and Malagasy is
verb-initial — if the six axes survive those, they generalize.

Two honest limitations, documented in the files themselves:

- **Shared script kills two linter checks.** English→French, →Spanish,
  →German, →Italian and →Polish all put source and target in Latin script,
  so `mixed-script` cannot fire and unlisted-foreign detection cannot tell a
  retained word from an ordinary one. Set `flag_unlisted_foreign: false` and
  treat the foreign layer as a reading axis.
- **Japanese breaks the word-based metrics.** No spaces means no word
  boundaries; `fingerprint.py`'s word counts do not transfer, and character
  count with kanji ratio would be the right measure. That is an open
  contribution.

`mg.md` is marked partially unverified on purpose: the linguistic sections
are solid, the typography section is a hypothesis to test against a corpus.
A file that looks authoritative and guesses is exactly what this skill warns
against, so it says so at the top instead.

`references/targets/_template.md` is the form for adding another. Pull
requests adding target languages are the most useful contribution — the core
is language-agnostic and only these files are not. Wanted:
Ukrainian, Portuguese, Turkish, Arabic, Chinese, Korean, Dutch, Czech.

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
