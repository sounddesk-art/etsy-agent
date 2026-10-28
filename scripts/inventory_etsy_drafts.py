#!/usr/bin/env python3
"""Read-only inventory of current Etsy draft listings."""
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path
import requests
from etsy_api import BASE, auth_headers, refresh_access_token, get_owner_shop

OUT=Path("data/etsy_draft_inventory.json")

def shop_id_from(payload):
    if payload.get("shop_id"):
        return int(payload["shop_id"])
    results=payload.get("results") or []
    if results and results[0].get("shop_id"):
        return int(results[0]["shop_id"])
    raise RuntimeError("Could not resolve Etsy shop_id")

def fetch_all(access, shop_id):
    out=[]
    offset=0
    while True:
        r=requests.get(
            f"{BASE}/application/shops/{shop_id}/listings",
            headers=auth_headers(access),
            params={"state":"draft","limit":100,"offset":offset,"sort_on":"created","sort_order":"desc"},
            timeout=45,
        )
        r.raise_for_status()
        payload=r.json()
        batch=payload.get("results") or []
        out.extend(batch)
        offset += len(batch)
        if not batch or offset >= int(payload.get("count") or len(out)):
            break
        if offset > 1000:
            raise RuntimeError("Unexpectedly large draft inventory; stop safely")
    return out

def compact(x):
    return {
      "listing_id":x.get("listing_id"),
      "title":x.get("title"),
      "state":x.get("state"),
      "created_timestamp":x.get("created_timestamp") or x.get("creation_timestamp"),
      "updated_timestamp":x.get("updated_timestamp"),
      "price":x.get("price"),
      "quantity":x.get("quantity"),
      "num_favorers":x.get("num_favorers"),
    }

def main():
    access=refresh_access_token()["access_token"]
    shop_id=shop_id_from(get_owner_shop(access))
    items=fetch_all(access,shop_id)
    data={
      "generated_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
      "shop_id":shop_id,
      "state_filter":"draft",
      "read_only":True,
      "draft_count":len(items),
      "items":[compact(x) for x in items],
    }
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"draft_count":len(items),"shop_id":shop_id,"write_operations":0}))

if __name__=="__main__":
    main()
