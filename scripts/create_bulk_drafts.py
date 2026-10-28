#!/usr/bin/env python3
import json,sys,time
from etsy_api import refresh_access_token,get_owner_shop,find_taxonomy_id,create_draft,upload_image,upload_file
from review_gate import require_reviewed

def main():
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python scripts/create_bulk_drafts.py <manifest.json>")
    items=json.load(open(sys.argv[1],encoding="utf-8"))
    if isinstance(items,dict):
        items=items.get("items",[])
    for item in items:
        require_reviewed(item)
    token=refresh_access_token()["access_token"]
    shop=get_owner_shop(token); shop_id=shop["shop_id"]
    taxonomy_cache={}
    results=[]
    for i,item in enumerate(items,1):
        q=item.get("taxonomy_query","Digital Prints")
        if q not in taxonomy_cache:
            taxonomy_cache[q]=find_taxonomy_id(token,q)[0]
        payload={
            "quantity":str(item.get("quantity",999)),
            "title":item["title"],
            "description":item["description"],
            "price":str(item["price"]),
            "who_made":item.get("who_made","i_did"),
            "when_made":item.get("when_made","2020_2026"),
            "taxonomy_id":str(taxonomy_cache[q]),
            "is_supply":"true" if item.get("is_supply",False) else "false",
            "type":"download",
            "should_auto_renew":"false",
            "tags":",".join(item.get("tags",[])[:13])
        }
        print(f"[{i}/{len(items)}] Creating draft: {item['title'][:70]}")
        listing=create_draft(token,shop_id,payload)
        lid=listing["listing_id"]
        upload_image(token,shop_id,lid,item["image"],1,item.get("alt_text",""))
        upload_file(token,shop_id,lid,item["file"],1)
        results.append({"listing_id":lid,"title":item["title"],"state":listing.get("state","draft")})
        time.sleep(0.4)
    print(json.dumps({"shop":shop.get("shop_name"),"created":len(results),"listings":results},indent=2))

if __name__=="__main__":
    main()
