# Style guide: <work>

Derived from `<reference corpus>` on `<date>`.

**Every claim below must cite a span actually read in the corpus.** A style
guide written from assumption launders guesses into rules and is worse than
no guide at all. Where you could not determine something, write "not
determined" — never a plausible-sounting default.

---

## 1. Dialogue typography

- **Speech marker:** `<char>` (U+____) — confirmed by `<count>` occurrences
  vs `<count>` of `<alternative>`
- **Quotation marks in speech:** <never / only for quoted material>
- **Narrative tag punctuation:** <cite an example>
- **New speaker:** <new paragraph required?>
- **Continued speech across paragraphs:** <marked how?>
- **Interrupted speech:** <cite>

> Cited example:
> ```
> ```

---

## 2. The foreign layer

- **Categories retained untranslated:** <address / oaths / titles / …>
- **Script:** <retained / transliterated>
- **Inflected?** <yes / no>
- **Density:** ~`<n>` tokens per 1000 words (from `fingerprint.py`)
- **Comprehension support:** <footnote / endnote / inline gloss / none>

**Allowlist** — every foreign token confirmed in the corpus. This feeds
`profile.json`.

```
```

> Cited examples:
> ```
> ```

---

## 3. Onomastics and coined terms

See `GLOSSARY.md` for entries. Record the *formation method* here:

- **Coinages are built from:** <archaic native roots / compounds /
  borrowings / …>
- **Morphological pattern:** <describe it well enough to build new terms>
- **Names:** <transliteration convention; established forms that override it>

> Cited examples, with the pattern each demonstrates:
> ```
> ```

---

## 4. Register and voice

### Narration

- Stratum:
- Mean sentence length: `<n>` words (corpus fingerprint)
- Does narration carry the foreign layer? <yes / no>
- Does profanity survive into narration? <yes / no>
- Distinctive habits:

### Per character

Repeat for each recurring voice. Strip the attribution from a line — if you
cannot tell who is speaking, the profile is not finished.

#### <character>

- **Dominant stratum:**
- **Collides with:** <the second stratum, if the voice mixes>
- **Mean sentence length:**
- **Marker word(s):** `<word>` — ~`<n>` per chapter, placed <where>
- **Terms of address:**
- **Never does:**

> Cited examples:
> ```
> ```

---

## 5. Calques to avoid

Patterns already observed in drafts of this work, so a reviewer can grep
for them.

| Pattern | Wrong | Right |
|---|---|---|
|  |  |  |

---

## 6. Verse

- **Rhyme:** <matches source / always / never>
- **Metre:** <syllabic / accentual / free>
- **Formatting:** <italic / indent / blockquote>
- **Performance artifacts** (stutters, breaks): <preserved how?>
- **Lines with later callbacks:** recorded in `GLOSSARY.md` under fixed
  phrases

---

## Corpus fingerprint

Paste the reference figures from `fingerprint.py` so drafts can be diffed
against them.

```json
```

---

## Deviations from target-language default

Where the corpus departs from `references/targets/<lang>.md`. The corpus
wins; record the departures so nobody "corrects" them later.

-
