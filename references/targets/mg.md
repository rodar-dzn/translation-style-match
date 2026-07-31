# Target language: Malagasy

> **Status: partially unverified.** The linguistic sections below are solid.
> The typography section is **not** — Malagasy book-publishing conventions
> are not something this file can state with confidence, and there is no
> broadly documented literary-translation house norm to cite.
>
> Determine typography from your corpus by counting, exactly as
> `SKILL.md` phase 1 requires, and correct this file from what you find.
> A contribution from a Malagasy editor or translator would be worth more
> than everything written here.

Standard literary Malagasy is based on the **Merina** dialect of the
Antananarivo highlands. Regional variants differ substantially; confirm
which your corpus uses before profiling anything.

---

## Script

Latin, 21 letters. **`c`, `q`, `u`, `w`, `x` are absent** from native
orthography, appearing only in unassimilated foreign words and names.

This makes the linter's foreign-token check unusually effective: a word
containing any of those five letters is almost certainly unassimilated. Worth
adding as a custom check if you extend `lint.py`.

Final `-a`, `-o` and `-y` are frequently unstressed and weakly articulated,
which matters for verse and for transliterating names.

---

## Dialogue typography — UNVERIFIED

Madagascar's publishing tradition sits under heavy French influence, so
French conventions are the **hypothesis to test**, not the answer:

- guillemets `«  »`, or the dash `—` for speaker changes
- narrow space before `;` `:` `!` `?`

Do not encode any of this in `profile.json` until you have counted it in the
corpus. If the corpus disagrees with this file, the corpus is right and this
file is wrong.

---

## Word order

**Verb – Object – Subject.** The subject comes last, and it is the
grammatically prominent position.

```
Nahita ny alika ny zaza.
saw      the dog  the child
"The child saw the dog."
```

For a translator working from an SVO source, this is not a rearrangement to
be performed sentence by sentence — it changes what is emphasized. English
foregrounds the subject by putting it first; Malagasy foregrounds it by
putting it last. A translation that mechanically maps SVO onto VOS while
ignoring information structure produces grammatical, inert prose.

---

## The voice system

The heart of Malagasy grammar, and the axis most likely to be flattened.

Verbs select which participant becomes the sentence-final subject, through
affixal morphology. The three broad voices:

| Voice | Prefix/affix family | Subject is |
|---|---|---|
| Actor | `m-` (`man-`, `mi-`) | the doer |
| Theme/Patient | `-ina`, `-ana` | the undergoer |
| Circumstantial | `a-`, `an-…-ana` | instrument, time, place, beneficiary |

This is **not** the active/passive distinction of European languages, and
translating it as such loses most of it. Theme voice is unmarked and
extremely common — far commoner than English passive — so rendering every
English active as actor voice produces a text that is subtly wrong
throughout.

**For the style guide:** record the corpus's distribution across the three
voices. It is measurable, it is characteristic, and a draft that diverges
from it is diverging on the language's central axis.

---

## Register strata

1. **Kabary / oratorical** — the formal speech register, culturally
   prestigious, dense with proverbs and elaborate indirection
2. **Literary written**
3. **Neutral**
4. **Colloquial** (`fiteny an-davan'andro`)
5. **Regional / marked**

### Ohabolana

Proverbs are a register feature, not decoration. Their density marks
elevated or oratorical speech, and a character who speaks in *ohabolana* is
characterized by that fact.

Where a source has a character speaking in aphorism, Malagasy has a genuine
native instrument. Where a source has plain speech, inserting proverbs
raises the register — which may or may not be wanted, but is never neutral.

Record the corpus's proverb density. Collect the ones it uses in the
glossary under fixed phrases; a proverb quoted twice must be rendered
identically both times.

### Indirection

Direct confrontation is dispreferred in formal Malagasy speech to a degree
that has no English equivalent. A blunt English line rendered bluntly may
read as characterizing rudeness that the source did not intend. This is a
judgment call to record in the style guide, per character, not to resolve
case by case.

---

## Borrowing layers

Malagasy vocabulary stratifies by source, and the strata carry register:

- **Austronesian core** — the native layer
- **Bantu** — early, fully assimilated
- **Arabic** — via Swahili traders; days, months, divination vocabulary
- **French** — colonial and modern; administration, technology, education
- **English** — recent, mostly technical

**A French borrowing where a native term exists is a register choice.** For
translators this cuts both ways: reaching for French cognates is easy and
produces text that reads as urban, educated, or foreign. Record which layer
the corpus favours for which domains.

---

## Other features

- **No grammatical gender**, and no gendered third-person pronoun (`izy`
  covers all). Where a source withholds a character's gender, Malagasy can
  do so effortlessly; where a source reveals it through pronouns, that
  information needs another home.
- **Reduplication is productive**, marking diminution, repetition or
  attenuation (`fotsy` white → `fotsifotsy` whitish). It is an available
  stylistic instrument, not just a lexical fact.
- **Inclusive/exclusive "we"**: `isika` includes the addressee, `izahay`
  excludes them. English `we` is ambiguous; every occurrence needs a
  decision, and getting it wrong misstates who is inside the group.
- **Deictic system** distinguishes many degrees of distance and visibility,
  well beyond this/that.

---

## Traps for translators from English or French

- **Mechanical SVO→VOS conversion** that ignores information structure.
- **Actor voice everywhere**, because it looks like the English active.
- **French cognate reflex** — reaching for the borrowing when a native term
  carries the register better.
- **`we` left undecided** between inclusive and exclusive.
- **Proverb inflation** — sprinkling *ohabolana* to sound literary, raising
  the register above what the source has.

---

## What this file still needs

- [ ] Dialogue typography, confirmed against a published corpus
- [ ] Quotation mark conventions and nesting
- [ ] Spacing rules — French-style narrow spaces, or not
- [ ] Whether a literary translation house norm exists to point at
- [ ] Transliteration convention for foreign names
- [ ] Verse conventions
