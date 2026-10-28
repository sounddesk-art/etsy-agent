#!/usr/bin/env python3
"""Convert the 50 researched concepts into a low-friction owner creative-review queue."""
from __future__ import annotations
import json
from pathlib import Path

SRC=Path("data/researched_listing_candidates.json")
OUT=Path("data/etsy_owner_review_queue.json")

STYLE_BY_SERIES={
 "cozy-animals":"warm editorial illustration, expressive but original animal character, tactile paper texture, calm neutral interior palette",
 "landscapes":"atmospheric fine-art landscape, layered depth, natural light, original composition, print-friendly detail",
 "celestial":"refined celestial illustration, balanced negative space, elegant symbolic geometry, original composition, sophisticated wall-art palette",
 "botanical-sun":"modern botanical illustration, organic shapes, warm sunlight, tactile print texture, original composition",
}

def proposed_prompt(item):
    title=item["title_draft"].split("|",1)[0].strip()
    style=STYLE_BY_SERIES.get(item["series"],"original contemporary wall-art illustration")
    return (
      f"Create an original printable artwork concept centered on: {title}. "
      f"Visual direction: {style}. Avoid text, trademarks, copyrighted characters, "
      "artist imitation, logos, stock-image composition, and obvious template repetition. "
      "Design for a premium wall-art listing with a clear focal point and enough detail for large prints."
    )

def build(item):
    return {
      "id":item["id"],
      "research_score":item["research_score"],
      "title_draft":item["title_draft"],
      "description_draft":item["description_draft"],
      "tags":item["tags"],
      "series":item["series"],
      "suggested_price":item["suggested_price"],
      "proposed_prompt":proposed_prompt(item),
      "owner_instruction":"Add at least one item-specific creative decision (subject detail, composition, palette, mood, medium, or exclusion). Do not merely write approved.",
      "human_prompt_or_notes":None,
      "human_reviewed_by":None,
      "human_reviewed_at":None,
      "status":"needs_human_creative_input",
      "generation_allowed":False,
      "etsy_upload_allowed":False,
    }

def main():
    src=json.loads(SRC.read_text(encoding="utf-8"))
    items=[build(x) for x in src["items"]]
    if len(items)!=50:
        raise RuntimeError(f"Expected exactly 50 researched candidates, got {len(items)}")
    if len({x["id"] for x in items})!=50:
        raise RuntimeError("Duplicate review IDs")
    data={
      "version":1,
      "purpose":"Individual creative review required before final AI-assisted artwork generation or Etsy draft upload.",
      "items":items,
    }
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"review_items":len(items),"generation_allowed":0,"etsy_upload_allowed":0}))

if __name__=="__main__":
    main()
