#!/usr/bin/env python3
"""Hard human-review gate for Etsy-bound AI-assisted products."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

REQUIRED_REVIEW_FIELDS = ("human_reviewed_at", "human_reviewed_by", "human_prompt_or_notes")

def review_errors(item):
    errors=[]
    if item.get("status") != "approved":
        errors.append("status must be approved")
    for field in REQUIRED_REVIEW_FIELDS:
        if not str(item.get(field) or "").strip():
            errors.append(f"{field} is required")
    return errors

def require_reviewed(item, label=None):
    errors=review_errors(item)
    if errors:
        ident=label or item.get("id") or item.get("title") or "item"
        raise RuntimeError(f"Etsy human-review gate blocked {ident}: " + "; ".join(errors))
    return True

def validate_manifest(path):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    items=data.get("items") if isinstance(data,dict) else data
    if not isinstance(items,list):
        raise RuntimeError("Manifest must be a list or contain an items list")
    failures=[]
    for item in items:
        errs=review_errors(item)
        if errs:
            failures.append({"id":item.get("id") or item.get("title"),"errors":errs})
    return items, failures

def main():
    p=argparse.ArgumentParser()
    p.add_argument("manifest")
    p.add_argument("--require-all",action="store_true")
    a=p.parse_args()
    items,failures=validate_manifest(a.manifest)
    approved=len(items)-len(failures)
    print(json.dumps({"total":len(items),"review_gate_passed":approved,
                      "review_gate_blocked":len(failures),
                      "blocked":failures[:20]},indent=2))
    if a.require_all and failures:
        raise SystemExit(2)

if __name__=="__main__":
    main()
