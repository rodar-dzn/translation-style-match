# translation-style-match

Make a new translation read as though the same hand produced an existing one
— by **measuring** that translation instead of guessing at it.

Built for the case where a translation already exists and something new has
to sit beside it: a series whose translator changed mid-run, a localization
split across several people, a draft that has to pass review against a
published house style.

- **Extracts** a style profile and a citation-backed glossary from a
  reference translation, by counting rather than by assumption.
- **Produces** translation prompts carrying those conventions, optionally
  executing them through a local CLI.
- **Checks** what comes back — mechanically, statistically, and by
  dispatching narrow reviewers at the axes no script reaches.

No dependencies, no API keys, no network calls. Python 3.9+, standard
library only.

**The skill ships a method, not a corpus.** No book text lives in this
repository. Reference material stays on your machine, gitignored, and CI
fails the build if anything book-shaped is ever committed.

---

## Does it work?

Partly, and the parts are documented. See **[LIMITATIONS.md](LIMITATIONS.md)**
for prior art, known weaknesses, and what remains unevidenced.

Validation run: a two-volume novel sharing one translator, plus a third
party's rough translation of the same book as a negative control. Profile
built from **volume 1 only**.

| Target | Truth | `fingerprint.py` | `delta.py` |
|---|---|---|---|
| Volume 2 | same translator | passed | 13% of chapters flagged |
| Rough draft | different translator | **passed** | 97% of chapters flagged |

`fingerprint.py` failed the discrimination test and was demoted to
diagnostic. Sentence and paragraph statistics track the *source* text's
structure, which survives translation whoever performs it — they were
measuring the author, not the translator. `delta.py` (Burrows's Delta over
function-word frequencies) separates them.

**One book pair in one language.** The difference between no evidence and
one data point. The reviewer swarm — the central function — has never been
run on real material at all.

---

## Install

```bash
git clone https://github.com/rodar-dzn/translation-style-match \
  ~/.claude/skills/translation-style-match
```

Usable as a Claude Code skill (`/translation-style-match`) or as a
standalone command-line tool.

---

## Quickstart

```bash
python tsm.py init      --reference reference-volume.epub --project myproject/
python tsm.py translate --project myproject/ --source chapter.txt --lang ru --execute
python tsm.py check     --project myproject/ --draft myproject/output/
python tsm.py review    --project myproject/ --draft myproject/output/
```

**`init`** reads the reference and settles everything countable, keeping the
counts as evidence: script, dialogue marker, quote characters, ellipsis
form, foreign-token allowlist, the recurring cast, and a measured voice
profile per character. It also derives tolerances from the corpus's own
chapter-to-chapter variation.

On a real novel it picked the en dash from 5435 occurrences against 110
guillemets, determined quotes are not used in speech (1.3% of dialogue
paragraphs), built a 34-word French allowlist, found 30 speakers from
dialogue tags, and profiled 10 voices — unaided.

**`translate`** assembles a prompt from those conventions. What makes it
more than a wrapper is pre-resolution: the source passage is scanned against
the glossary and only the terms actually present are included, so a
translator gets the six terms this page needs rather than a four-hundred-row
table it will skim. `--execute` pipes it through a locally installed CLI
(`claude` or `ollama`, auto-detected) and lints the result. Passing
`--draft` builds a repair prompt targeting only what broke.

**`check`** runs every measurement and writes one report.

**`review`** writes self-contained reviewer prompts for the axes no script
reaches.

The scripts in `scripts/` remain usable on their own; `tsm.py` only spares
you the flags.

---

## How it works

Style decomposes into six axes that fail independently and need different
amounts of attention:

| Axis | Caught by | Effort |
|---|---|---|
| Dialogue typography | linter | trivial once profiled |
| Foreign layer | linter (partly) | low |
| Onomastics and coined terms | linter, via glossary | medium — the lookups |
| **Register and voice** | **measurement + reading** | **most of the budget** |
| Calques | reading only | medium |
| Neologism formation | glossary review | low |

The tooling clears the cheap axes so attention goes where it decides the
outcome — voice.

Three rules govern everything:

- **The corpus outranks your taste.** A finding that cannot cite what the
  reference does instead is an opinion. It goes in the bin.
- **Verify before you invent.** Most apparent gaps are terms the corpus does
  render, under a phrasing nobody predicted.
- **Declare gaps, never fill them plausibly.** A reference file that looks
  authoritative while guessing is the failure this project exists to prevent.

### Defeating the average

Asked to "translate in this style", a model produces its *average* notion of
good literary prose. That flattening is the whole problem.

`profile_voices.py` measures deviation from the average directly, using
**keyness** — Dunning log-likelihood of each character's vocabulary against
the pooled speech of everyone else. A marker word belongs to a speaker
rather than a subject, and it surfaces without any word list or
per-language configuration.

What measurement cannot do is *name* the stratum. The keyword list makes
that a glance rather than an investigation, and it is the only handwork
left.

---

## Tools

| Script | Does |
|---|---|
| `extract_corpus.py` | EPUB / FB2 / text → one plain file per chapter, spine order preserved |
| `detect_profile.py` | writes `profile.json` from what it counts, with the counts kept as evidence |
| `detect_cast.py` | finds the recurring cast from dialogue tags — a name in the narration half of a speech paragraph is almost always a speaker, in any language |
| `profile_voices.py` | per-character sentence shape, punctuation, address, and keyness |
| `build_glossary.py` | candidate terms; aligned target spans when a bitext exists; `--confirm` to check one rendering |
| `make_translation.py` | translation and repair prompts with glossary terms pre-resolved |
| `delta.py` | Burrows's Delta — whether the text reads as the same hand at all |
| `fingerprint.py` | dialogue density, sentence length, punctuation rates, foreign-token density — diagnostic, not discriminative |
| `lint.py` | dash characters, quotes in speech, mixed-script words, glossary violations, typography |
| `split_dialogue.py` | groups speech by speaker; generates the blind attribution test |
| `make_reviews.py` | self-contained reviewer prompts from the project's own data |
| `inject_faults.py` | plants known defects and scores what the checker caught |

---

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
| `mg.md` | typography **unverified** | VOS order; voice system's extraction restriction |

Deliberately typologically mixed. German marks dialogue with quotation
marks, Japanese has no word spaces, Malagasy is verb-initial — if the six
axes survive those, they generalize.

`_template.md` is the form for adding another. Pull requests adding target
languages are the most useful contribution: the core is language-agnostic
and only these files are not. Wanted: Ukrainian, Portuguese, Turkish,
Arabic, Chinese, Korean, Dutch, Czech.

Every rule in a target file is a **default to check against**, never a
specification to impose. Published translations deviate deliberately, and
the corpus always wins.

---

## Scope

Use on text you have the right to produce: your own work, licensed or
commissioned work, public domain, or in-house localization. The corpus
guards in `.gitignore` and CI exist to keep the project from drifting into
a pipeline for unauthorized editions.

---

## License

MIT for the code. `references/` is CC-BY-4.0 — use the method, credit the
source.

Built by Darya Romanenkova.
