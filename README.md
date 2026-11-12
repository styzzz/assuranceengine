# AssuranceEngine

An evidence-first approach to AI control assurance: test whether controls work against hashed technical evidence, let an AI assessor conclude only when the evidence supports it, and keep a human reviewer in charge.

**Status: concept with a design specification, a reference scoring tool and a prototype site. There is no production system, no customer data and no measured accuracy.** The table at the bottom separates what is built from what is only specified.

## See it

- `index.html` is the prototype site. Open it in a browser, or serve it with GitHub Pages. The panel at the top is interactive: pick a control to see the evidence, the assessor's reasoning, the state and the integrity hash. All data is synthetic.
- `docs/project-one-pager.md` is a one-page summary for reviewers.

## Run it

```bash
python3 tools/assurance_index.py samples/controls.sample.json --as-of 2026-11-02
```

Standard library only, Python 3.9+. The tool validates every record against the rules in `spec/finding.schema.json`, verifies every evidence hash, and computes the draft Enterprise Assurance Index. Sample result:

```
Raw index        72.3
Reported index   69.0
  capped at 69: critical non-compliance in IAM-002
Evidence coverage 94%
Pending review   DATA-005
Evidence gaps    DATA-008
All evidence hashes verified.
```

A strong average does not hide the one critical failure, and the missing evidence is reported rather than ignored.

## Repository map

| Path | What it is |
|---|---|
| `index.html` | Prototype site |
| `docs/architecture.md` | The Goldfish Model: layers, responsible AI controls, what would prove it |
| `docs/assurance-index-methodology.md` | Draft scoring model, guardrails and known weaknesses |
| `docs/project-one-pager.md` | One-page summary |
| `spec/finding.schema.json` | JSON Schema for a control assessment record. A conclusion without evidence is invalid |
| `samples/controls.sample.json` | 17 synthetic controls across identity, cloud, AI governance, data and privacy |
| `samples/workpaper.sample.md` | A sample audit workpaper |
| `tools/assurance_index.py` | Validator and reference index calculator |
| `infosec-navigator/` | InfoSec Navigator: information security control catalogue, architecture and companion specification, with its own README, validator and tests |

## How the design works

- **The Elephant** is a fixed, versioned knowledge base of frameworks (SOC 2, ISO 27001, ISO 42001, NIST AI RMF, NIST CSF) and organization policies.
- **The Goldfish** is a stateless AI assessor. It sees one control and one evidence set and remembers nothing between tasks.
- Every conclusion maps to one of six states: compliant, non-compliant, partially compliant, insufficient evidence, not applicable, pending human review.
- No evidence means no finding. The assessor must abstain and record why.
- A person approves every conclusion. The platform supports readiness and testing. It does not certify or issue an audit opinion.

## What is built and what is not

| Item | Status |
|---|---|
| Control assessment schema | Built |
| Evidence hash verification | Built |
| Draft index calculator with severity and coverage caps | Built |
| Synthetic sample data and workpaper | Built |
| Prototype site | Built |
| InfoSec Navigator catalogue, validator, tests and page | Built (design draft) |
| InfoSec Navigator AI companions, knowledge layer, Aikido connector, Digital Twin | Specified only |
| AI assessment agents | Specified only |
| Cloud and identity connectors | Specified only |
| Repeatability, accuracy and egress testing | Specified only |
| Private deployment packaging | Specified only |

Index weights and thresholds are reasoned starting points and are not calibrated against real audits. See the methodology document for known weaknesses.
