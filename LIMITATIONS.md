# Prior art, validation status, and known weaknesses

Brought here rather than waited for. A tool whose selling point is that it
reports its own blind spots has to start by reporting them.

---

## Validation status

**One book pair, one language.** That is the difference between no evidence
and one data point — not between no evidence and a validated tool.

The run: a two-volume novel sharing one translator, plus a third party's
rough translation of the same book as a negative control. The profile was
built from **volume 1 only**, then volume 2 and the draft were scored
against it.

| Target | Truth | `fingerprint.py` | `delta.py` |
|---|---|---|---|
| Volume 2 | same translator | passed | 13% of chapters flagged |
| Rough draft | different translator | **passed** | 97% of chapters flagged |

`fingerprint.py` failed. The foreign draft came out statistically
indistinguishable from the reference, and on several metrics scored *closer*
than the genuine continuation. Diagnosis: sentence length, paragraph length
and dialogue ratio largely track the **source** text's structure, which
survives translation whoever performs it. Those metrics were measuring the
author, not the translator.

`delta.py` separates them. It is now the discriminative test;
`fingerprint.py` is retained as diagnostic only, and is labelled as such.

**Not validated at all:** the reviewer swarm. Briefs are written and prompts
generate correctly, but the swarm has never been run on real material. It is
the tool's central function and it has zero evidence behind it.

The recall harness reports 18/18 on planted faults. That number is close to
meaningless: the injector and the detector were written by the same person
and agree by construction. It tests the plumbing, not the checking.

---

## Prior art

This problem is not new, and most of it is solved better elsewhere.

### Translation memory

**The industry's answer to "match the existing translation," standard since
the 1990s.** Build a TM from the earlier volumes and get fuzzy matches per
segment. Anyone from the localization world will ask why this project does
not simply use one.

The honest answer: TM matches segments and falls silent where no match
exists — which is all of a new book. It cannot tell you whether a passage it
has never seen *sounds* like the same translator. That gap is what this
occupies. But the overlap is large, and there is no TM integration here at
all. That is a real omission.

### CAT quality-assurance modules

Verifika, ApSIC Xbench, Trados terminology verification. These do
terminology consistency, number and tag checks, forbidden-term enforcement —
essentially everything `lint.py` does, longer established and with
morphological awareness this project lacks.

**This project loses that comparison directly.** `lint.py` exists because it
had to be in-process and dependency-free, not because it is better.

### MQM

Multidimensional Quality Metrics — the standardized error taxonomy for
translation quality: accuracy, fluency, terminology, style, locale
convention, design. The professional standard, and the vocabulary a
translation buyer already speaks.

The six axes here are **not** mapped to it. That is a credibility cost: work
that refuses the common vocabulary looks like work that did not check
whether one existed. The defence is narrow but real — MQM scores general
quality, and "does this sound like the same translator" is not one of its
dimensions.

### Stylometry

Burrows's Delta, Zeta, the `stylo` R package, JGAAP. A mature field with
thirty years of validation behind it.

`fingerprint.py` was a naive reinvention that ignored all of it, and the
validation run duly killed it. Delta should have been the starting point,
not the repair. It is now implemented and it works.

### MT metrics

BLEU, chrF and TER measure surface overlap; COMET and BLEURT are neural and
correlate far better with human judgment.

None of them measure style match — they measure closeness to a correct
translation, which is a different axis. This project has **no** metric that
correlates with human judgment, and does not claim one.

---

## What is actually new here

Being fair to the work as well as harsh with it.

**Deriving thresholds from the reference's own variation.** Chapters of one
book already differ, and that spread is the noise floor. Most QA tooling
picks thresholds by intuition and tunes them by complaint. The useful
by-product is negative and nobody asks for it: a metric on which the corpus
itself swings 98% between chapters is exposed as having no resolution, and
can never be a useful trigger. Measured, not guessed.

**Keyness for voice profiles.** Marker words — the particle or oath that
belongs to a speaker rather than a subject — surface as statistically
overrepresented against the pooled speech of everyone else, with no word
list and no per-language configuration. Averaging is the failure mode, so
the fix is to measure deviation from the average directly.

**Declared ignorance as a first-class output.** `mg.md` ships stamped
UNVERIFIED with a checklist of what is unknown. Glossary entries carry
CANON / NEW / OPEN / REVIEW status. A check that could not run reports "not
run", never "pass". None of this is a posture: it is enforced in the code
and the workflow.

**The target-language reference collection.** Eight languages, structured to
one schema, with the tooling's own limitations documented per language. No
equivalent open collection is known to the author.

---

## Known weaknesses

1. **No validation of the main function.** The reviewer swarm has never run.
2. **One language pair.** Delta's 13%-vs-97% result may not generalize.
3. **No metric correlating with human judgment.** No COMET equivalent.
4. **Glossary matching is literal substring matching.** It handles suffixing
   languages by accident — an inflected form usually contains the nominative
   as a prefix — and breaks on stem alternation. No morphological analysis.
5. **Bitext alignment is positional.** Gale-Church or hunalign would be
   correct; this narrows to a readable window and says so.
6. **Japanese breaks the word-based metrics.** No word spaces means
   `fingerprint.py`'s counts do not transfer. Character count with kanji
   ratio would be right. Documented, not fixed.
7. **Shared script disables two linter checks.** Every European pair loses
   mixed-script and unlisted-foreign detection.
8. **Speaker attribution runs about 43%** on real novel prose. The rest goes
   to `_unattributed.txt` for a person.
9. **No inter-annotator agreement measurement** for the swarm.
10. **Single-corpus assumption.** Harmonizing several translators is a
    stated use case and is not supported.
11. **No TM integration, no MQM mapping.** See above.
12. **Register collision is not measurable.** Keyness finds *what* a
    character says differently. A voice that collides two strata inside one
    line — the coarse mouth using formal vocabulary — is invisible to
    counting, and that collision is often the characterization itself.

---

## What would change the picture

In order of value:

1. **Run the swarm once, calibrated.** Run the briefs against a chapter of
   the reference translation first, where every finding is a false positive
   by construction. That gives a false-positive rate before any finding is
   trusted. Without this the central function remains unevidenced.
2. **A second language pair.** Any series with two volumes by one
   translator. Confirms or kills Delta's result. Costs an hour and no code.
3. **A native speaker on `mg.md`.** The typography section is a hypothesis.
4. Morphological glossary matching, then TM integration, then MQM mapping.

Items 3 and 4 are worth nothing until 1 and 2 are done.
