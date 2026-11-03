# Sample audit workpaper (synthetic)

All content is synthetic. No real environment was assessed.

| Field | Value |
|---|---|
| Control | IAM-002 |
| Objective | No wildcard permissions are attached to deployment roles |
| Frameworks | SOC 2 CC6.3, ISO 27001 A.8.2, NIST CSF 2.0 PR.AA |
| Risk | Critical |
| Assessed by | identity-agent (stateless, model_version: sample) |
| Assessment date | 2026-11-02 |

## Evidence

- Source: IAM policy export
- Collected: 2026-11-02T09:14:00Z
- Method: read-only API call
- SHA-256: see `samples/controls.sample.json`, record IAM-002 (verified by `tools/assurance_index.py`)

```
role=stg-deploy-role
policy=AdministratorAccess-Custom
Effect=Allow
Action=*
Resource=*
```

## Test procedure

1. Retrieve the policies attached to each role tagged as a deployment role.
2. Flag any statement that allows all actions or all resources.
3. Record the exact policy text as evidence and hash it.

## Result

State: non_compliant. The staging deployment role allows every action on every resource, which breaks the least-privilege objective. The evidence is complete and current, so this is a finding and not a data gap.

## Review

| Field | Value |
|---|---|
| Reviewer | pending |
| Decision | pending |
| Remediation owner | to be assigned (must differ from the approver) |

## Index impact

Critical non-compliance caps the Enterprise Assurance Index at 69 until remediated and revalidated.
