#!/usr/bin/env python3
import json, sys, os
from etsy_api import refresh_access_token, get_owner_shop, get_listing, update_listing

LISTINGS = [
    {"listing_id": 4607724874, "ref": "LND-001", "title": "Alpine Lake Sunrise Printable Wall Art | Mountain Landscape Digital Download"},
    {"listing_id": 4607725004, "ref": "LND-002", "title": "Golden Coastal Cliffs Printable Wall Art | Coastal Landscape Digital Download"},
    {"listing_id": 4607725142, "ref": "LND-003", "title": "Misty Forest River Printable Wall Art | Nature Landscape Digital Download"},
    {"listing_id": 4607725266, "ref": "LND-004", "title": "Lavender Fields Sunset Printable Wall Art | Floral Landscape Digital Download"},
    {"listing_id": 4607725378, "ref": "LND-005", "title": "Autumn Mountain Valley Printable Wall Art | Fall Landscape Digital Download"},
    {"listing_id": 4607725508, "ref": "LND-006", "title": "Scandinavian Fjord Printable Wall Art | Nordic Landscape Digital Download"},
]

def subject_from_title(title):
    return title.split(" Printable Wall Art", 1)[0].strip()

def description(title, ref):
    name = subject_from_title(title)
    return """{} — Printable Wall Art

Instant digital download. No physical item will be shipped.

YOU RECEIVE
• 1 high-resolution PNG artwork in a ZIP archive
• Pixel dimensions: 2400 × 3000 px
• Aspect ratio: 4:5
• Equivalent to 8 × 10 inches at 300 PPI

PRINTING
Print at home, with a local print shop, or with an online printing service. Colors may vary slightly between screens and printers.

CREATIVE PROCESS
Created with AI-assisted creative tools from seller-directed creative input, then curated and prepared for this shop.

LICENSE
Personal use only. Do not resell, redistribute, share or upload the digital file for resale.

Internal reference: {}
""".format(name, ref)

def main():
    os.makedirs("output", exist_ok=True)
    token = refresh_access_token()["access_token"]
    shop = get_owner_shop(token)
    sid = int(shop["shop_id"])
    result = {"updated": 0, "failed": 0, "listings": [], "failures": []}
    for item in LISTINGS:
        lid = int(item["listing_id"])
        try:
            before = get_listing(token, sid, lid)
            state = str(before.get("state") or "")
            if state == "active":
                raise RuntimeError("safety stop: listing is active; refusing to edit live listing")
            payload = {"title": item["title"], "description": description(item["title"], item["ref"])}
            update_listing(token, sid, lid, payload)
            after = get_listing(token, sid, lid)
            if str(after.get("title") or "") != item["title"]:
                raise RuntimeError("verification failed: title mismatch after update")
            desc = str(after.get("description") or "")
            if "2400 × 3000 px" not in desc:
                raise RuntimeError("verification failed: pixel resolution missing")
            if not desc.rstrip().endswith("Internal reference: " + item["ref"]):
                raise RuntimeError("verification failed: internal reference missing at bottom")
            result["updated"] += 1
            result["listings"].append({"listing_id": lid, "state": state or "draft", "title": item["title"], "ref": item["ref"]})
            print("updated {}: {}".format(lid, item["title"]))
        except Exception as e:
            result["failed"] += 1
            result["failures"].append({"listing_id": lid, "error": str(e)})
            print("FAILED {}: {}".format(lid, e), file=sys.stderr)
    with open("output/update_existing_drafts_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["failed"]:
        sys.exit(2)

if __name__ == "__main__":
    main()