#!/usr/bin/env python3
from pathlib import Path
import json, zipfile, time
from etsy_api import refresh_access_token,get_owner_shop,find_taxonomy_id,create_draft,upload_image,upload_file

ASSET_DIR=Path("assets/final")
OUT=Path("output/final")
OUT.mkdir(parents=True,exist_ok=True)

items=[
{"file":"01-coffee-first.png","title":"Highland Cow Coffee Printable Wall Art | Coffee First Funny Kitchen Decor | Digital Download","tags":["highland cow art","coffee wall art","cow kitchen decor","funny coffee print","rustic wall decor","printable wall art","farmhouse printable","cozy kitchen art","digital download","highland cow print","coffee lover gift","cottagecore decor","instant download"]},
{"file":"02-good-vibes-only.png","title":"Good Vibes Only Beach Printable | Sunset Coastal Wall Art | Positive Quote Digital Download","tags":["good vibes print","beach wall art","sunset printable","coastal wall decor","positive quote art","summer wall art","ocean printable","printable wall art","digital download","boho beach decor","feel good poster","instant download","beach lover gift"]},
{"file":"03-just-one-more-chapter.png","title":"Just One More Chapter Cat Printable | Book Lover Wall Art | Cozy Reading Digital Download","tags":["book lover print","cat wall art","reading printable","bookish wall decor","cozy reading art","library wall art","cat lover gift","printable wall art","digital download","book nook decor","reader gift","instant download","cozy cat print"]},
{"file":"04-adventure-awaits.png","title":"Adventure Awaits Mountain Printable | Alpine Lake Wall Art | Travel Quote Digital Download","tags":["mountain wall art","adventure print","alpine printable","lake wall decor","travel quote art","nature wall art","hiking decor","printable wall art","digital download","mountain poster","outdoor lover gift","instant download","cabin wall decor"]},
{"file":"05-life-is-better-with-a-dog.png","title":"Life Is Better With a Dog Printable | Dog Lover Wall Art | Happy Dog Digital Download","tags":["dog lover print","dog wall art","pet lover decor","happy dog print","dog quote art","pet wall decor","printable wall art","digital download","dog owner gift","golden dog art","instant download","cute dog poster","home with dogs"]},
{"file":"06-stay-kind.png","title":"Stay Kind Wildflower Printable | Botanical Wall Art | Positive Quote Digital Download","tags":["stay kind print","wildflower art","botanical print","flower wall art","positive quote","cottagecore art","printable wall art","digital download","floral wall decor","kindness poster","instant download","boho flower print","garden lover gift"]},
{"file":"07-slow-down.png","title":"Slow Down Sea Turtle Printable | Ocean Wall Art | Mindful Quote Digital Download","tags":["sea turtle art","ocean wall art","slow down print","coastal printable","mindful wall art","turtle lover gift","printable wall art","digital download","ocean decor","beach house print","instant download","calm wall decor","marine life art"]},
{"file":"08-good-things-take-time.png","title":"Good Things Take Time Cat Printable | Funny Cat Wall Art | Positive Digital Download","tags":["cat wall art","cat quote print","funny cat decor","positive wall art","cool cat print","cat lover gift","printable wall art","digital download","motivational cat","instant download","cute cat poster","cozy wall decor","cat sunglasses"]},
{"file":"09-trust-the-process.png","title":"Trust The Process Moon Phase Printable | Celestial Wall Art | Boho Digital Download","tags":["moon phase art","celestial print","trust the process","boho wall art","moon wall decor","spiritual decor","printable wall art","digital download","lunar wall art","celestial poster","instant download","mystic wall decor","moon lover gift"]},
{"file":"10-radiate-good-energy.png","title":"Radiate Good Energy Sun Printable | Boho Sun Wall Art | Positive Quote Digital Download","tags":["sun wall art","good energy print","boho sun print","positive wall art","celestial decor","sunshine poster","printable wall art","digital download","boho wall decor","radiate positivity","instant download","sun lover gift","warm neutral art"]}
]

def description(title):
    lead=title.split("|")[0].strip()
    return f"""{lead}

Instant digital download printable wall art. No physical item will be shipped.

YOU RECEIVE
• 1 high-quality PNG artwork
• Delivered in a ZIP file

The preview artwork shown in this listing is the same artwork included in the download. Colors may vary slightly between screens and printers.

AI DISCLOSURE
This design was created with AI-assisted creative tools and then selected, curated and prepared for sale by NiceDesignStudios.

PERSONAL USE
For personal use only. Please do not resell or redistribute the digital file."""

def main():
    missing=[x["file"] for x in items if not (ASSET_DIR/x["file"]).exists()]
    if missing:
        raise SystemExit("Missing final assets: "+", ".join(missing))
    token=refresh_access_token()["access_token"]
    shop=get_owner_shop(token); shop_id=shop["shop_id"]
    taxonomy_id=find_taxonomy_id(token,"Digital Prints")[0]
    results=[]
    for i,item in enumerate(items,1):
        src=ASSET_DIR/item["file"]
        zpath=OUT/(src.stem+"-download.zip")
        with zipfile.ZipFile(zpath,"w",zipfile.ZIP_DEFLATED) as z:
            z.write(src,arcname=src.name)
        payload={
            "quantity":"999",
            "title":item["title"],
            "description":description(item["title"]),
            "price":"4.90",
            "who_made":"i_did",
            "when_made":"2020_2026",
            "taxonomy_id":str(taxonomy_id),
            "is_supply":"false",
            "type":"download",
            "should_auto_renew":"false",
            "tags":",".join(item["tags"][:13])
        }
        print(f"[{i}/10] Creating final draft: {item['title']}")
        listing=create_draft(token,shop_id,payload)
        lid=listing["listing_id"]
        upload_image(token,shop_id,lid,str(src),1,item["title"].split("|")[0].strip())
        upload_file(token,shop_id,lid,str(zpath),1)
        results.append({"listing_id":lid,"title":item["title"]})
        time.sleep(0.4)
    print(json.dumps({"shop":shop.get("shop_name"),"created":len(results),"listings":results},indent=2))

if __name__=="__main__":
    main()
