# Target language: Polish

**Confirm every rule here against the corpus before enforcing it.** The
corpus outranks this file.

---

## Dialogue

Polish uses a dash, like Russian, but the surrounding grammar of the tag
differs and the quotation marks are not the same.

```
– Nie dziś – powiedziała i odwróciła się.
– To kiedy?
```

### Which dash

`–` (U+2013, półpauza) is standard in most Polish houses. `—` (U+2014)
appears in some. Hyphen is never correct. Count both in the corpus; the
ratio will be lopsided.

### The tag

**No comma before the dash** that introduces the tag — this is the main
divergence from Russian practice and the error a Russian-speaking translator
will make:

```
Correct:   – Nie dziś – powiedziała.
Wrong:     – Nie dziś, – powiedziała.
```

A period closes the tag only if speech does not resume. Where it does:

```
– Nie dziś – powiedziała. – Może jutro.
```

The tag verb is lowercase.

---

## Quotation marks

- Primary: `„ … "` — low opening (U+201E), high closing (U+201D)
- Nested: `« … »` (pointing outward) or `‚ … '`
- Never `"` straight or English `" "`

Quotation marks mark quoted material, thought and titles — not dialogue.

---

## Address

`pan` (sir) / `pani` (madam) / `państwo` (plural) with **third-person verb
agreement** — not a pronoun but a noun:

```
Czy pan wie?     literally "Does the gentleman know?"
```

Informal is `ty`. The system is closer to Spanish `usted` than to French
`vous`, and it governs verb person, not just pronoun choice.

Switching from `pan` to `ty` is a scene, negotiated explicitly in Polish
social usage. Record per character pair in the glossary, with the point of
change.

Vocative case is alive and used in direct address (`Aniu!` from `Ania`) —
a nominative in address reads as brusque or foreign.

---

## Register strata

1. **Literacki / wysoki** — elevated, literary
2. **Oficjalny** — formal written
3. **Neutralny** — unmarked
4. **Potoczny** — colloquial
5. **Wulgarny** — taboo

Like Russian, Polish obscenity is **morphologically productive** — a small
root set generating verbs, adjectives and particles. A character marked by
profanity is marked by grammar, and mapping English swearing word-for-word
produces something that reads as translated.

Archaic and dialectal forms are available as register instruments,
particularly the *kresy* and highland varieties, both heavily used in Polish
historical fiction.

---

## Grammar that shapes style

- **Seven cases**, including the vocative. Every name needs its declension
  pattern recorded — inconsistent declension across a long draft is
  conspicuous and common.
- **Aspect pairs.** Nearly every verb exists as perfective/imperfective, and
  the choice is obligatory. English past tense gives no signal, so each
  instance is a decision. Getting aspect wrong changes what the sentence
  says about completion and repetition, not merely its flavour.
- **Free word order**, with the rheme falling late. Preserving English SVO
  throughout produces grammatical, monotone prose.
- **Pro-drop.** Verb endings carry person, so explicit pronouns are
  emphatic. `ja powiedziałem` where `powiedziałem` suffices reads as
  contrastive.
- **Gendered past tense.** Verbs agree with subject gender, so a source that
  conceals a character's gender cannot be rendered neutrally without
  restructuring.

---

## Punctuation

| Feature | Correct | Common error |
|---|---|---|
| Ellipsis | `…` | `...` |
| Decimal | comma | period |
| Thousands | narrow space | comma |
| Ranges | `–` no spaces | hyphen |

Commas before subordinate clauses are grammatically obligatory, as in German
— not a stylistic choice.

---

## The shared-script problem

Polish uses Latin script with diacritics (`ą ć ę ł ń ó ś ź ż`). Against an
English source this means `mixed-script` cannot fire, but the diacritics
give a partial signal: a long run of unaccented Latin in a Polish text is
worth flagging as a possible untranslated leftover.

Set `flag_unlisted_foreign: false` for English→Polish; consider adding a
diacritic-density check when extending `lint.py`.

---

## Names

- Polish names **decline**, including foreign ones once assimilated. Record
  each name's pattern in the glossary before first use.
- Feminine surnames historically took distinct forms (`-owa`, `-ówna`);
  their use is a period and register marker.
- Established Polish forms override transliteration (`Londyn`, `Paryż`,
  `Wiedeń`).
