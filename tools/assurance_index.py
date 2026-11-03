#!/usr/bin/env python3
"""Reference calculator for the draft Enterprise Assurance Index.

Reads control assessment records, checks each one against the rules in
spec/finding.schema.json, verifies every evidence hash, and computes the index
described in docs/assurance-index-methodology.md.

Usage:
    python3 tools/assurance_index.py samples/controls.sample.json --as-of 2026-11-02

Standard library only. Exit code 1 if any record is invalid or any hash fails.
"""
import argparse
import hashlib
import json
import sys
from datetime import date, datetime

STATES = {
    "compliant", "non_compliant", "partially_compliant",
    "insufficient_evidence", "not_applicable", "pending_review",
}
RISKS = {"critical", "high", "medium", "low", "unrated"}

# Draft parameters. Each is a documented, versioned choice, not a measured constant.
STATE_SCORE = {
    "compliant": 1.0,
    "partially_compliant": 0.5,
    "non_compliant": 0.0,
    "insufficient_evidence": 0.0,
    "pending_review": 0.0,
}
RISK_WEIGHT = {"critical": 5, "high": 3, "medium": 2, "low": 1, "unrated": 3}
FRESH_DAYS = 30          # full credit inside this window
STALE_DAYS = 60          # half credit up to here, none beyond
CAP_CRITICAL_FAILURE = 69
CAP_LOW_COVERAGE = 79
COVERAGE_FLOOR = 0.80

NEEDS_EVIDENCE = {"compliant", "non_compliant", "partially_compliant"}


def validate(rec):
    """Return a list of problems with one control record."""
    errs = []
    for key in ("control_id", "objective", "state", "risk"):
        if not rec.get(key):
            errs.append(f"missing {key}")
    if rec.get("state") not in STATES:
        errs.append(f"unknown state {rec.get('state')!r}")
    if rec.get("risk") not in RISKS:
        errs.append(f"unknown risk {rec.get('risk')!r}")
    state, evidence = rec.get("state"), rec.get("evidence")
    if state in NEEDS_EVIDENCE and not evidence:
        errs.append("a conclusion requires evidence (no evidence, no finding)")
    if state == "insufficient_evidence" and not rec.get("abstention_reason"):
        errs.append("insufficient_evidence requires abstention_reason")
    if evidence:
        for key in ("source", "collected_at", "method", "excerpt", "sha256"):
            if not evidence.get(key):
                errs.append(f"evidence missing {key}")
    return errs


def hash_ok(rec):
    ev = rec.get("evidence")
    if not ev:
        return True
    return hashlib.sha256(ev["excerpt"].encode("utf-8")).hexdigest() == ev["sha256"]


def age_days(rec, as_of):
    ev = rec.get("evidence")
    if not ev:
        return None
    collected = datetime.fromisoformat(ev["collected_at"].replace("Z", "+00:00")).date()
    return (as_of - collected).days


def freshness(days):
    if days is None:
        return 0.0
    if days <= FRESH_DAYS:
        return 1.0
    if days <= STALE_DAYS:
        return 0.5
    return 0.0


def compute(records, as_of):
    applicable = [r for r in records if r["state"] != "not_applicable"]
    denom = sum(RISK_WEIGHT[r["risk"]] for r in applicable)
    numer = 0.0
    rows = []
    for r in applicable:
        d = age_days(r, as_of)
        f = freshness(d)
        credit = STATE_SCORE[r["state"]] * f
        numer += RISK_WEIGHT[r["risk"]] * credit
        rows.append((r["control_id"], r["state"], r["risk"], d, f, credit))
    raw = 100.0 * numer / denom if denom else 0.0

    with_evidence = [r for r in applicable if r.get("evidence")]
    coverage = len(with_evidence) / len(applicable) if applicable else 0.0
    critical_failures = [r["control_id"] for r in applicable
                         if r["risk"] == "critical" and r["state"] == "non_compliant"]
    pending = [r["control_id"] for r in applicable if r["state"] == "pending_review"]
    gaps = [r["control_id"] for r in applicable if r["state"] == "insufficient_evidence"]

    final, reasons = raw, []
    if critical_failures and final > CAP_CRITICAL_FAILURE:
        final = CAP_CRITICAL_FAILURE
        reasons.append(f"capped at {CAP_CRITICAL_FAILURE}: critical non-compliance in {', '.join(critical_failures)}")
    if coverage < COVERAGE_FLOOR and final > CAP_LOW_COVERAGE:
        final = CAP_LOW_COVERAGE
        reasons.append(f"capped at {CAP_LOW_COVERAGE}: evidence coverage {coverage:.0%} is below {COVERAGE_FLOOR:.0%}")
    return dict(raw=raw, final=final, reasons=reasons, coverage=coverage, rows=rows,
                critical_failures=critical_failures, pending=pending, gaps=gaps,
                applicable=len(applicable), excluded=len(records) - len(applicable))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--as-of", help="evaluation date, YYYY-MM-DD (default: file's as_of_default)")
    args = ap.parse_args()

    with open(args.path) as f:
        data = json.load(f)
    records = data["controls"]
    as_of = date.fromisoformat(args.as_of or data["as_of_default"])

    problems = 0
    for r in records:
        for e in validate(r):
            print(f"INVALID  {r.get('control_id', '?')}: {e}")
            problems += 1
        if not hash_ok(r):
            print(f"HASH FAIL  {r['control_id']}: excerpt does not match sha256")
            problems += 1
    if problems:
        sys.exit(1)

    res = compute(records, as_of)
    print(f"As of {as_of}  |  {res['applicable']} applicable controls, {res['excluded']} not applicable\n")
    print(f"{'control':<10} {'state':<22} {'risk':<9} {'age(d)':>6} {'fresh':>6} {'credit':>7}")
    for cid, state, risk, d, f, credit in res["rows"]:
        age = "-" if d is None else str(d)
        print(f"{cid:<10} {state:<22} {risk:<9} {age:>6} {f:>6.1f} {credit:>7.2f}")
    print()
    print(f"Raw index        {res['raw']:.1f}")
    print(f"Reported index   {res['final']:.1f}")
    for reason in res["reasons"]:
        print(f"  {reason}")
    print(f"Evidence coverage {res['coverage']:.0%}")
    print(f"Pending review   {', '.join(res['pending']) or 'none'}")
    print(f"Evidence gaps    {', '.join(res['gaps']) or 'none'}")
    print("All evidence hashes verified.")


if __name__ == "__main__":
    main()
