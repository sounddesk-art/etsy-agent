#!/usr/bin/env python3
import sys, json
from etsy_api import (
    refresh_access_token, get_owner_shop, find_taxonomy_id,
    create_draft, upload_image, upload_file, update_listing
)

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/create_draft.py <listing-package.json>")

    pkg=json.load(open(sys.argv[1],encoding="utf-8"))
    token=refresh_access_token()["access_token"]
    shop=get_owner_shop(token)
    shop_id=shop["shop_id"]

    taxonomy_id=pkg.get("taxonomy_id")
    taxonomy_name=None
    if not taxonomy_id:
        taxonomy_id,taxonomy_name=find_taxonomy_id(
            token, pkg.get("taxonomy_query","Digital Prints")
        )

    payload={
        "quantity": str(pkg.get("quantity",1)),
        "title": pkg["title"],
        "description": pkg["description"],
        "price": str(pkg["price"]),
        "who_made": pkg.get("who_made","i_did"),
        "when_made": pkg.get("when_made","2020_2026"),
        "taxonomy_id": str(taxonomy_id),
        "is_supply": "true" if pkg.get("is_supply",False) else "false",
        "type": "download",
        "should_auto_renew": "false",
    }

    tags=[str(t).strip() for t in pkg.get("tags",[]) if str(t).strip()][:13]
    if tags:
        payload["tags"]=",".join(tags)

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
        "state":listing.get("state","draft"),
        "taxonomy_id":taxonomy_id,
        "taxonomy_name":taxonomy_name
    },indent=2))

if __name__=="__main__":
    main()
