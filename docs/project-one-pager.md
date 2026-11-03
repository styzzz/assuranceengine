# AssuranceEngine: project one-pager

**Role:** Founder and product architect
**Status:** Concept with a design specification, reference scoring tool and prototype site. No production deployment, customers or revenue.

## Problem

Audits test whether controls exist and are documented. They rarely prove the controls work now. Evidence collection is manual, sampled and point-in-time, and AI systems add controls that legacy GRC tools do not test.

## Approach

An evidence-first assessment engine. Read-only connectors collect technical evidence. A fixed GRC knowledge base (the Elephant) supplies frameworks and policies. A fresh, stateless AI agent (the Goldfish) assesses one control against one evidence set. Output is one of six explicit states. A human reviewer signs off. Workpapers link every conclusion to hashed evidence.

## What is built in this repository

- Control assessment schema that rejects a conclusion without evidence (`spec/finding.schema.json`)
- Reference calculator for a draft Enterprise Assurance Index with severity caps and evidence-integrity checks (`tools/assurance_index.py`)
- 17 synthetic controls with real SHA-256 hashes, and a sample workpaper
- Methodology and architecture documents, each marked with what is implemented versus only specified
- A prototype website

## Skills shown

AI governance (ISO 42001, NIST AI RMF), continuous controls monitoring, audit workpaper design, control testing and evidence standards, responsible AI controls (grounding, abstention, human oversight), scoring methodology design, Python.

## What is not claimed

No live product, no customer data, no measured accuracy. The AI assessment engine is specified, not built. Weights and thresholds are draft and uncalibrated.
