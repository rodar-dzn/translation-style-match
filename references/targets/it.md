# Target language: Italian

**Confirm every rule here against the corpus before enforcing it.** The
corpus outranks this file.

---

## Dialogue

Italian houses use two systems. Determine which by counting before writing a
line; mixing them is the error.

### Caporali

```
«Non stasera», disse lei, e si voltò.
«E allora quando?»
```

`«  »` (U+00AB / U+00BB), **without inner spaces** — unlike French, which
puts a narrow space inside them. Each turn takes its own pair.

### Dashes

```
— Non stasera — disse lei, e si voltò.
```

Common in contemporary and translated fiction.

### The tag

Comma **outside** the closing caporale, tag lowercase:

```
«Non stasera», disse lei.
«Non stasera!», esclamò.
```

Nesting inside caporali uses `" "` or `' '`, depending on house.

---

## Address

| Form | Register |
|---|---|
| `tu` | informal singular |
| `Lei` | formal singular — third person feminine agreement, often capitalized |
| `voi` | archaic or southern formal; standard formal until the mid-20th century |
| `voi` / `loro` | plural |

`Lei` takes **third-person** verb agreement regardless of the addressee's
gender. `voi` as a formal singular is a strong period marker — it was
official usage under Fascism and survives regionally in the south. Using it
in a contemporary setting relocates the book.

Record per character pair in the glossary, with the point of any switch.

---

## Register strata

1. **Letterario / aulico** — elevated, literary
2. **Formale**
3. **Standard** — unmarked
4. **Colloquiale / familiare**
5. **Popolare / gergale**
6. **Volgare** — taboo

### The passato remoto problem

The single most consequential choice, and it is **regional as well as
temporal**:

- **Passato remoto** (`disse`) is the literary narrative past, and remains
  ordinary spoken usage in the south.
- **Passato prossimo** (`ha detto`) dominates northern speech and much
  contemporary writing.

A novel narrated in passato remoto and one in passato prossimo differ in
register before any vocabulary is chosen — and the same choice in dialogue
places a character geographically. **Count both in the corpus, separately
for narration and for each character.**

### Congiuntivo

The subjunctive is obligatory in standard Italian after certain
constructions, and dropping it is a strong marker of uneducated or casual
speech. This makes it an instrument: a character who fails to use it is
characterized by that failure.

Record whether the corpus's narration is strict, and which characters
deviate.

---

## Sentence structure

- Italian tolerates long periods with heavy subordination; literary prose
  exploits this.
- **Pro-drop.** Explicit subject pronouns are emphatic. `lui ha detto` where
  `ha detto` suffices reads as contrastive or foreign.
- **Clitic pronouns** cluster and attach to verbs (`glielo diede`); handling
  them woodenly produces prose that is grammatical and unmistakably
  translated.
- **Free word order** with the rheme late, as in the Slavic files here.

### Traps for translators from English

- **Progressive aspect.** `stare + gerundio` is narrower than English
  `-ing`; using it wherever the source has a progressive is a calque.
- **Possessives on body parts and family.** Italian uses the article
  (`si ruppe la gamba`), and drops the possessive with singular family
  members (`mia madre`, but `le mie sorelle`).
- **Adverbs in `-mente`.** Less tolerated than English `-ly`; two in a
  sentence is heavy.
- **Anglicisms.** Contemporary Italian absorbs them freely, but their
  density is a house choice and a register signal. Count the corpus's rate.

---

## Punctuation

| Feature | Correct | Common error |
|---|---|---|
| Ellipsis | `…` | `...` |
| Apostrophe | `’` | `'` |
| Decimal | comma | period |
| Thousands | period | comma |
| Ranges | `–` | hyphen |

Accents: grave is default (`è`, `città`); acute on closed vowels (`perché`,
`né`). `e` versus `è` and `perche` versus `perché` are the errors that mark
a text as unedited.

---

## The shared-script problem

Latin source, Latin target: `mixed-script` cannot fire and
`flag_unlisted_foreign` cannot separate a retained foreign word from an
Italian one. Set `flag_unlisted_foreign: false` for English→Italian work.

---

## Names

- Names do not inflect, but **gender assignment** for invented nouns must be
  fixed before first use and held across the draft — it governs every
  article and adjective downstream. Record it in the glossary.
- Established Italian forms override transliteration (`Londra`, `Parigi`,
  `Monaco di Baviera`).
- Elision and article choice depend on the following sound, not spelling
  (`lo zio`, `l'amico`, `gli studenti`). Invented terms need their article
  recorded alongside their gender.
