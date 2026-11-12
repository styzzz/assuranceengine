#!/usr/bin/env python3
"""Validate the InfoSec Navigator catalogue and generate data.js for the page.

Reads infosec-navigator/controls.json, checks it, and writes
infosec-navigator/data.js, which index.html loads. Loading a script keeps the
page working when opened straight from disk (file://), as the rest of the
prototype does.

Usage:
    python3 infosec-navigator/build.py           # validate and write data.js
    python3 infosec-navigator/build.py --check   # validate; fail if data.js is stale

Standard library only. Exit code 1 on any validation error or stale output.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "controls.json")
OUTPUT = os.path.join(HERE, "data.js")

ID_PATTERN = re.compile(r"^ISN-([A-Z]{3})-(\d{2})$")
RISKS = ("critical", "high", "medium", "low")
REQUIRED = ("id", "domain", "component", "title", "objective", "default_risk", "frameworks",
            "evidence", "test", "pass_criteria", "common_gaps", "abstain_when")
ENGINE_STATES = ("compliant", "partially_compliant", "non_compliant",
                 "insufficient_evidence", "not_applicable", "pending_review")


def _non_empty_strings(value):
    return isinstance(value, list) and value and all(
        isinstance(v, str) and v.strip() for v in value)


def validate(data):
    """Return a list of human-readable problems. An empty list means valid."""
    errs = []
    frameworks = data.get("frameworks", {})
    domains = data.get("domains", {})
    controls = data.get("controls", [])

    if not frameworks:
        errs.append("no frameworks defined")
    for fw_key, fw in frameworks.items():
        if not fw.get("name") or not fw.get("ids"):
            errs.append(f"framework {fw_key} needs a name and ids")

    for key, meta in domains.items():
        if not meta.get("name") or not re.fullmatch(r"[A-Z]{3}", meta.get("code", "")):
            errs.append(f"domain {key} needs a name and a three-letter code")
    codes = [m.get("code") for m in domains.values()]
    if len(codes) != len(set(codes)):
        errs.append("domain codes must be unique")

    if set(data.get("engine_states", {})) != set(ENGINE_STATES):
        errs.append("engine_states must list exactly the six assessment states")

    components = data.get("components", {})
    if not components:
        errs.append("no components defined")
    for key, meta in components.items():
        if not meta.get("name") or not meta.get("description"):
            errs.append(f"component {key} needs a name and a description")
    used_components = set()

    seen_ids = set()
    used_domains = set()
    for c in controls:
        cid = c.get("id", "<no id>")
        for field in REQUIRED:
            if field not in c or c[field] in ("", None, [], {}):
                errs.append(f"{cid}: missing {field}")
        if cid in seen_ids:
            errs.append(f"{cid}: duplicate id")
        seen_ids.add(cid)

        m = ID_PATTERN.match(cid)
        domain = c.get("domain")
        if not m:
            errs.append(f"{cid}: id must look like ISN-ABC-01")
        if domain not in domains:
            errs.append(f"{cid}: unknown domain {domain!r}")
        else:
            used_domains.add(domain)
            if m and m.group(1) != domains[domain]["code"]:
                errs.append(f"{cid}: id code should be {domains[domain]['code']} for domain {domain}")

        comp = c.get("component")
        if comp not in components:
            errs.append(f"{cid}: unknown component {comp!r}")
        else:
            used_components.add(comp)

        if c.get("default_risk") not in RISKS:
            errs.append(f"{cid}: default_risk must be one of {', '.join(RISKS)}")

        mapped = c.get("frameworks") or {}
        if not any(mapped.values()):
            errs.append(f"{cid}: needs at least one framework mapping")
        for fw_key, ids in mapped.items():
            if fw_key not in frameworks:
                errs.append(f"{cid}: unknown framework {fw_key!r}")
                continue
            if not isinstance(ids, list):
                errs.append(f"{cid}: {fw_key} must be a list")
                continue
            for ref in ids:
                if ref not in frameworks[fw_key]["ids"]:
                    errs.append(f"{cid}: {ref!r} is not in {fw_key} reference ids")
            if len(ids) != len(set(ids)):
                errs.append(f"{cid}: duplicate reference in {fw_key}")

        evidence = c.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errs.append(f"{cid}: needs at least one evidence source")
        else:
            for item in evidence:
                for key in ("source", "method"):
                    if not str(item.get(key, "")).strip():
                        errs.append(f"{cid}: evidence item missing {key}")
                if item.get("access") != "read-only":
                    errs.append(f"{cid}: evidence access must be 'read-only' ({item.get('source', '?')})")

        for field in ("test", "common_gaps", "abstain_when"):
            if field in c and not _non_empty_strings(c[field]):
                errs.append(f"{cid}: {field} must be a non-empty list of text")

        for field in ("title", "objective", "pass_criteria"):
            if field in c and not str(c[field]).strip():
                errs.append(f"{cid}: {field} is empty")

    for key in domains:
        if key not in used_domains:
            errs.append(f"domain {key} has no controls")
    for key in components:
        if key not in used_components:
            errs.append(f"component {key} has no controls")

    companions = data.get("companions", [])
    for comp_ai in companions:
        name = comp_ai.get("name", "<no name>")
        for field in ("name", "deliverable", "question"):
            if not str(comp_ai.get(field, "")).strip():
                errs.append(f"companion {name}: missing {field}")
        if comp_ai.get("component") not in components:
            errs.append(f"companion {name}: unknown component {comp_ai.get('component')!r}")
        if comp_ai.get("status", "specified") != "specified":
            errs.append(f"companion {name}: status must be 'specified' until built")
        for field in ("returns", "requires"):
            if not _non_empty_strings(comp_ai.get(field)):
                errs.append(f"companion {name}: {field} must be a non-empty list of text")
    names = [c.get("name") for c in companions]
    if len(names) != len(set(names)):
        errs.append("companion names must be unique")

    return errs


def render(data):
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    return ("// Generated by infosec-navigator/build.py from controls.json. Do not edit.\n"
            "window.INFOSEC_NAVIGATOR = " + payload + ";\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail if data.js is missing or out of date")
    args = ap.parse_args()

    with open(SOURCE, encoding="utf-8") as f:
        data = json.load(f)

    errs = validate(data)
    if errs:
        for e in errs:
            print(f"INVALID  {e}")
        print(f"\n{len(errs)} problem(s). data.js not written.")
        return 1

    text = render(data)
    if args.check:
        try:
            with open(OUTPUT, encoding="utf-8") as f:
                current = f.read()
        except FileNotFoundError:
            current = None
        if current != text:
            print("STALE    data.js does not match controls.json. Run build.py to regenerate.")
            return 1
        print(f"OK       {len(data['controls'])} controls valid and data.js is up to date.")
        return 0

    with open(OUTPUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"OK       {len(data['controls'])} controls valid. Wrote {os.path.relpath(OUTPUT)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
