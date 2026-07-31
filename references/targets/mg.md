# Target language: Malagasy

> **Status.** The linguistic and register sections below are solid and
> usable. **The typography section is not** — Malagasy book-publishing
> conventions are not something this file can state with confidence, and
> there is no broadly documented literary-translation house norm to cite.
>
> Determine typography from your corpus by counting, exactly as `SKILL.md`
> phase 1 requires, and correct this file from what you find. A contribution
> from a Malagasy editor or translator would be worth more than everything
> written here.

Standard literary Malagasy is based on the **Merina** dialect of the
Antananarivo highlands, standardized in orthography from 1823. Regional
varieties — Betsimisaraka, Sakalava, Betsileo, Antandroy and others — differ
substantially in lexicon and phonology. Confirm which your corpus uses before
profiling anything; a translation that drifts between them is as conspicuous
as one that drifts between Peninsular and American Spanish.

---

## Script and orthography

Latin, 21 letters. **`c`, `q`, `u`, `w`, `x` are absent** from native
orthography, appearing only in unassimilated foreign words and names.

This makes an unusually reliable custom check: a word containing any of those
five letters is almost certainly unassimilated. Worth adding when extending
`lint.py` — it recovers most of the foreign-layer detection that shared-script
pairs otherwise lose.

Digraphs `ai`, `ao`, `oa`, `eo` and the consonant clusters `mp`, `nt`, `ndr`,
`ntr`, `tr`, `dr` behave as units.

### Stress, and why it matters for verse

Stress is generally **penultimate**, with a systematic exception: words
ending in **`-ka`, `-tra`, `-na`** take **antepenultimate** stress.

Final vowels in those endings are weak and often barely articulated. For
verse this is decisive — syllable-counting a Malagasy line as though every
written vowel were pronounced will produce metre that does not exist. Count
what is spoken.

---

## Dialogue typography — UNVERIFIED

Madagascar's publishing tradition sits under heavy French influence, so
French conventions are the **hypothesis to test**, not the answer:

- guillemets `«  »`, or the dash `—` for speaker changes
- possibly narrow space before `;` `:` `!` `?`

Do not encode any of this in `profile.json` until you have counted it in the
corpus. If the corpus disagrees with this file, the corpus is right.

---

## Word order

**Verb – Object – Subject.** The subject comes last, and that final position
is the grammatically prominent one.

```
Nahita ny alika ny zaza.
saw      the dog  the child
"The child saw the dog."
```

For a translator working from an SVO source this is not a rearrangement to
perform sentence by sentence. English foregrounds the subject by putting it
first; Malagasy foregrounds it by putting it last. Mechanically mapping SVO
onto VOS while ignoring information structure produces grammatical, inert
prose — the commonest failure in translated Malagasy.

Fronting a constituent for emphasis uses the particle `dia`, and heavy use of
`dia` is itself a register signal worth counting.

---

## The voice system

The heart of Malagasy grammar, the axis most likely to be flattened, and the
one with the widest syntactic consequences.

Verbs select which participant becomes the sentence-final subject, through
affixal morphology:

| Voice | Affix family | Subject is |
|---|---|---|
| Actor | `m-` (`mi-`, `man-`, `maha-`) | the doer |
| Theme / patient | `-ina`, `-ana` | the undergoer |
| Circumstantial | `a-`, `an-…-ana` | instrument, time, place, beneficiary, reason |

This is **not** the active/passive distinction of European languages.
Theme voice is unmarked and extremely frequent — far commoner than English
passive, and carrying none of its markedness. Rendering every English active
as actor voice produces a text that is subtly wrong throughout while
containing no identifiable error.

### The extraction restriction

The reason the voice system governs everything else: **only the subject can
be relativized, questioned, or clefted.**

To relativize the object, the verb must first be put into theme voice so that
the object *becomes* the subject. English relative clauses therefore cannot be
transferred structurally — each one forces a voice decision in the main verb.

A translator who is not tracking this will either produce ungrammatical
relatives or silently restructure sentences to avoid them, and the second
failure is invisible until someone counts relative-clause density against the
corpus.

**For the style guide:** record the corpus's distribution across the three
voices, and its relative-clause density. Both are measurable, both are
characteristic, and a draft that diverges is diverging on the language's
central axis.

---

## Tense

Marked by prefix alternation on the verb stem, cleanly and regularly:

| Prefix | Tense | Example |
|---|---|---|
| `m-` | present | `mividy` — buys |
| `n-` | past | `nividy` — bought |
| `h-` | future | `hividy` — will buy |

Malagasy has **no perfect/imperfect distinction and no aspect pairs**. Where
a Slavic target forces an aspect decision on every verb and a Romance target
forces a choice between preterite and imperfect, Malagasy forces neither —
but the information those systems carry has to go somewhere, into adverbs,
particles or restructuring. Record how the corpus handles it.

There is **no copula** in present-tense equational sentences: `Mpianatra izy`
= "he is a student", with no verb.

---

## Pronouns, definiteness, deixis

**Pronoun form varies by position.** The first person is `aho` after the
verb, `izaho` when fronted or topicalized. Treating these as free variants
is an error; the fronted form is emphatic.

**Inclusive/exclusive "we"**: `isika` includes the addressee, `izahay`
excludes them. English `we` is ambiguous, so every occurrence is a decision,
and getting it wrong misstates who is inside the group — often at exactly the
moment a scene turns on that.

**No grammatical gender and no gendered third person.** `izy` covers he, she,
it and they. Where a source withholds a character's gender, Malagasy does it
effortlessly; where a source reveals it through pronouns alone, that
information needs another home.

**Definiteness** is marked and carries more than in English:

- `ny` — the general definite article
- `ilay` — the specific, previously-mentioned referent, roughly "that same"

`ilay` is a tracking device: it tells the reader this is the thing from
before. English does this with bare `the`, so a translation that renders
every `the` as `ny` loses the thread that `ilay` maintains.

**Deixis** distinguishes many degrees of distance *and visibility* — `ity`,
`io`, `iny`, `itsy`, `iroa`, `iry` and more, forming a graded series well
beyond this/that. Visibility is grammaticalized: whether the referent can be
seen is encoded. This is an instrument European sources give no signal for,
and its distribution is characteristic enough to record.

---

## Register strata

1. **Kabary / oratorical** — the formal speech register, culturally
   prestigious, dense with proverbs and elaborate indirection
2. **Biblical / archaic** — see below
3. **Literary written**
4. **Neutral**
5. **Colloquial** (`fiteny an-davan'andro`)
6. **Regional / marked**

### The Bible as the elevated stratum

The 1835 Malagasy Bible is the foundational literary text, and its language
functions much as Church Slavonic does for Russian or the King James Version
for English: it is **the** available source of elevated, archaic, solemn
register.

This matters directly. Where a source text reaches for archaic or liturgical
English, Malagasy has a genuine native instrument rather than a workaround —
and a translation that renders elevated register only through vocabulary,
without touching this stratum, has left the main tool unused.

Record whether the corpus draws on it, and for which characters or scenes.

### Ohabolana

Proverbs are a register feature, not decoration. Their density marks elevated
or oratorical speech, and a character who speaks in *ohabolana* is
characterized by that fact.

Where a source has a character speaking in aphorism, Malagasy has a native
instrument. Where a source has plain speech, inserting proverbs raises the
register — which may be wanted, but is never neutral.

Record the corpus's proverb density. Collect the ones it uses in the glossary
under fixed phrases: a proverb quoted twice must be rendered identically both
times, and *ohabolana* are exactly the kind of material later callbacks
quote.

### Indirection and fady

Direct confrontation is dispreferred in formal Malagasy speech to a degree
that has no English equivalent, underpinned by *fihavanana*, the value placed
on social harmony. A blunt English line rendered bluntly may characterize a
speaker as rude in ways the source did not intend.

*Fady* — taboo — additionally constrains what can be named directly,
particularly around death, illness and certain kin relations. Circumlocution
where a source is direct is not softening; it is the neutral register.

These are judgment calls to settle in the style guide per character, not to
resolve case by case.

---

## Borrowing layers

Vocabulary stratifies by source, and the strata carry register:

- **Austronesian core** — the native layer; Malagasy's closest relatives are
  in southern Borneo
- **Bantu** — early, fully assimilated
- **Arabic** — via traders; days, months, divination vocabulary
- **French** — colonial and modern; administration, technology, education
- **English** — recent, mostly technical

**A French borrowing where a native term exists is a register choice**, and
in dialogue it is often a characterization: French code-switching marks urban,
educated, or self-consciously modern speech. Its density is one of the
sharpest voice signals available.

Record which layer the corpus favours, by domain and by character.

---

## Verse

**Hainteny** is the traditional poetic genre — oral, elliptical, frequently
dialogic, dense with metaphor and often erotic or courtship-themed. Where a
corpus renders embedded verse, check whether it draws on hainteny convention
before assuming a European form.

Malagasy verse is **not** naturally syllabo-tonic on the European model.
Given the stress rules above, counting written vowels will produce a metre
that does not exist in speech. Read `references/verse.md`, then determine the
corpus's actual practice — rhyme, syllable count, or free — by reading verse
passages aloud rather than by scanning them on the page.

---

## Names

Malagasy names are typically long, compound and semantically transparent —
built from meaningful elements rather than opaque roots. Two prefixes carry
social information:

- **`Ra-`** — a common honorific element in personal names
- **`Andria-`** — historically noble, associated with the Merina aristocracy

A translator inventing Malagasy-shaped names for a fantasy or historical text
needs to know that these prefixes *say something*, and that attaching
`Andria-` to a commoner reads as an error to a Malagasy reader.

Names do not inflect, so the declension question does not arise. But record
each name's internal morphology in the glossary if the source's names carry
meaning that the corpus chose to render.

Kinship terms are widely used as address in place of names; where a source
uses a bare name, the corpus may well use a kin term, and that is a policy to
record rather than a case-by-case choice.

---

## Traps for translators from English or French

- **Mechanical SVO→VOS conversion** that ignores information structure.
- **Actor voice everywhere**, because it resembles the English active.
- **Relative clauses transferred structurally**, ignoring the extraction
  restriction — or silently avoided, which is harder to notice.
- **`ny` for every `the`**, losing the tracking work that `ilay` does.
- **`we` left undecided** between inclusive and exclusive.
- **French cognate reflex** — reaching for the borrowing when a native term
  carries the register better.
- **Proverb inflation** — sprinkling *ohabolana* to sound literary, raising
  the register above the source's.
- **Bluntness imported wholesale**, mischaracterizing speakers as rude.
- **Verse scanned on the page** rather than by ear.

---

## What this file still needs

- [ ] Dialogue typography, confirmed against a published corpus
- [ ] Quotation mark conventions and nesting
- [ ] Spacing rules — French-style narrow spaces, or not
- [ ] Whether a literary translation house norm exists to point at
- [ ] Transliteration convention for foreign names
- [ ] Contemporary practice on French code-switching in printed dialogue
- [ ] Whether published fiction favours Merina exclusively, or admits
      regional voices in dialogue
