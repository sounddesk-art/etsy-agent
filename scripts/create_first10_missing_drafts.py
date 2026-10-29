#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, zipfile, time
from etsy_api import refresh_access_token,get_owner_shop,find_taxonomy_id,create_draft,upload_image,upload_file

MANIFEST=Path("data/first_10_test_listings.json")
ASSET_DIR=Path("assets/first10_new")
OUT=Path("output/first10_new")
OUT.mkdir(parents=True,exist_ok=True)

FILE_MAP={
 "sleepy-ginger-cat":"sleepy-ginger-cat.png",
 "eucalyptus-minimal":"eucalyptus-minimal.png",
 "olive-branch-sun":"olive-branch-sun.png",
 "sun-moon-harmony":"sun-moon-harmony.png",
}

def description(item):
    lead=item["title"].split("|")[0].strip()
    return f"""{lead}

High-resolution printable wall art. Instant digital download; no physical item will be shipped.

YOU RECEIVE
• 1 high-resolution PNG artwork
• Print-ready digital file delivered in a ZIP archive

PRINTING
Print at home, with a local print shop, or with an online printing service. Colors may vary slightly between screens and printers.

CREATIVE PROCESS
This artwork was created with AI-assisted creative tools from seller-directed creative input, then individually selected, curated and prepared for this shop.

LICENSE
Personal use only. Do not resell, redistribute, share or upload the digital file for resale.
"""

def main():
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    items=[x for x in data["items"] if x.get("status")=="NEEDS_NEW_IMAGE"]
    if len(items)!=4:
        raise SystemExit(f"Expected 4 missing-image listings, found {len(items)}")
    missing=[FILE_MAP[x["id"]] for x in items if not (ASSET_DIR/FILE_MAP[x["id"]]).exists()]
    if missing:
        raise SystemExit("Missing final approved assets: "+", ".join(missing))
    token_data=refresh_access_token()
    scope=set(str(token_data.get("scope") or "").split())
    if "listings_w" not in scope:
        raise SystemExit("BLOCKED: current Etsy OAuth token lacks listings_w")
    token=token_data["access_token"]
    shop=get_owner_shop(token); shop_id=int(shop["shop_id"])
    taxonomy_id=find_taxonomy_id(token,"Digital Prints")[0]
    results=[]
    for item in items:
        src=ASSET_DIR/FILE_MAP[item["id"]]
        zpath=OUT/(src.stem+"-download.zip")
        with zipfile.ZipFile(zpath,"w",zipfile.ZIP_DEFLATED) as z:
            z.write(src,arcname=src.name)
        payload={
            "quantity":"999",
            "title":item["title"],
            "description":description(item),
            "price":"4.90",
            "who_made":"i_did",
            "when_made":"2020_2026",
            "taxonomy_id":str(taxonomy_id),
            "is_supply":"false",
            "type":"download",
            "should_auto_renew":"false",
            "tags":",".join(item["tags"][:13]),
        }
        listing=create_draft(token,shop_id,payload)
        lid=int(listing["listing_id"])
        upload_image(token,shop_id,lid,str(src),1,item["title"].split("|")[0].strip())
        upload_file(token,shop_id,lid,str(zpath),1)
        results.append({"listing_id":lid,"id":item["id"],"title":item["title"]})
        time.sleep(0.25)
    print(json.dumps({"status":"DRAFTS_CREATED","created":len(results),"published":0,"auto_renew":False,"items":results},indent=2))

if __name__=="__main__":
    main()
