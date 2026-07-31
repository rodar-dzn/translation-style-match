# Target language: Russian

Typographic and stylistic conventions for Russian literary prose.

**Confirm every rule here against the corpus before enforcing it.**
Published translations deviate deliberately, and the corpus outranks this
file. What follows is the default to check *against*, not a specification to
impose.

---

## Dialogue

Russian marks speech with a dash and does not use quotation marks around it.

```
– Не сегодня, – сказала она и отвернулась.
```

### Which dash

Three characters look similar and are routinely confused:

| Char | Code | Name | Use |
|---|---|---|---|
| `–` | U+2013 | en dash | dialogue in much Russian book typesetting |
| `—` | U+2014 | em dash | dialogue in other houses; also parenthetical |
| `-` | U+002D | hyphen | word-internal only, never dialogue |

Both `–` and `—` are defensible for speech; houses differ. **Pick whichever
the corpus uses and enforce it absolutely.** Mixing the two within one book
is the error, not choosing the "wrong" one. Count occurrences in the corpus
to settle it — the ratio is usually lopsided enough to be unambiguous.

A non-breaking space after the dialogue dash is common in typeset books and
usually not worth reproducing in a working manuscript.

### Structure

Speech and the narrative tag are separated by commas and dashes, and the tag
is lowercase even after what would be a sentence-ending mark:

```
– Не сегодня, – сказала она.
– Не сегодня! – крикнула она.
– Не сегодня? – спросила она.
```

Note the comma before the closing dash in the first case, and its absence
after `!` and `?`.

When narration follows the tag and continues into new speech:

```
– Не сегодня, – сказала она и отвернулась. – Может быть, завтра.
```

### One speaker per paragraph

A new speaker requires a new paragraph. Narration belonging to the speaker
may share the paragraph; narration about someone else may not.

```
Wrong:   Он кивнул. – Хорошо. – Она отвернулась.
Right:   Он кивнул.
         – Хорошо.
         Она отвернулась.
```

### Continued speech

Where one speaker's turn runs across paragraphs, subsequent paragraphs take
**no** opening dash. A dash on a continuation paragraph reads as a second
speaker and is a common import error.

### Quotation marks in speech

Russian dialogue does not take quotation marks. `«…»` inside a speech line
is legitimate only for something genuinely quoted — a title, an inscription,
a character quoting a third party verbatim, or unspoken thought.

The linter flags `«»` inside dialogue as a **warning**, not an error,
precisely because these legitimate cases exist. Review each one.

---

## Quotation marks

- Primary: `«…»` (guillemets, U+00AB / U+00BB)
- Nested: `„…“` (U+201E / U+201C)
- Never `"…"` (straight, U+0022) or `“…”` (English curly) in typeset prose

Nesting: `«Он сказал: „не сегодня“, и ушёл»`

---

## Other punctuation

| Feature | Correct | Common error |
|---|---|---|
| Ellipsis | `…` (U+2026) | `...` (three periods) |
| Parenthetical dash | `—` with spaces | hyphen |
| Ranges | `–` no spaces (`1941–1945`) | hyphen or spaced dash |
| `ё` | house style — check corpus | inconsistency within one book |

The `ё` question matters: some publishers set it always, some only where
ambiguity demands it, some never. All three are defensible; mixing is not.
Determine the corpus's policy by counting.

---

## Foreign material

Russian literary translation commonly retains some source-language material
in Latin script — forms of address, interjections, terms of art. Where it
does:

- **Latin script is retained, not transliterated.** `monsieur`, not `мсье`.
- **Case is not inflected.** A Latin-script word does not take a Cyrillic
  ending. `с monsieur Дюпоном`, never `с monsieur'ом`.
- **The policy must be uniform by category.** Retaining `oui` while
  russifying `mademoiselle` collapses the device.

Mixed-script words (`litanию`, `positively скандальный`) are always errors.

Where comprehension needs support, the corpus will have chosen one of:
numbered footnotes, endnotes, inline parenthetical gloss, or nothing. Match
it. Do not introduce a gloss system the corpus does not use.

---

## Register vocabulary strata

Russian stratifies more steeply than English, which is why flattening is the
default failure mode when translating from it. Rough ladder:

1. **Church Slavonic / high archaic** — liturgical, elevated, archaizing
2. **Literary / bookish** — formal written register
3. **Neutral** — the unmarked default
4. **Colloquial (разговорное)** — informal but unremarkable
5. **Vernacular (просторечие)** — uneducated, marked
6. **Slang / obscene (мат)** — taboo, and grammatically productive

Two things translators from English routinely miss:

- **English has no equivalent of stratum 1.** Where a source uses
  King-James-inflected English, Russian can reach for genuinely archaic
  morphology, and a translation that renders it as merely "formal" has lost
  a whole dimension.
- **Мат is productive, not lexical.** Russian obscenity generates verbs,
  adjectives, adverbs and particles from a small root set. A character
  marked by profanity in Russian is marked by *grammar*, not by a
  vocabulary list, and mapping English swearing one-to-one produces
  something that reads as translated.

---

## Sentence structure

Russian tolerates longer periods and deeper subordination than contemporary
English, and permits far freer word order — which carries information
English encodes with stress or cleft constructions.

Two calque patterns to watch for:

- **Fronted subjects everywhere.** English fixes subject-verb-object;
  Russian moves the rheme to the end. Preserving English order throughout
  produces prose that is grammatical, monotone, and subtly foreign.
- **Participial pile-up.** English `-ing` clauses map easily onto Russian
  деепричастия, and translators over-use them. The corpus will show a
  natural rate; count it.

---

## Names and transliteration

- Established names follow tradition, not phonetics. Check reference works
  before transliterating a name that may already have a Russian form.
- Once a name appears in the corpus, that spelling is binding — including
  its declension pattern.
- Record in the glossary whether a name declines at all. Inconsistent
  declension of the same name is a conspicuous error and a frequent one in
  long drafts.
