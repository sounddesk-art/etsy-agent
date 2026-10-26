#!/usr/bin/env python3
import sys, json
from etsy_api import refresh_access_token, get_owner_shop, create_draft, upload_image, upload_file

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/create_draft.py <listing-package.json>")
    pkg=json.load(open(sys.argv[1],encoding="utf-8"))
    token=refresh_access_token()["access_token"]
    shop=get_owner_shop(token)
    shop_id=shop["shop_id"]

    payload={
        "quantity": pkg.get("quantity",999),
        "title": pkg["title"],
        "description": pkg["description"],
        "price": pkg["price"],
        "who_made": pkg.get("who_made","i_did"),
        "when_made": pkg.get("when_made","2020_2026"),
        "taxonomy_id": pkg["taxonomy_id"],
        "is_supply": str(pkg.get("is_supply",False)).lower(),
        "type": "download",
        "should_auto_renew": "false",
    }
    for i,t in enumerate(pkg.get("tags",[])[:13]):
        payload[f"tags[{i}]"]=t

    listing=create_draft(token,shop_id,payload)
    listing_id=listing["listing_id"]

    for rank,img in enumerate(pkg.get("images",[]),start=1):
        upload_image(token,shop_id,listing_id,img,rank,pkg.get("alt_text",""))

    for rank,path in enumerate(pkg.get("files",[]),start=1):
        upload_file(token,shop_id,listing_id,path,rank)

    print(json.dumps({
        "status":"draft_created",
        "shop_id":shop_id,
        "shop_name":shop.get("shop_name"),
        "listing_id":listing_id,
        "state":listing.get("state","draft")
    },indent=2))

if __name__=="__main__":
    main()
