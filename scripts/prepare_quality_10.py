#!/usr/bin/env python3
"""Prepare the ten owner-approved quality Etsy drafts for manual publication."""
from __future__ import annotations
import json, time
from etsy_api import refresh_access_token,get_owner_shop,update_listing

AI=("CREATIVE PROCESS\nThis artwork was created with AI-assisted creative tools "
    "from seller-directed creative input, then individually selected, curated "
    "and prepared for this shop.")

def desc(lead,focus):
    return f"""\{lead}

A colorful printable artwork created for \{focus}. Instant digital download; no physical item will be shipped.

YOU RECEIVE
• High-resolution digital artwork
• Print-ready digital file supplied with this listing
• Artwork shown in the preview is the artwork included in the download

PRINTING
Print at home, with a local print shop, or with an online printing service. Colors may vary slightly between screens and printers.

\{AI}

LICENSE
Personal use only. Do not resell, redistribute, share, or upload the digital file for resale.
""".replace("\\","")

ITEMS=[
(4603491287,"Highland Cow Coffee Printable | Highland Cow Wall Art | Funny Kitchen Decor",
 ["highland cow wall","highland cow art","farmhouse wall art","coffee wall art","cow kitchen decor","highland cow print","farmhouse decor","rustic wall art","cow lover gift","animal wall art","printable wall art","digital download","coffee lover gift"],
 "Highland Cow Coffee Printable","highland cow lovers, cozy kitchens and farmhouse interiors"),
(4603491319,"Good Vibes Only Beach Printable | Coastal Sunset Wall Art | Positive Quote",
 ["coastal sunset wall","coastal wall art","beach house decor","sunset wall art","ocean wall art","beach wall art","coastal sunset art","positive quote art","printable wall art","coastal wall decor","beach house art","digital download","good vibes print"],
 "Good Vibes Only Beach Printable","coastal rooms, beach lovers and positive home decor"),
(4603512936,"Just One More Chapter Cat Printable | Book Lover Wall Art | Reading Nook Decor",
 ["book lover wall art","reading nook decor","book lover gift","bookish wall art","library wall decor","home library decor","cat wall art","reader gift","cozy reading art","printable wall art","digital download","book nook decor","cat lover gift"],
 "Just One More Chapter Cat Printable","book lovers, reading nooks and cozy home libraries"),
(4603512982,"Adventure Awaits Mountain Printable | Mountain Wall Art | Alpine Lake Decor",
 ["mountain printable","mountain wall art","printable wall art","nature wall art","landscape wall art","mountain print","landscape printable","alpine wall art","lake wall decor","travel quote art","outdoor lover gift","digital download","cabin wall decor"],
 "Adventure Awaits Mountain Printable","mountain lovers, travel-inspired interiors and cabins"),
(4603513014,"Life Is Better With a Dog Printable | Dog Lover Wall Art | Happy Dog Decor",
 ["dog lover print","dog wall art","dog lover gift","pet lover decor","happy dog print","dog quote art","pet wall decor","dog owner gift","golden dog art","cute dog poster","printable wall art","digital download","home with dogs"],
 "Life Is Better With a Dog Printable","dog lovers, pet-friendly homes and cheerful gallery walls"),
(4603491485,"Stay Kind Wildflower Printable | Botanical Wall Art | Positive Quote Decor",
 ["wildflower art","botanical print","flower wall art","positive quote","cottagecore art","floral wall decor","wildflower print","botanical wall art","kindness poster","garden lover gift","printable wall art","digital download","boho flower print"],
 "Stay Kind Wildflower Printable","botanical interiors, cottagecore rooms and positive decor"),
(4603491521,"Slow Down Sea Turtle Printable | Ocean Wall Art | Mindful Coastal Decor",
 ["sea turtle art","ocean wall art","coastal printable","turtle lover gift","ocean decor","beach house print","marine life art","mindful wall art","calm wall decor","slow down print","printable wall art","digital download","coastal wall decor"],
 "Slow Down Sea Turtle Printable","ocean lovers, calm rooms and mindful coastal decor"),
(4603513112,"Good Things Take Time Cat Printable | Funny Cat Wall Art | Positive Quote",
 ["cat wall art","cat quote print","funny cat decor","cat lover gift","cute cat poster","motivational cat","positive wall art","cat sunglasses","cozy wall decor","funny cat print","printable wall art","digital download","cat lover decor"],
 "Good Things Take Time Cat Printable","cat lovers, playful rooms and positive gallery walls"),
(4603491575,"Trust The Process Moon Phase Printable | Moon Phase Wall Art | Celestial Decor",
 ["moon phase wall art","celestial wall art","moon phases wall art","spiritual wall art","moon wall art","moon phases print","moon phase print","moon phase decor","astrology wall art","boho wall decor","moon phase poster","celestial decor","trust the process"],
 "Trust The Process Moon Phase Printable","celestial, spiritual and boho interiors"),
(4603491613,"Radiate Good Energy Sun Printable | Boho Sun Wall Art | Positive Quote",
 ["boho sun wall art","boho wall decor","printable wall art","neutral wall art","abstract sun print","terracotta wall art","sunburst wall art","boho sun print","sun wall decor","boho home decor","positive wall art","digital download","good energy print"],
 "Radiate Good Energy Sun Printable","boho interiors, warm gallery walls and positive decor"),
]

def main():
    token_data=refresh_access_token()
    scope=set(str(token_data.get("scope") or "").split())
    if "listings_w" not in scope:
        raise SystemExit("BLOCKED: current Etsy OAuth token lacks listings_w")
    access=token_data["access_token"]
    shop=get_owner_shop(access); shop_id=int(shop["shop_id"])
    updated=[]
    for lid,title,tags,lead,focus in ITEMS:
        payload={
          "title":title,"description":desc(lead,focus),"price":"4.90",
          "quantity":"999","should_auto_renew":"false",
          "tags":",".join(tags[:13]),
        }
        result=update_listing(access,shop_id,lid,payload)
        if str(result.get("state"))!="draft":
            raise SystemExit(f"SAFETY STOP: listing {lid} is not draft after metadata update")
        updated.append({"listing_id":lid,"title":title})
        time.sleep(0.15)
    print(json.dumps({"status":"READY_FOR_OWNER_PUBLICATION","updated":len(updated),
                      "published":0,"items":updated},indent=2))

if __name__=="__main__":
    main()
