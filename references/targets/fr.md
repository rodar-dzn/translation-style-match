# Target language: French

Typographic and stylistic conventions for French literary prose.

**Confirm every rule here against the corpus before enforcing it.** Houses
differ, and contemporary practice has drifted from the classical norms
below. The corpus outranks this file.

---

## Dialogue

French has two systems, and a corpus will use one of them consistently.

### Classical: guillemets enclosing the exchange

A single pair of guillemets opens and closes the whole conversation.
Speaker changes inside it are marked with a dash.

```
« Pas ce soir, dit-elle en se détournant.
— Alors quand ?
— Quand la glace aura fondu. »
```

Note that the closing guillemet appears once, at the end of the exchange —
not after every turn.

### Modern: dashes only

Increasingly common in contemporary fiction, and closer to what a translator
coming from Russian or Spanish will expect.

```
— Pas ce soir, dit-elle en se détournant.
— Alors quand ?
```

**Determine which system the corpus uses before writing a line.** Mixing them
is the error; either alone is correct. Count guillemet pairs against dash
count to settle it.

### Which dash

`—` (U+2014, cadratin) is standard for dialogue. `–` (U+2013, demi-cadratin)
appears in some houses. Hyphen is never correct.

### The incise

The narrative tag inverts subject and verb, and takes no capital even after
`!` or `?`:

```
— Pas ce soir, dit-elle.
— Pas ce soir ! s'écria-t-elle.
— Pas ce soir ? demanda-t-elle.
```

Inversion is obligatory in the incise. `— Pas ce soir, elle dit.` is not a
stylistic variant; it is wrong.

Euphonic `-t-` is inserted where the verb ends in a vowel: `demanda-t-elle`,
`répondit-il` (no `-t-`, the verb ends in `t`).

---

## Spacing

The feature most often botched by non-French typesetting, and the fastest
tell that a text was not set by a French house.

A **narrow no-break space** (U+202F; U+00A0 is the common fallback) goes:

| Before | Inside |
|---|---|
| `;` `:` `!` `?` `»` | after `«` |

```
Correct:   « Pas ce soir ! » demanda-t-elle : pourquoi ?
Wrong:     «Pas ce soir!» demanda-t-elle: pourquoi?
```

`,` and `.` take no preceding space. Note that Canadian French practice
differs — narrow space before `;` `!` `?` is often dropped.

---

## Quotation marks

- Primary: `«  »` with inner spaces
- Nested: `“ ”` or a second pair of guillemets, depending on house
- Never `"` (straight) in typeset prose

---

## Other punctuation

| Feature | Correct | Common error |
|---|---|---|
| Ellipsis | `…` (U+2026) | `...` |
| Apostrophe | `’` (U+2019) | `'` (U+0027) |
| Numeric ranges | `–` | hyphen |
| Thousands | narrow space (`1 000`) | comma |
| Decimal | comma (`3,14`) | period |

---

## Register strata

Steeper than English, and the ladder is explicitly named in French usage —
dictionaries mark these, which makes them checkable.

1. **Littéraire / soutenu** — elevated, written
2. **Courant** — the unmarked default
3. **Familier** — informal, unremarkable in speech
4. **Populaire** — marked as uneducated
5. **Argot** — slang, including *verlan* (syllable-reversed: `meuf`, `keuf`)
6. **Vulgaire** — taboo

### The tense system carries register

This is the single most important thing to get right, and English gives no
signal for it.

- **Passé simple** marks literary narration. It is essentially absent from
  speech. A novel narrated in passé simple and one narrated in passé composé
  are in different registers before a word of vocabulary is chosen.
- **Imparfait du subjonctif** is strongly literary, often archaizing or
  ironic. Its presence is a deliberate effect.
- Where a source uses archaizing English, French can reach for these. A
  translation that renders elevated register only through vocabulary has
  left the main instrument unused.

Record which the corpus uses in narration, and whether it shifts.

### Tutoiement and vouvoiement

English `you` encodes nothing; French `tu` / `vous` encodes relationship,
status and its changes. Every character pair needs a decision, and the
*moment a pair switches* is usually a scene in itself.

Record in the glossary, per character pair: which form, and where it changes.
This is not a detail — mishandling it rewrites relationships.

---

## Sentence structure

- French tolerates longer periods and heavier subordination than
  contemporary English.
- **Literary negation** drops `pas`: `je ne saurais dire`. This is register,
  not error.
- **`ne` explétif** appears after certain verbs and conjunctions
  (`avant qu'il ne parte`) and carries no negative meaning.

### Traps for translators from English

- **`-ing` forms.** English progressives and gerunds do not map onto French
  participe présent as freely as they look. Overuse produces prose that is
  grammatical and unmistakably translated.
- **Possessives.** English marks the possessor on body parts and clothing;
  French uses the definite article with a reflexive: `il s'est cassé la
  jambe`, not `il a cassé sa jambe`.
- **Progressive aspect.** There is no French present progressive. `être en
  train de` is available but marked, and using it wherever English has `-ing`
  is a calque.
- **Adverb placement.** French places adverbs differently and tolerates far
  fewer of them in `-ment` than English does in `-ly`.

---

## The shared-script problem

When the source is also written in Latin script, two of the linter's checks
lose their power:

- `mixed-script` cannot fire.
- `flag_unlisted_foreign` cannot distinguish a retained foreign word from an
  ordinary French one.

Set `flag_unlisted_foreign: false` in `profile.json` for English→French work.
The foreign-layer axis becomes a reading axis, and the allowlist in the style
guide becomes documentation rather than an enforceable rule.

---

## Names and transliteration

- Established French forms override phonetic transliteration
  (`Londres`, `Munich`).
- French does not inflect names, so the declension question does not arise —
  but **gender assignment** for invented nouns does, and it must stay
  consistent across the whole draft. Record it in the glossary.
- Accents on capitals are correct and expected in careful typesetting
  (`École`, `À`), though some houses drop them. Check the corpus.
