# Target language: Japanese

**Confirm every rule here against the corpus before enforcing it.** The
corpus outranks this file.

Japanese is the strongest test of whether a style profile generalizes. Most
of the six axes survive; two of them work through machinery that has no
European equivalent, and the linter's assumptions need rewriting rather than
reconfiguring.

---

## Dialogue

Speech is enclosed in **kagi kakko**: `「 … 」`. Nested quotation uses
double brackets `『 … 』`.

```
「今夜はだめ」彼女はそう言って背を向けた。
「じゃあ、いつ?」
```

Notes that break European assumptions:

- **No sentence-final `。` before the closing bracket.** The bracket closes
  the sentence.
- **No space** anywhere — Japanese does not space between words, so the
  linter's word-boundary regex is meaningless here.
- The tag follows the bracket directly, without punctuation between them.
- Each speaker's turn is its own paragraph, as elsewhere.

`『 』` also marks titles of works. Where the corpus uses it for both,
context distinguishes them and the linter cannot.

---

## Script mixing is register

Japanese writes with three systems simultaneously, and the choice between
them is a stylistic instrument with no European counterpart:

| System | Carries |
|---|---|
| **Kanji** 漢字 | density signals formality, education, difficulty |
| **Hiragana** ひらがな | softness, childishness, intimacy, native words |
| **Katakana** カタカナ | loanwords, emphasis, robotic or foreign speech, sound |

A word normally written in kanji, written instead in hiragana, is a
deliberate softening. Written in katakana, it is alienated or emphasized.

**Kanji density is measurable and characteristic.** Record it for narration
and per character; it belongs in the style guide as a number. This is the
Japanese equivalent of the vocabulary-stratum ladder in the European files,
and it is the axis a careless translation flattens first.

---

## Pronouns are characterization

There is no neutral first person. The choice states age, gender, class,
period and self-regard:

| Form | Signals |
|---|---|
| 私 (わたし) | neutral-polite; formal for men, default for women |
| 僕 | soft masculine, younger, unassertive |
| 俺 | rough masculine, casual or aggressive |
| わたくし | highly formal |
| あたし | feminine, casual |
| わし | elderly masculine, archaic |

English `I` carries none of this. **Every character needs a pronoun decided
before the first line, recorded in the glossary**, and a character who
switches is doing something the scene must support.

Second-person pronouns are worse: あなた, 君, お前, てめえ span intimacy to
insult, and Japanese frequently drops the pronoun entirely, using the
person's name or nothing. Overusing second-person pronouns because the
source has `you` is the single commonest calque from English.

---

## Sentence-final particles

Japanese has the marker-word system from `references/register.md` built into
its grammar. Particles at the end of a sentence carry attitude, gender coding
and social stance:

`ね` seeking agreement · `よ` asserting · `な` masculine musing ·
`わ` feminine (or Kansai masculine) · `ぞ`/`ぜ` rough masculine ·
`かしら` feminine wondering · `だろう`/`でしょう` presumption

Combined with copula choice (`だ` plain / `です` polite / `である` written
formal), these do most of the work that European languages spread across
vocabulary and syntax.

**This is where voice lives.** A per-character reviewer for Japanese should
be briefed primarily on particle and copula distribution, not on word choice.

---

## Politeness levels

Not a two-way `tu`/`vous` split but a system:

1. **常体** plain (`だ`, `する`)
2. **敬体** polite (`です`, `します`)
3. **尊敬語** respectful — elevates the other party
4. **謙譲語** humble — lowers oneself
5. **丁寧語** courteous

Which level a character uses toward which other character encodes the entire
social map, and **a shift mid-scene is a dramatic event**. Record the matrix
in the glossary: for each character pair, the level, and where it changes.

Narration also picks a level. `である` narration reads formal and literary;
`だ` narration reads modern and close.

---

## Role language

Fiction uses **役割語** — conventionalized speech patterns instantly
signalling a character type: the elderly scholar, the rural speaker, the
aristocratic young woman, the foreigner. These are literary conventions, not
transcriptions of real speech.

If the corpus uses role language for a character type, matching it is
obligatory; inventing a naturalistic voice instead will read as wrong even
though it is more realistic.

---

## Punctuation

| Feature | Correct |
|---|---|
| Full stop | `。` (U+3002) |
| Comma | `、` (U+3001) |
| Ellipsis | `……` (doubled, U+2026 ×2) |
| Interpunct | `・` for lists and foreign name parts |
| Long vowel | `ー` in katakana |

`?` and `!` exist in modern fiction but are not classical; the corpus
decides. They are usually followed by a full-width space when mid-paragraph.

**Ellipsis is conventionally doubled** — a single `…` reads as incomplete.

---

## What the tooling cannot do here

Be honest about this rather than producing false confidence:

- **`lint.py`'s word regex is meaningless.** No spaces means no word
  boundaries; `mixed-script` would fire on every ordinary sentence, since
  script mixing *is* Japanese. **Set `flag_unlisted_foreign: false` and
  expect `mixed-script` to be useless.**
- **`fingerprint.py`'s word counts are wrong.** Metrics based on `words` do
  not transfer. Character counts and kanji ratio would be the right
  measures; implementing them is an open contribution.
- **`split_dialogue.py`** works, since it keys on `「` rather than on words —
  but attribution by name matching is weaker, because Japanese drops
  subjects freely. Expect a low attribution rate and a large
  `_unattributed.txt`.

The reading axes — register, voice, calques — carry proportionally more of
the load for Japanese than for any European target here.

---

## Traps for translators from English

- **Pronoun overuse**, first and second person alike.
- **Flattened particles** — dialogue that is grammatical and characterless.
- **Uniform politeness level**, erasing the social map.
- **Kanji density mismatched to the character or narrator.**
- **Word order.** Japanese is SOV and verb-final; the verb carries the
  sentence's turn, and English word order imported wholesale wastes it.
