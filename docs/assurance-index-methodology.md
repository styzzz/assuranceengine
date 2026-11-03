# Enterprise Assurance Index: draft methodology (v0.1)

Status: draft design. Parameters below are reasoned starting points and have not been validated against real assessments. `tools/assurance_index.py` implements this document exactly.

## Purpose

Give executives one number for assurance posture without letting that number hide missing evidence or critical failures. The index is computed by fixed rules from control records. It is never an AI opinion.

## Inputs per control

| Field | Meaning |
|---|---|
| `state` | compliant, partially_compliant, non_compliant, insufficient_evidence, pending_review, not_applicable |
| `risk` | critical, high, medium, low, unrated |
| `evidence.collected_at` | when the evidence was collected, used for freshness |
| `evidence` present | used for coverage |

## Scoring

1. **State score.** compliant 1.0, partially_compliant 0.5, non_compliant 0, insufficient_evidence 0, pending_review 0. A control awaiting a human reviewer earns no credit until a reviewer settles it. not_applicable controls leave the calculation entirely.
2. **Risk weight.** critical 5, high 3, medium 2, low 1. Unrated is weighted 3, so an unrated control cannot be used to dilute the score.
3. **Freshness.** Evidence 30 days old or newer earns full credit. 31 to 60 days earns half. Older earns none. A control tested once and never refreshed decays.
4. **Raw index.** `100 x sum(weight x state score x freshness) / sum(weight)` over applicable controls.

## Guardrails (what the index may not hide)

| Rule | Effect |
|---|---|
| Any critical control is non_compliant | Reported index is capped at 69 |
| Evidence coverage below 80% of applicable controls | Reported index is capped at 79 |

The report always shows the raw index, the reported index, the reason for any cap, evidence coverage, controls pending review, and evidence gaps. The caps stop a strong average from masking one serious failure or a large untested area.

## Worked example

`samples/controls.sample.json` holds 17 synthetic controls. Running the calculator gives a raw index of 72.3, capped to 69 because IAM-002 (wildcard permissions on a deployment role) is a critical failure. Evidence coverage is 94%. DATA-005 is pending review and DATA-008 has no evidence.

## Known weaknesses and open questions

- The weights, window lengths and caps are judgment calls. They need calibration against real audit outcomes before the index is used for decisions.
- Treating a pending review as zero credit makes the index move when reviewers act. An alternative is to publish a provisional and a reviewed index side by side.
- A weighted average still lets many low-risk passes offset a high-risk partial. The caps address only the most severe cases.
- Framework mapping is by label. Real mappings need licensed framework text and a review process.
- Control confidence (how sure the assessor is) is not yet modeled. Today only evidence presence, freshness and human review feed the score.
