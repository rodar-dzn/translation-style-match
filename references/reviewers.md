# Reviewer briefs

Phase 4 is the axis no script reaches. It is also where a single reviewer
degrades fastest: hand one model a twenty-point checklist and it will spread
its attention thin and miss most of the list. Narrow briefs, run
independently, find more — and the overlap between them doubles as a
confidence filter, because a finding three reviewers reach separately is
rarely noise.

The cost is literal. Five reviewers is five times the spend. Run them on the
chapters that earned it, not on everything.

---

## The rule that governs all of them

**The corpus outranks the reviewer's taste.**

Put this sentence in every brief. Without it, reviewers "improve" the prose
— they flag deliberate archaism as awkwardness, a character's ugly verbal tic
as an error, a deliberately flat passage as flat writing. Every one of those
is a correct observation about prose and a wrong observation about *matching*,
and a review pass full of them is worse than no review, because it buries the
real findings.

A reviewer may only report a divergence **from the reference translation**.
"I would have phrased this differently" is not a finding. If a reviewer
cannot point at what the corpus does instead, it has nothing to say.

---

## When to dispatch

Order matters. Each gate removes work from the expensive stage.

1. `lint.py` is clean. Mechanical noise masks real findings and wastes
   reviewer attention on things a script already knows.
2. `fingerprint.py --compare` has been read. It tells you *which* chapters
   and *which* axes diverge.
3. Dispatch reviewers on those chapters, for those axes.

Running the full swarm over an entire book, unfiltered, is how this technique
becomes expensive without becoming useful.

---

## Brief 1 — Voice (one instance per character)

The most valuable reviewer, and the reason `split_dialogue.py` exists: this
one reads a single character's extracted lines, not the whole chapter.

> You are checking whether one character's speech is consistent with how the
> reference translation renders that character.
>
> **Character profile:** <paste from STYLEGUIDE.md — dominant stratum, the
> stratum it collides with, mean sentence length, marker words and their
> frequency and placement, forms of address, what this character never does>
>
> **Reference examples:** <paste 5–10 cited lines from the corpus>
>
> **Lines to review:** <paste from work/voices/by-speaker/NAME.txt>
>
> For each line that does not fit the profile, report:
> - the line, with its location tag
> - which signal is missing or wrong (stratum, length, marker, address)
> - what the corpus does instead, quoting a reference example
> - a specific replacement line
>
> The corpus outranks your taste. Report only divergence from the profile,
> never that a line could be written better. If a line fits the profile and
> you dislike it, say nothing.
>
> Do not report every line. If more than a third of the lines look wrong,
> stop and say the profile may be mis-specified — that is more useful than
> two hundred findings.

That last instruction matters. A reviewer given a bad profile will
enthusiastically flag the entire chapter, and you want it to tell you the
profile is wrong rather than bury you.

## Brief 2 — Marker drift

Cheap, narrow, and catches something reading rarely does.

> **Marker words:** <word> belongs to <character>, appearing roughly <n>
> times per chapter, placed <where>.
>
> In the text below, report:
> - occurrences in any other character's speech (a marker that spreads stops
>   being a marker)
> - a rate far below or above <n> per chapter
> - occurrences in an unusual syntactic position
>
> Report counts and locations. Do not rewrite anything.

## Brief 3 — Calques

> Find constructions carried over from <source language> that are
> grammatical in <target language> but not idiomatic in it: literal
> renderings of dead metaphors, idioms translated piece by piece, source word
> order preserved where the target would reorder, and wordplay translated
> literally.
>
> Wordplay is the priority. When a pun is rendered literally, the surrounding
> prose often still shows characters reacting to a joke that is no longer
> there. Flag the joke *and* the orphaned reaction.
>
> For each finding: quote the span, name the source construction behind it,
> and give an idiomatic replacement. Where a pun cannot survive, say so and
> propose what to do about the surrounding reactions.
>
> Do not flag unusual phrasing that is merely striking. Literary prose is
> allowed to be strange. Flag only what is strange *because of the source*.

## Brief 4 — Verse

> Read `references/verse.md` first.
>
> **Corpus verse policy:** <rhyme / metre / formatting, from STYLEGUIDE.md>
>
> For each verse passage, check in this order: does it scan aloud; does it
> follow the corpus's policy rather than the source's; stanza count
> preserved; parallel openings and refrains preserved; do the surrounding
> prose reactions still make sense; are performance artifacts (stutters,
> breaks) in their original metrical positions.
>
> A failure to scan, or prose reactions that no longer fit, outranks any
> inaccuracy of imagery. Say which of the two you are reporting.

## Brief 5 — Glossary drift

Long drafts drift. A term rendered one way in chapter 3 quietly becomes
something else by chapter 30, and no single-chapter read will ever catch it.

> **Glossary:** <paste GLOSSARY.md>
>
> Across the whole draft, report:
> - a term rendered inconsistently between chapters
> - a name whose declension pattern changes
> - two glossary entries that have been collapsed into one rendering
> - a coined term whose formation does not match the pattern recorded in
>   STYLEGUIDE.md
>
> Give locations for every instance, and say which rendering the corpus
> supports. Where the glossary itself is silent, say so — that is a gap to
> fill, not an error to fix.

## Brief 6 — Narration

Everything above is about dialogue. Narration needs its own pass.

> **Narration profile:** <from STYLEGUIDE.md — stratum, sentence length,
> whether it carries the foreign layer, whether profanity survives into it>
>
> Where the narrator is a character, check whether their written register
> differs from their spoken one, and whether the corpus maintains that gap.
>
> Report divergence from the profile only, with the corpus's practice cited.

---

## Aggregating

Reviewers produce overlapping, unranked, occasionally contradictory output.
Merging is a real step, not a formality.

**Deduplicate by span.** Two reviewers flagging the same sentence for
different reasons is one location with two findings, not two problems.

**Rank by agreement.** A span flagged by three independent reviewers is
almost certainly real. A span flagged by one, on a subjective axis, is a
candidate. Say which is which — a reviewer report that presents both at the
same confidence is not usable.

**Group by axis, not by page.** Six findings on one axis mean one habit to
change. Six findings across six axes mean six separate fixes. The grouping
tells the translator what kind of work is in front of them.

**Drop anything without a corpus citation.** This is the enforcement point
for the rule at the top. A finding that cannot say what the reference
translation does instead is an opinion, and it goes in the bin regardless of
how well argued it is.

**Report what was not covered.** If a chapter went unreviewed, or a reviewer
returned nothing, say so explicitly. Silent gaps are how a consistency pass
stops being trustworthy.

---

## Calibrating

Before trusting the swarm, run it on a chapter of the **reference
translation** itself, as though it were a draft.

Everything it reports is a false positive by construction — the corpus cannot
diverge from itself. The volume and character of that output tells you how
much your briefs over-fire, and which reviewer needs tightening. It is the
cheapest calibration available and it takes one chapter.
