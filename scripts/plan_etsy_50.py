#!/usr/bin/env python3
"""Build a 50-slot Etsy selection plan without deleting or publishing anything."""
from __future__ import annotations
import json,re
from pathlib import Path

INV=Path("data/etsy_draft_inventory.json")
RESEARCH=Path("data/etsy_market_research.json")
CAND=Path("data/researched_listing_candidates.json")
OUT=Path("data/etsy_50_selection_plan.json")
STOP={"wall","art","printable","digital","download","original","the","and","in","at","of","by","with","good","print"}

def toks(s):
    return {x for x in re.findall(r"[a-z0-9]+",(s or "").lower()) if len(x)>2 and x not in STOP}

def fit(title,niche):
    a=toks(title.split("|",1)[0]); b=toks(niche["keyword"])
    if not a or not b: return 0.0
    inter=len(a&b); union=len(a|b)
    j=inter/union if union else 0
    soft=0.0
    for x in a:
        if any(x in y or y in x for y in b):
            soft += .15
    sim=min(1.0,j+soft)
    return sim*float(niche["opportunity_score"]),sim

def main():
    inv=json.loads(INV.read_text(encoding="utf-8"))
    research=json.loads(RESEARCH.read_text(encoding="utf-8"))
    candidates=json.loads(CAND.read_text(encoding="utf-8"))
    ranked=[]
    for d in inv["items"]:
        if "Wall Art" not in (d.get("title") or ""):
            continue
        best=None
        for n in research["niches"]:
            score,sim=fit(d["title"],n)
            if best is None or score>best["fit_score"]:
                best={"fit_score":round(score,2),"similarity":round(sim,3),
                      "matched_keyword":n["keyword"],"research_score":n["opportunity_score"]}
        ranked.append({**d,**best})
    ranked.sort(key=lambda x:(-x["fit_score"],-x["similarity"],x["listing_id"]))
    existing=[x for x in ranked if x["similarity"]>=.45]
    # Strong match threshold is deliberately conservative; product-type variants
    # such as postcards/bookmarks are not promoted because this research is wall-art specific.
    represented={x["matched_keyword"] for x in existing}
    new=[]
    used=set()
    ordered=sorted(candidates["items"],key=lambda x:(-float(x["research_score"]),x["id"]))
    for x in ordered:
        if len(existing)+len(new)>=50: break
        # First prefer niches not already represented by an existing strong draft.
        if x["source_keyword"] in represented or x["source_keyword"] in used:
            continue
        new.append(x); used.add(x["source_keyword"])
    for x in ordered:
        if len(existing)+len(new)>=50: break
        if any(y["id"]==x["id"] for y in new): continue
        new.append(x)
    if len(existing)+len(new)!=50:
        raise RuntimeError("Could not build exactly 50 target slots")
    keep_ids={x["listing_id"] for x in existing}
    hold=[x for x in inv["items"] if x["listing_id"] not in keep_ids]
    plan={
      "version":1,
      "target_slots":50,
      "existing_drafts_total":inv["draft_count"],
      "existing_research_matched_slots":len(existing),
      "new_research_slots":len(new),
      "existing_drafts_hold_only_no_delete":len(hold),
      "rules":{
        "existing_keep_threshold":"wall-art only and token similarity >= 0.45 to a current live-researched niche",
        "new_slots":"highest research scores, preferring niches not already represented",
        "publishing":"disabled",
        "deletion":"disabled",
        "human_review":"required per item before final activation",
      },
      "existing_review_candidates":[{
        "listing_id":x["listing_id"],"title":x["title"],"matched_keyword":x["matched_keyword"],
        "research_score":x["research_score"],"similarity":x["similarity"],"fit_score":x["fit_score"],
        "status":"needs_human_review"
      } for x in existing],
      "new_review_candidates":[{
        "id":x["id"],"title_draft":x["title_draft"],"source_keyword":x["source_keyword"],
        "research_score":x["research_score"],"status":"needs_human_creative_input"
      } for x in new],
      "hold_existing_drafts":[{"listing_id":x["listing_id"],"title":x["title"],"state":x["state"]} for x in hold],
    }
    OUT.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
      "target":50,"existing":len(existing),"new":len(new),"hold":len(hold),
      "write_operations_to_etsy":0
    }))

if __name__=="__main__":
    main()
