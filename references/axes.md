# The six axes of a translation style profile

A translation's identity is not one thing. It decomposes into six axes that
fail independently and are fixed by different means. Profile each one
separately; a draft can be perfect on five and still be spotted instantly
because of the sixth.

Examples below are invented for illustration. Replace them with spans from
the corpus you are actually profiling.

---

## 1. Dialogue typography

**What to record:** which character marks speech, whether quotation marks
appear inside it, whether a speech line may share a paragraph with
narration, how interruptions and trailing speech are punctuated, how a
speaker's continued speech across paragraphs is marked.

**Why it is first:** it is the highest-frequency feature in fiction and the
most visible. A reader who cannot articulate what is wrong will still feel
that the page looks different.

**The commonest failure** is importing the source language's convention
wholesale — keeping English-style quotation marks in a target language that
uses dashes, or keeping narration glued to the speech line.

```
Source convention:   "Not tonight," she said, and turned away.

Wrong (imported):    "Не сегодня," сказала она и отвернулась.
Wrong (half-fixed):  Она отвернулась. — Не сегодня.
Right (RU):          – Не сегодня, – сказала она и отвернулась.
```

Note the third case also changes the dash *character*. See
`targets/ru.md` — this is where target-language reference files earn their
keep.

**Linter catches:** all of it. This axis should reach zero errors before
any human reads the draft.

---

## 2. The foreign layer

Many translations deliberately leave some source-adjacent material
untranslated — forms of address, interjections, honorifics, oaths, terms of
art. The pattern is rarely random, and it is rarely what a new translator
would guess.

**What to record:**

- Which categories stay untranslated (address? oaths? food? titles?).
- Whether they stay in the original script or are transliterated.
- Whether the same word is treated consistently, or varies by speaker.
- How the translation handles comprehension — footnotes, inline gloss,
  context, or nothing at all.
- The *density*: roughly how often a foreign token appears per page.

**The commonest failure** is inconsistency: keeping one category in the
original script while transliterating another, which collapses the contrast
the device depends on. If forms of address stay in Latin script, they must
all stay — russifying half of them destroys the texture and reads as
carelessness rather than choice.

**Second commonest** is the mixed-script word, where a foreign stem takes a
target-language ending:

```
Wrong:   всю мою litanию бед
Right:   вереницу бед
```

This is always an error, never a style. The linter flags it.

**Linter catches:** mixed-script words, and any Latin-script token absent
from the profile's allowlist. Building that allowlist from the corpus is
phase-1 work.

---

## 3. Onomastics and coined terms

Proper nouns, invented vocabulary, place names, titles, institutions.

**What to record:** the canonical rendering of every term, and where in the
corpus you found it.

This is the axis with the strictest rule and the least room for judgment:
**verify before you invent.** A reader of the earlier volumes recognizes a
changed name immediately, and it is the single loudest signal that a
different hand is at work.

Two traps:

- **The near miss.** A rendering that differs by one letter or one
  diacritic from canon reads as a typo to a returning reader. These are
  invisible to a translator working from the source alone.
- **The collapsed distinction.** Where the source uses two different terms
  for related things, the translation almost certainly does too. Merging
  them because they seem synonymous destroys information the author encoded.
  Check whether apparent synonyms are actually distinct in the corpus before
  treating them as interchangeable.

**Linter catches:** known variants, once you have recorded them in the
glossary's rejection column. It cannot catch a term you never looked up.

---

## 4. Register and voice

How speech differs between characters, and how narration differs from
speech.

**What to record:** for each recurring character, the markers that make them
identifiable with the attribution removed. See `references/register.md` for
the method — this axis has enough depth to need its own file.

**Why it is the hard one:** the other five axes are enforceable by rule.
This one requires reading, and it is what separates a competent draft from
an indistinguishable one. A translation can be flawless on typography,
glossary, and script policy and still read as a different book because every
character speaks in the same neutral voice.

**The commonest failure** is exactly that flattening. Machine translation
and hurried human translation both produce it, because the source's register
signals — archaism, profanity, syntactic complexity, sentence length,
vocabulary stratum — are the first things lost when a translator works
sentence by sentence without a model of who is speaking.

**Linter catches:** nothing. Budget your reading time here.

---

## 5. Calques

Constructions carried over from the source that are grammatical in the
target language but not idiomatic in it.

**What to look for:**

- **Literal metaphors.** Figurative language that works in the source
  because of a dead metaphor the target language lacks. Rendering it word
  for word produces something that reads as strange rather than vivid.
- **Idiom fragments.** A fixed expression translated piece by piece, leaving
  a phrase that is comprehensible but inert.
- **Syntactic tracing.** Source word order preserved where the target
  language would reorder — especially participial constructions and
  the placement of subordinate clauses.
- **Broken wordplay.** The worst case, because it damages the surrounding
  scene. If a pun is translated literally, the text may still describe
  characters reacting to a joke that is no longer there. Wordplay must be
  *reinvented* in the target language, accepting a different literal meaning
  in exchange for a working effect. Where that is impossible, the
  surrounding reactions have to be adjusted too.

**Linter catches:** nothing. This is a reading axis.

---

## 6. Neologism formation

When the source coins a word, the translation must coin one too — and the
method it uses is itself a style feature.

**What to record:** from which stratum of the target language the existing
coinages are built. Archaic roots? Compounds? Borrowed affixes? Native
morphology? Once you can state the pattern, new coinages follow from it.

**Why it matters:** a coinage built by a different method is conspicuous
even when it is a perfectly good word. If existing invented terms are
compounds of archaic native roots, a new term assembled from an
international borrowing will stand out — not as wrong, but as *foreign to
the translation*, which is the same problem.

**The method:** collect every coined term you have already confirmed as
CANON. Describe what they have in common morphologically. Write that
description into the style guide. Then build new terms to match it, and
record in the glossary which existing entries each new one was patterned on.

**Linter catches:** nothing, but the glossary's `NEW` status makes every
invention visible for review, which is the point.

---

## Using the axes in review

Report findings *by axis*, not by page order. Six findings on one axis mean
a systematic problem that one fix can address; six findings across six axes
mean six separate problems. Grouping makes the difference visible, and it
tells the translator whether to change a habit or fix a line.
