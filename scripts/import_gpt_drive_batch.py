#!/usr/bin/env python3
from __future__ import annotations
import json, re
from pathlib import Path
import requests

BATCH = Path("data/gpt_drive_batch.json")
ASSETS = Path("assets/generated")
ASSETS.mkdir(parents=True, exist_ok=True)

def slugify(name: str) -> str:
    s = re.sub(r"\.[^.]+$", "", name)
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:90] or "art"

def infer_series(name: str) -> str:
    n=name.lower()
    if any(x in n for x in ["mountain","lake","coast","beach","landscape","forest","fjord","alpine","canyon","hill","lavender","valley"]):
        return "landscapes"
    return "other"

def main():
    batch=json.loads(BATCH.read_text(encoding="utf-8"))
    items=[]
    move_map=[]
    for i,src in enumerate(batch.get("items",[]),1):
        name=src["file"]
        url=src["download_url"]
        print(f"[{i}/{len(batch.get('items',[]))}] downloading {name}")
        r=requests.get(url,timeout=120)
        r.raise_for_status()
        dest=ASSETS/name
        dest.write_bytes(r.content)
        if not dest.stat().st_size:
            raise RuntimeError(f"empty download: {name}")
        series=src.get("series") or infer_series(name)
        display=src.get("display_name") or Path(name).stem.replace("_"," ").replace("-"," ").title()
        item={
            "id":src.get("id") or slugify(name),
            "display_name":display,
            "series":series,
            "file":name,
            "products":["wall_art"],
            "tags":src.get("tags") or [series.replace("-"," "),display.lower(),"printable wall art","digital download"],
            "keyword":src.get("keyword") or "landscape wall art",
            "title":src.get("title"),
            "price":src.get("price","4.90"),
            "status":"approved_for_draft",
            "drive_file_id":src.get("drive_file_id"),
            "batch_id":batch.get("batch_id"),
            "style":src.get("style") or "photorealistic landscape",
            "owner_batch_authorized_at":batch.get("owner_batch_authorized_at"),
            "owner_batch_authorized_by":batch.get("owner_batch_authorized_by"),
            "owner_prompt_or_notes":batch.get("owner_prompt_or_notes"),
            "human_reviewed_at":None,
            "human_reviewed_by":None,
            "human_prompt_or_notes":None
        }
        items.append(item)
        move_map.append({"id":src.get("drive_file_id"),"name":name})
    Path("data/generated_manifest.json").write_text(json.dumps({"version":4,"items":items},indent=2),encoding="utf-8")
    Path("output").mkdir(exist_ok=True)
    Path("output/drive_move_map.json").write_text(json.dumps(move_map,indent=2),encoding="utf-8")
    print(f"Prepared {len(items)} GPT-staged image(s).")

if __name__=="__main__":
    main()
