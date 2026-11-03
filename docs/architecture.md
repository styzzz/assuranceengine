# Architecture: the Goldfish Model

Status: design specification. This repository contains the specification, sample data, a reference scoring tool and a prototype site. It does not contain a working assessment engine.

## The idea

Separate what the system knows from what it judges.

- **The Elephant** is a persistent, immutable knowledge base: control frameworks, mappings and an organization's own policies. It changes only through versioned, reviewed updates.
- **The Goldfish** is a stateless assessor. Each agent receives one control objective and one evidence set, produces a structured assessment, and keeps no memory of earlier tasks. One assessment cannot bias the next.

## Layers

| Layer | Responsibility | Control it provides |
|---|---|---|
| Knowledge | Frameworks, control mappings, policies, test procedures | Versioned and immutable, so assessments cite a fixed source |
| Evidence | Read-only connectors collect configurations, logs, access records and AI artifacts | Source, timestamp, method and SHA-256 hash recorded at collection |
| Assessment | One stateless agent per control | No cross-control contamination |
| Decision | Maps agent output to six explicit states | A conclusion needs evidence; otherwise the state is insufficient_evidence |
| Human review | Reviewer inspects evidence, comments, approves or rejects | The person, not the model, signs off |
| Output | Control register, evidence explorer, workpapers, index, executive view | Every figure links back to evidence |

## Responsible AI controls

| Risk | Design response | Status |
|---|---|---|
| Hallucinated findings | Output must cite evidence; schema rejects a conclusion without it (`spec/finding.schema.json`) | Schema and checker implemented |
| Overconfident guesses | Explicit `insufficient_evidence` state with a recorded abstention reason | Schema and checker implemented |
| Tampered evidence | SHA-256 of each excerpt, verified before scoring | Implemented in `tools/assurance_index.py` |
| Score hiding failures | Capped index, coverage and gaps always reported | Implemented in `tools/assurance_index.py` |
| Non-repeatable results | Record control definition, evidence snapshot, model version and output per assessment | Specified, not built |
| Model drift | Pin model version per assessment; re-run on change | Specified, not built |
| Over-reliance on AI | Mandatory human review state; separation between remediation owner and approver | Specified, not built |
| Data exposure | Private deployment, read-only connectors, no outbound internet for core evaluation, no training on customer data | Specified, not built or tested |

## Deployment targets (proposed)

AWS private VPC, Azure private VNet, Google Cloud private VPC, on-premise. Physically air-gapped installation is a separate target with its own requirements (offline updates, offline model weights) and is not yet scoped. Proposed single-node footprint: one NVIDIA GPU with 16 GB VRAM, 8 vCPUs, 32 GB RAM, 100 GB NVMe. These are untested planning figures.

## What would prove it

1. A repeatability test: the same control and evidence, run many times, produces the same state.
2. A benchmark of agent conclusions against experienced auditors' conclusions on the same evidence.
3. A network egress test showing no outbound traffic during evaluation.
4. A permission test showing the connectors cannot write.
