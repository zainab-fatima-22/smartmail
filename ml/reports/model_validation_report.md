# SmartMail — Model Validation Report

## 1. Held-out test set performance

From `ml/reports/evaluation.txt` (regenerate with `python ml/src/train.py`):

| Metric | Score |
|---|---|
| Accuracy | 100% |
| Precision (macro) | 100% |
| Recall (macro) | 100% |
| F1-score (macro) | 100% |

Every category scores perfectly on the 144-email held-out test set (24
per category), with a clean diagonal confusion matrix.

### Why this number is not the full story

100% accuracy on the held-out set mostly reflects that the training
data is **synthetic and template-generated** (see
`ml/data/raw/DATASET_INFO.md`): each category's templates use fairly
distinct vocabulary, so even a simple linear model can separate them
almost perfectly. This number demonstrates the *pipeline* works
correctly end-to-end — it is **not** a claim about real-world
classification accuracy, and should not be quoted as such.

## 2. Stress-testing on out-of-distribution, deliberately ambiguous emails

To get a more honest picture of the model's real behavior, we tested it
against emails written specifically to sit *between* categories —
phrasing a real inbox would plausibly contain, but that the clean
synthetic templates don't. None of this text appears in the training
data. Reproduce with `python ml/src/validate_model.py`.

| Email | Predicted | Confidence | Runner-up |
|---|---|---|---|
| "Your invoice payment is overdue, please review immediately." | important | 40.1% | work (18.4%) |
| "Team meeting reminder: quarterly review deadline is critical, please attend." | work | 66.4% | important (11.5%) |
| "Limited time offer: renew your subscription now to avoid losing access!" | spam | 29.2% | important (22.4%) |
| "You have been selected for an exclusive 70% discount, claim now!" | promotional | 34.3% | spam (34.3%) |
| "Hey, exciting news – we are having a work party this Friday, you in?" | work | 21.0% | important (19.0%) |
| "URGENT: verify your account or it will be suspended within 24 hours." | important | 46.0% | spam (17.2%) |
| "Thanks for connecting! Check out our community meetup next week." | social | 39.9% | promotional (17.4%) |
| "asdf jkl random text 12345" (nonsense) | promotional | 17.9% | work (17.8%) |

**This is the useful result.** Confidence drops sharply (from ~95-99% on
clean template-matched emails down to 20-65%) exactly on the inputs
designed to be genuinely ambiguous, and the runner-up categories are
the ones you'd intuitively expect. The nonsense input produces
near-uniform, low confidence across categories rather than false
certainty — the model "knows what it doesn't know" reasonably well for
a linear classifier.

## 3. Which categories are easiest to classify?

On the clean synthetic test set, all categories score equally (by
construction — the templates were deliberately kept distinct). On the
ambiguous stress test, **Work** was the most robust category (66.4%
confidence even on a blended work/social email), likely because
meeting/deadline vocabulary is fairly unique to that category.

## 4. Which categories are commonly confused, and why?

The stress test confirms both overlaps the project spec anticipated:

- **Work vs. Important** — both categories share urgency-adjacent
  vocabulary ("review", "deadline", "critical", "immediately"). An
  invoice reminder or a deadline-heavy meeting note can plausibly read
  as either, and the model's confidence drops accordingly (40-46%
  instead of >90%).
- **Promotional vs. Spam** — both use discount/urgency language
  ("limited time", "exclusive", "claim now"). The "70% discount, claim
  now" example produced a near tie (34.3% vs 34.3%) — this is the
  single most confusable pair in the dataset, which matches real-world
  intuition: legitimate marketing and scam emails often use nearly
  identical rhetorical patterns, and the line between them is
  genuinely blurry even for humans.

## 5. Limitations

- Training data is synthetic (see `ml/data/raw/DATASET_INFO.md`) —
  real inboxes contain far messier language, HTML artifacts, longer
  threads, and much more vocabulary diversity than these templates.
- The model is a **linear** classifier (TF-IDF + Logistic Regression).
  It has no notion of word order, negation, or semantic context beyond
  n-gram co-occurrence — it cannot tell "your account is NOT at risk"
  from "your account IS at risk."
- Confidence scores are model probabilities, not certainties, and
  should be treated as such (this is why the frontend shows a
  low-confidence warning below the configured threshold).
- The model was not evaluated against real spam corpora or adversarial
  inputs (e.g. deliberately obfuscated spam text, "fr33 pr!ze").
  Real-world spam filters typically combine several signals (sender
  reputation, links, headers) that this text-only model does not use.
- The model should be retrained if the underlying data distribution
  changes significantly (e.g. real user data eventually replaces the
  synthetic dataset).

## 6. Reproducing this report

```bash
python ml/src/train.py            # regenerates ml/reports/evaluation.txt
python ml/src/validate_model.py   # regenerates this stress-test table
```
