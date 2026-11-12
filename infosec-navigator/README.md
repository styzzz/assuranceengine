# InfoSec Navigator

The information security module of AssuranceEngine. It holds the information security control objectives, the read-only evidence each one needs, the test steps, the pass criteria, and the conditions under which an assessor must abstain instead of concluding.

**Status: design draft.** The catalogue, validator, tests and browser page are built. The AI companions, the knowledge layer, the Aikido platform connection and the Digital Twin are specified only. Nothing in this module has been tested against a real environment, and nothing here is an audit opinion.

## Open it

Open `index.html` in a browser. It loads `data.js` from the same folder, so it works from disk without a server.

## What is in the module

| Path | What it is |
|---|---|
| `controls.json` | The source of truth: 27 control objectives, seven architecture components, framework reference IDs, and 15 companion definitions |
| `build.py` | Validates `controls.json` and writes `data.js`. Standard library only |
| `data.js` | Generated from `controls.json`. Do not edit by hand |
| `index.html` | The navigator page: search, filters, control cards, architecture, companions, coverage |
| `test_navigator.py` | Unit tests for the catalogue and the validator |

## Run it

From the repository root:

```bash
python3 infosec-navigator/build.py
python3 infosec-navigator/build.py --check
python3 -m unittest discover -s infosec-navigator -v
```

`build.py` validates the catalogue and regenerates `data.js`. `--check` fails if `data.js` is stale. The tests include a check that `data.js` is up to date, so run `build.py` after any change to `controls.json`.

## How it fits the INFOSEC NAVIGATOR architecture

The concept has seven operating components, a knowledge layer and a platform layer. The module represents each one:

| Layer in the concept | In this module |
|---|---|
| Executive Governance Layer | Component `executive_governance`: the governance and accountability controls |
| Compliance Management | Component `compliance`, plus the framework reference mapping on every control |
| Risk Management | Component `risk`: risk register, asset inventory, supplier risk |
| Security Control Assessment | Component `control_assessment`: access, detection, data and resilience controls |
| Vulnerability Management | Component `vulnerability` |
| Application Security | Component `appsec` |
| Cloud Security | Component `cloud` |
| NAVIGATOR AI knowledge layer | **Specified only.** Not built |
| AIKIDO platform | **Specified only.** No connector, no integration |

Each control carries a `domain` (its topic) and a `component` (the operating layer it sits in). The page filters on both.

## Built versus specified

| Item | Status |
|---|---|
| Control catalogue: 27 objectives with evidence, test steps, pass criteria, common gaps and abstention rules | Built |
| Framework reference mapping to ISO/IEC 27001:2022 Annex A, NIST CSF 2.0 and SOC 2 criteria (subset used here) | Built, **needs verification** (see below) |
| Validator: unknown references, missing evidence, write access, duplicate IDs, unmapped domains and components, companions claiming to be built | Built and tested |
| Navigator page: search, domain, component, risk and framework filters; coverage report | Built and browser-tested at desktop and phone width |
| AI companions (15): the questions from the concept, with what each one needs first | Specified only. `status` is fixed at `specified` and the validator rejects anything else |
| Knowledge layer (policies, standards, registers as one knowledge base) | Specified only |
| Aikido platform connector | Specified only |
| Digital Twin (operating model, knowledge base, trained AI brain and dashboards combined) | Specified only |
| Dashboards (Compass, Radar, Drift and the others) | Specified only |
| Compliance content for PCI DSS, HIPAA and CIS Controls | **Not in the catalogue yet.** Each would need its own reference set, checked against licensed text |

## Rules the module keeps

These come from the AssuranceEngine design and are enforced where a rule can be checked:

- **No evidence, no finding.** Every control lists the evidence it needs. Where that evidence is missing, the assessor records `insufficient_evidence` with the reason. The abstention conditions are on each card.
- **Read-only.** Every evidence source must be marked `read-only`. The validator rejects anything else.
- **Human approval.** A conclusion is `pending_review` until a person approves it.
- **No claims beyond what is built.** Companions and layers that do not exist are labelled "specified only" on the page itself.

## Known limits

- **Framework references were written from the published frameworks and are not yet checked against licensed text.** ISO/IEC 27001:2022 Annex A, NIST CSF 2.0 and the SOC 2 criteria are used at identifier and short-name level. Verify every identifier and name before this is used for any assessment.
- **Only a subset of each framework is referenced.** The reference sets list the IDs the controls use, not the full frameworks. The coverage panel shows which listed references no control uses yet.
- **Default risk ratings are suggestions.** The organization sets its own ratings. The index methodology in `docs/assurance-index-methodology.md` is still a draft.
- **Content is synthetic guidance.** It has not been reviewed by an external auditor or tested in any environment.
- **Companion questions from the concept are not evaluated.** Concept claims such as "predicts SLA degradation" or "ROI analysis" have no method, data or accuracy measure behind them yet. They are recorded as specified intent only.

## Adding or changing a control

1. Edit `controls.json`. Use the next free number in the domain, for example `ISN-ACC-07`. The middle segment must match the domain code.
2. Map the control to at least one reference ID per framework it touches. Only IDs already in the reference sets are accepted. Add a reference ID to a framework's `ids` only after checking its exact wording.
3. Give every evidence source `"access": "read-only"`.
4. Run `python3 infosec-navigator/build.py`, then the tests.
