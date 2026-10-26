#!/usr/bin/env python3
import json, time
from pathlib import Path
from etsy_api import refresh_access_token,get_owner_shop,find_taxonomy_id,create_draft,upload_image,upload_file

TEMPLATES=json.loads(Path("data/product_templates.json").read_text())
M=json.loads(Path("output/repurposed_manifest.json").read_text())

def desc(item,t):
    return f"""{item['display_name']} — {t['label']}

Instant digital download. No physical item will be shipped.

YOU RECEIVE
• High-resolution digital artwork
• {t['delivery']}

LICENSE
Personal use and small commercial use of up to 100 physical end products is included.
You may print the design on physical items such as greeting cards for sale.
You may not resell, redistribute, share, or upload the digital file itself, and may not upload the design to print-on-demand marketplaces.

AI DISCLOSURE
Created with AI-assisted creative tools and curated, selected and prepared by NiceDesignStudios.
"""

def main():
    token=refresh_access_token()["access_token"]
    shop=get_owner_shop(token); sid=shop["shop_id"]
    tax=find_taxonomy_id(token,"Digital Prints")[0]
    made=[]
    for i,item in enumerate(M["items"],1):
        t=TEMPLATES[item["product"]]
        title=f"{item['display_name']} | {t['label']} | Digital Download"
        tags=(item.get("tags") or [])[:11] + [t["label"].lower(),"digital download"]
        payload={
          "quantity":"999","title":title,"description":desc(item,t),"price":t["price"],
          "who_made":"i_did","when_made":"2020_2026","taxonomy_id":str(tax),
          "is_supply":"false","type":"download","should_auto_renew":"false",
          "tags":",".join(tags[:13])
        }
        print(f"[{i}/{len(M['items'])}] {title}")
        l=create_draft(token,sid,payload); lid=l["listing_id"]
        upload_image(token,sid,lid,item["image"],1,item["display_name"])
        upload_file(token,sid,lid,item["download"],1)
        made.append({"listing_id":lid,"title":title,"source_id":item["id"],"product":item["product"]})
        time.sleep(.35)
    print(json.dumps({"created":len(made),"listings":made},indent=2))
if __name__=="__main__": main()
