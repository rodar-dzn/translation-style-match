# Target language: German

**Confirm every rule here against the corpus before enforcing it.** The
corpus outranks this file.

German is the useful counterexample in this collection: it marks dialogue
with **quotation marks, not dashes**. A profile built by assuming the
dash convention will be wrong from the first line.

---

## Dialogue

```
„Nicht heute Abend", sagte sie und wandte sich ab.
„Wann dann?"
```

The German pair is `„ … "` — opening mark **low** (U+201E), closing mark
high (U+201C). Nesting uses single marks: `‚ … '`.

Swiss practice uses guillemets pointing outward: `« … »`. Some houses use
inward-pointing `» … «`. All three exist; the corpus decides.

| Style | Opens | Closes | Where |
|---|---|---|---|
| Standard | `„` | `"` | Germany, Austria |
| Guillemets out | `«` | `»` | Switzerland |
| Guillemets in | `»` | `«` | some German houses |

**Straight quotes and English curly quotes are both wrong.** So is `"` as an
opener — the shape and the height differ, and readers register it.

### The tag

Comma before the closing mark, lowercase tag, no inversion required:

```
„Nicht heute Abend", sagte sie.
„Nicht heute Abend!", rief sie.
```

The comma goes **inside** the quotation for statements, and `!` or `?`
replace it, with the comma following outside.

---

## Nouns are capitalized

Every noun, always. This is not stylistic and a draft that misses it is
unreadable as German. It also means capitalization gives the linter no
signal for proper nouns — the trick used in `build_glossary.py` for English
sources does not transfer to German sources.

---

## Address

`du` (informal) and `Sie` (formal, always capitalized) — plus `ihr` for
informal plural. As with French `tu`/`vous`, English gives no signal, and
the switch between them is a scene.

Record per character pair in the glossary. Note also that historical
settings may use `Ihr` or `Er` as archaic address forms, which is a register
instrument English lacks.

---

## Register strata

1. **Gehoben / literarisch** — elevated
2. **Standardsprache** — unmarked
3. **Umgangssprache** — colloquial
4. **Salopp** — casual, marked
5. **Derb / vulgär** — coarse

### Konjunktiv I marks reported speech

This has no English equivalent and is a major literary instrument.

```
Er sagte, er sei müde.        (Konjunktiv I — reported, neutral)
Er sagte, er wäre müde.       (Konjunktiv II — reported with doubt)
Er sagte, er ist müde.        (Indicative — colloquial, or endorsed)
```

The choice signals the narrator's stance toward what is reported.
Journalistic and literary German use Konjunktiv I systematically; colloquial
German avoids it. **Record which the corpus uses**, because a translation
that renders all reported speech in the indicative has silently changed the
narrator.

### Preterite versus perfect

`Er ging` (preterite) is the narrative tense in writing; `Er ist gegangen`
(perfect) dominates spoken German, especially in the south. Narration in the
perfect reads as spoken or regional. Count both in the corpus.

---

## Sentence structure

- **Verb-final subordinate clauses** and the **Satzklammer**, where a verb's
  parts bracket the clause, permit long suspended periods that English cannot
  hold. German literary prose exploits this; translations from English often
  fail to, producing short flat sentences that are grammatical and
  characteristically un-German.
- **Compound nouns** are productive and near-unbounded. This is the primary
  instrument for neologisms — record how the corpus builds them, because a
  coinage assembled by a different method stands out.
- **Modal particles** (`doch`, `ja`, `mal`, `eben`, `halt`, `wohl`) carry
  attitude that English marks with intonation. Dialogue without them reads
  as translated even when every word is correct. Their density and
  distribution is a per-character voice signal worth recording explicitly.

### Traps for translators from English

- **Missing modal particles** — the commonest single tell.
- **Progressive aspect.** No German present progressive; `am + infinitive` is
  regional and marked.
- **Short sentences.** English rhythm imported wholesale wastes the
  Satzklammer.
- **Genitive avoidance.** `von + dative` is colloquial; literary German
  prefers the genitive. Check the corpus's rate.

---

## Other punctuation

| Feature | Correct | Common error |
|---|---|---|
| Ellipsis | `…` | `...` |
| Decimal | comma | period |
| Thousands | period or narrow space | comma |
| Ranges | `–` (Halbgeviertstrich) | hyphen |
| Apostrophe | `’` | `'` |

The comma before subordinate clauses is grammatically obligatory, not
stylistic.

---

## The shared-script problem

Latin source and Latin target: `mixed-script` cannot fire, and
`flag_unlisted_foreign` cannot separate a retained foreign word from a
German one. Set `flag_unlisted_foreign: false` for English→German work.

---

## Names

- Names take genitive `-s` without an apostrophe: `Annas Buch`.
- Established German forms override transliteration (`Mailand`, `Moskau`).
- **Gender assignment** for invented nouns must stay consistent across the
  draft, and it determines every article and adjective ending downstream.
  Record it in the glossary before the first use.
