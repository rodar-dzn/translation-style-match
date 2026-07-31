# Target language: Spanish

**Confirm every rule here against the corpus before enforcing it.** The
corpus outranks this file — and with Spanish, first confirm *which* Spanish:
peninsular and American norms differ in ways that are immediately audible.

---

## Dialogue

Spanish uses the **raya** (`—`, U+2014), and its spacing rule is the detail
most often botched by non-Spanish typesetting.

```
—No esta noche —dijo ella, y se apartó.
—¿Entonces cuándo?
```

**No space between the raya and the speech.** The dash attaches directly to
the first word, and to the tag that follows it. Getting this wrong is the
fastest tell that a text was not set by a Spanish house.

The tag is closed with a second raya only if speech resumes afterwards:

```
—No esta noche —dijo ella—. Quizá mañana.
```

Note the period **after** the closing raya, not before it. Where the tag
ends the paragraph, no closing raya is used.

Quotation marks are not used for dialogue. `«  »` (comillas latinas) mark
quoted material, thought, or titles; `" "` (inglesas) nest inside them.
Straight quotes are not used in typeset prose.

---

## Inverted marks

`¿` and `¡` open every question and exclamation, and they open at the point
the question begins — not necessarily at the start of the sentence:

```
Si no viene, ¿qué hacemos?
```

Omitting them is an error, not a modernism. The linter should treat a `?`
without a preceding `¿` in the same sentence as an error; add it as a custom
check when extending `lint.py`.

---

## Other punctuation

| Feature | Correct | Common error |
|---|---|---|
| Ellipsis | `…` or `...` (both accepted) | inconsistency |
| Decimal | comma or period — regional | mixing |
| Thousands | period or space — regional | mixing |
| Ranges | `-` or `–` | check corpus |

---

## Address: the biggest variable

English `you` maps onto a system that differs by region, and getting it wrong
relocates the book:

| Form | Where | Register |
|---|---|---|
| `tú` | almost everywhere | informal singular |
| `vos` | Río de la Plata, Central America | informal singular, with its own verb forms |
| `usted` | everywhere | formal singular (and informal in parts of Colombia) |
| `vosotros` | Spain only | informal plural |
| `ustedes` | Spain formal; **all** plural in America | plural |

`vosotros` in a text otherwise set in America is jarring. `vos` conjugates
distinctly (`vos tenés`, not `tú tienes`) and is not a pronoun swap.

Record per character pair in the glossary: which form, and where it changes.
A shift from `usted` to `tú` is a scene, not a detail.

---

## Register strata

1. **Culto / literario** — elevated written
2. **Estándar** — unmarked
3. **Coloquial** — informal, unremarkable
4. **Vulgar / popular** — marked
5. **Malsonante** — taboo

Profanity is heavily regional. A Peninsular obscenity may be neutral or
meaningless in Mexico and vice versa. Pick the variety from the corpus and
stay inside it — mixed-variety profanity is a conspicuous error.

### Tense carries register

- **Pretérito perfecto simple** (`dijo`) vs **compuesto** (`ha dicho`): the
  split is regional as much as temporal. Peninsular Spanish uses the
  compound far more; most of America prefers the simple. Count both in the
  corpus.
- **Imperfecto de subjuntivo** has two forms, `-ra` and `-se`. They are
  largely interchangeable, but `-se` reads as more literary and the corpus
  will favour one. Record the ratio.
- **Future subjunctive** (`hubiere`) survives only in legal and deliberately
  archaic registers. Its appearance is always a deliberate effect.

---

## Sentence structure

Spanish tolerates longer periods than English and permits free subject
placement, which encodes emphasis English marks with stress.

### Traps for translators from English

- **Pronoun overuse.** Spanish is pro-drop; `él dijo` where `dijo` suffices
  reads as emphatic or foreign. This is the single commonest calque.
- **Possessives on body parts.** `se rompió la pierna`, not `rompió su
  pierna`.
- **Progressive aspect.** `estar + gerundio` exists but is narrower than
  English `-ing`. Using it wherever the source has a progressive is a calque.
- **Gerund of consequence.** English freely uses `-ing` for a resulting
  action; Spanish gerund cannot express posteriority.
- **Adverbs in `-mente`.** Far less tolerated than English `-ly`, and two in
  one sentence is heavy.

---

## The shared-script problem

Source and target both in Latin script means `mixed-script` cannot fire and
`flag_unlisted_foreign` cannot separate a retained foreign word from an
ordinary Spanish one. Set `flag_unlisted_foreign: false` for English→Spanish
work; the foreign-layer axis becomes a reading axis.

---

## Names

- Established Spanish forms override transliteration (`Londres`, `Amberes`).
- Names do not inflect, but **gender assignment** for invented nouns must
  stay consistent across the draft. Record it in the glossary.
- Spanish uses two surnames; where a source character has one, the corpus's
  practice decides whether to leave it alone.
