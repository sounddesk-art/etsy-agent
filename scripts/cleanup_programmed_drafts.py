#!/usr/bin/env python3
"""One-time owner-authorized cleanup of the programmed Etsy drafts."""
from __future__ import annotations
import time, json, requests
from etsy_api import BASE, auth_headers, refresh_access_token, get_owner_shop
from inventory_etsy_drafts import fetch_all, shop_id_from

KEEP={
4603491287,4603491319,4603512936,4603512982,4603513014,
4603491485,4603491521,4603513112,4603491575,4603491613,
}
CUTOFF=1793024764

def main():
    token_data=refresh_access_token()
    scope=set(str(token_data.get("scope") or "").split())
    if "listings_d" not in scope:
        raise SystemExit("BLOCKED: current Etsy OAuth token lacks listings_d; no listings deleted.")
    access=token_data["access_token"]
    shop_id=shop_id_from(get_owner_shop(access))
    drafts=fetch_all(access,shop_id)
    by_id={int(x["listing_id"]):x for x in drafts if x.get("listing_id")}
    missing=sorted(KEEP-set(by_id))
    if missing:
        raise SystemExit(f"SAFETY STOP: approved seed drafts missing: {missing}")
    bad=[]
    for lid,x in by_id.items():
        if lid in KEEP:
            continue
        created=int(x.get("created_timestamp") or x.get("creation_timestamp") or 0)
        if x.get("state")!="draft" or created<=CUTOFF:
            raise SystemExit(f"SAFETY STOP: non-seed draft {lid} is outside programmed-draft boundary")
        bad.append((created,lid,x.get("title") or ""))
    bad.sort()
    if len(bad)>105:
        raise SystemExit(f"SAFETY STOP: expected at most 105 programmed drafts, found {len(bad)}")
    print(json.dumps({"drafts_before":len(drafts),"approved_preserved":10,"cleanup_candidates":len(bad)}))
    deleted=0
    for _,lid,_title in bad:
        r=requests.delete(f"{BASE}/application/listings/{lid}",
                          headers=auth_headers(access),timeout=45)
        if r.status_code==404:
            continue
        if r.status_code!=204:
            try: detail=r.json()
            except Exception: detail=r.text[:300]
            raise SystemExit(f"Delete failed for {lid}: HTTP {r.status_code} {detail}")
        deleted+=1
        if deleted%20==0:
            print(f"Deleted {deleted}/{len(bad)} programmed drafts")
        time.sleep(0.15)
    remaining=fetch_all(access,shop_id)
    remain_ids={int(x["listing_id"]) for x in remaining if x.get("listing_id")}
    if not KEEP.issubset(remain_ids):
        raise SystemExit("SAFETY FAILURE: an approved quality seed is missing after cleanup")
    extras=remain_ids-KEEP
    if extras:
        raise SystemExit(f"Cleanup incomplete; {len(extras)} non-seed drafts remain")
    print(json.dumps({"status":"CLEAN","deleted_this_run":deleted,
                      "drafts_after":len(remaining),"approved_quality_drafts":10}))

if __name__=="__main__":
    main()
