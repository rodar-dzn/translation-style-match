---
name: translation-style-match
description: When a new translation must match an existing one — continuing a series whose translator changed, harmonizing several translators into one voice, or auditing a draft against a published style. Also use when the user mentions "match the translation style", "same style as the official translation", "translation consistency", "style guide from corpus", "glossary from corpus", "stylistic audit", "перевести в том же стиле", "свести переводчиков", or "стилевой аудит". Builds a style profile and a citation-backed glossary from a reference corpus, then lints and reviews new text against them.
---

# Translation style matching

Make a new translation read as though the same hand produced it, by
measuring an existing translation instead of guessing at it.

## Scope

Use on text the user has the right to produce: their own work, licensed or
commissioned work, public domain, or in-house localization. If the goal is a
complete unauthorized edition of a copyrighted book, say so plainly once and
offer the audit and style-guide work instead.

Reference corpora stay on the user's machine under `corpus/`, which is
gitignored. Never commit corpus material, and never paste long stretches of
it into chat — quote the short spans a finding rests on.

## The four phases

Run them in order. Each produces a file the later phases depend on.

### Phase 1 — Profile

Turn the reference translation into a written, checkable description.

1. Convert the user's reference files to plain text:
   ```bash
   python scripts/extract_corpus.py corpus/reference.epub --out work/ref/
   ```
   Handles EPUB, FB2, and plain text. One file per chapter, spine order
   preserved.

2. Measure it:
   ```bash
   python scripts/fingerprint.py work/ref/ --out work/ref-fingerprint.json
   ```

3. Read `references/axes.md`. Fill `templates/STYLEGUIDE.template.md` by
   sampling the corpus for each of the six axes. Every claim in the style
   guide must cite a span you actually read. A style guide written from
   assumption is worse than none — it launders guesses into rules.

4. Read `references/targets/<lang>.md` for the target language's typographic
   conventions, and confirm each one against the corpus rather than
   assuming the corpus follows them. Published translations deviate.

5. Write `profile.json` from `templates/profile.template.json`, filling in
   what you confirmed. This is what the linter enforces.

### Phase 2 — Glossary

Names and coined terms are where a mismatch is spotted fastest, and they
are the cheapest thing to get right.

```bash
python scripts/build_glossary.py --source work/src/ --target work/ref/ \
    --out work/candidates.md
```

The script extracts candidate terms from the source and, when a bitext is
available, surfaces the aligned target paragraphs for each. It does not
decide the rendering — you do, by reading the aligned spans.

For each candidate, record the outcome in `GLOSSARY.md`:

- **CANON** — found in the reference corpus. Record the rendering and where
  you found it. This is the default and it is binding.
- **NEW** — the corpus is silent. Only now may you coin something, and it
  must follow the morphological pattern of neighbouring CANON entries.
  Record which entries you patterned it on.
- **OPEN** — unresolved. Flag it to the user rather than silently guessing.

The rule that matters: **verify before you invent.** Most apparent gaps are
terms the corpus does render, elsewhere, under a phrasing you did not
predict. Search the corpus for plausible variants before declaring NEW.

### Phase 3 — Lint

```bash
python scripts/lint.py draft/ --profile profile.json --glossary GLOSSARY.md
```

Catches what is mechanical and unambiguous: wrong dash characters, quotation
marks inside speech, mixed-script words, unreviewed foreign tokens, glossary
violations, straight quotes, three-dot ellipses.

Fix every error before spending attention on the reading pass. Mechanical
noise masks real problems, and it is the layer readers notice first.

### Phase 4 — Review

What the linter cannot see must be read for. This is the phase that decides
the outcome: phases 1–3 get a draft to *plausible*, and only this one gets it
to *indistinguishable*.

First, ask whether the draft reads as the same hand at all:

```bash
python scripts/delta.py --reference work/ref/ --test draft/
```

Burrows's Delta over function-word frequencies. On the validation run in
`README.md` this separated a same-translator volume from a different
translator's draft at 13% against 97% of chapters flagged.

Then find out *where* to look:

```bash
python scripts/fingerprint.py draft/ --compare work/ref-fingerprint.json
```

Divergences point at categories of problem that reading one chapter never
reveals. Treat this as diagnostic, not discriminative — the same validation
run showed it cannot tell translators apart, because sentence and paragraph
statistics largely track the source text's structure rather than the
translator's habits.

Then split the dialogue, so each reviewer gets a compact input instead of the
whole book:

```bash
python scripts/split_dialogue.py draft/ --profile profile.json \
    --glossary GLOSSARY.md --out work/voices/
```

This also writes `blind-test.txt` and its key — the flattening test from
`references/register.md`. Run it on the reference corpus too; the gap between
the two scores is the size of the problem.

Now dispatch reviewers. Read `references/reviewers.md` for the briefs: one
per character voice, plus marker drift, calques, verse, glossary drift and
narration. Narrow independent briefs find more than one reviewer with a long
checklist, and their overlap doubles as a confidence filter.

Three things govern this phase, and all three are in `reviewers.md`:

- **The corpus outranks the reviewer's taste.** A finding that cannot say
  what the reference translation does instead is an opinion. Drop it.
- **Gate the swarm.** Dispatch only after the linter is clean, and only on
  the chapters and axes the fingerprint flagged. Five reviewers over a whole
  book is five times the spend for the same answer.
- **Calibrate first.** Run the briefs against a chapter of the reference
  translation itself. Everything reported is a false positive by
  construction, which tells you which briefs over-fire.

Report findings grouped by axis rather than by page — six findings on one
axis mean one habit to change; six across six axes mean six separate fixes.

In Claude Code, reviewers run as subagents, dispatched by the user.

## Working notes

**The corpus is the authority, not your taste.** When the reference
translation does something you would not have done, it still wins. You are
matching, not improving. If a corpus choice is genuinely an error, note it
for the user and follow it anyway unless they say otherwise.

**Register is the hard axis and the one that matters most.** Typography and
glossary get a draft to "plausible". Voice is what gets it to
"indistinguishable". Budget attention accordingly — most of a review pass
should be about who is speaking and whether they sound like themselves.

**Report what you skipped.** If a passage was not reviewed, mark it in the
output. Silent gaps are how a consistency pass stops being trustworthy.
