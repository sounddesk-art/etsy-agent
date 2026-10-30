#!/usr/bin/env python3
from __future__ import annotations
import json, time, zipfile, traceback
from pathlib import Path
from PIL import Image, ImageOps
from etsy_api import refresh_access_token,get_owner_shop,find_taxonomy_id,create_draft,upload_image,upload_file,get_listing,get_listing_images,get_listing_files

ASSETS=Path("assets/generated")
OUT=Path("output/drive_wall_art")
OUT.mkdir(parents=True,exist_ok=True)

def draft_authorized(item):
    if item.get("status") not in {"approved_for_draft","approved"}:
        return False,"status is not approved_for_draft"
    human=all(str(item.get(k) or "").strip() for k in ("human_reviewed_at","human_reviewed_by","human_prompt_or_notes"))
    batch=all(str(item.get(k) or "").strip() for k in ("owner_batch_authorized_at","owner_batch_authorized_by","owner_prompt_or_notes"))
    if not (human or batch): return False,"missing human review or explicit owner batch authorization"
    return True,"ok"

def norm_tags(tags):
    out=[]
    for tag in tags or []:
        tag=" ".join(str(tag).lower().strip().split())
        if len(tag)>20: tag=tag[:20].rstrip()
        if tag and tag not in out: out.append(tag)
    for tag in ["printable wall art","digital download"]:
        if tag not in out: out.append(tag)
    return out[:13]

def title_for(item):
    if item.get("title"): return str(item["title"])[:140]
    kw=item.get("keyword") or "Landscape Wall Art"
    return "{} Printable Wall Art | {} | Digital Download".format(item["display_name"],kw.title())[:140]

def description(item):
    return """{} — Printable Wall Art

Instant digital download. No physical item will be shipped.

YOU RECEIVE
• 1 high-resolution 4:5 PNG artwork in a ZIP archive
• Prepared for an 8x10 / 16x20 style aspect ratio

PRINTING
Print at home, with a local print shop, or with an online printing service. Colors may vary slightly between screens and printers.

CREATIVE PROCESS
Created with AI-assisted creative tools from seller-directed creative input, then curated and prepared for this shop.

LICENSE
Personal use only. Do not resell, redistribute, share or upload the digital file for resale.
""".format(item["display_name"])

def prepare_file(item):
    src=ASSETS/item["file"]
    if not src.exists(): raise RuntimeError("missing source image {}".format(src))
    pdir=OUT/item["id"]; pdir.mkdir(parents=True,exist_ok=True)
    outpng=pdir/"{}-printable-4x5.png".format(item["id"])
    with Image.open(src) as im:
        im=im.convert("RGB")
        fitted=ImageOps.fit(im,(2400,3000),method=Image.Resampling.LANCZOS,centering=(.5,.5))
        fitted.save(outpng,optimize=True)
    zpath=pdir/"{}-digital-download.zip".format(item["id"])
    with zipfile.ZipFile(zpath,"w",zipfile.ZIP_DEFLATED) as z: z.write(outpng,arcname=outpng.name)
    return outpng,zpath

def main():
    manifest=json.loads(Path("data/generated_manifest.json").read_text(encoding="utf-8"))
    items=manifest.get("items",[])
    result={"version":1,"created":0,"failed":0,"listings":[],"failures":[]}
    if not items:
        Path("output/etsy_upload_result.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(json.dumps(result,indent=2)); return
    token=refresh_access_token()["access_token"]
    shop=get_owner_shop(token); sid=int(shop["shop_id"])
    taxonomy_id=find_taxonomy_id(token,"Digital Prints")[0]
    for idx,item in enumerate(items,1):
        ok,reason=draft_authorized(item)
        if not ok:
            result["failed"]+=1; result["failures"].append({"source_file":item.get("file"),"id":item.get("id"),"error":reason}); continue
        try:
            image_path,download_path=prepare_file(item)
            payload={"quantity":"999","title":title_for(item),"description":description(item),
                "price":str(item.get("price","4.90")),"who_made":"i_did","when_made":"2020_2026",
                "taxonomy_id":str(taxonomy_id),"is_supply":"false","type":"download","should_auto_renew":"false",
                "tags":",".join(norm_tags(item.get("tags")))}
            print("[{}/{}] creating {}".format(idx,len(items),payload["title"]))
            listing=create_draft(token,sid,payload); lid=int(listing["listing_id"])
            upload_image(token,sid,lid,str(image_path),1,item["display_name"])
            upload_file(token,sid,lid,str(download_path),1)
            verify=get_listing(token,sid,lid); images=get_listing_images(token,sid,lid); files=get_listing_files(token,sid,lid)
            state=str(verify.get("state") or "")
            if state=="active": raise RuntimeError("safety violation: listing unexpectedly active")
            if len(images.get("results") or [])<1: raise RuntimeError("verification failed: listing image missing")
            if len(files.get("results") or [])<1: raise RuntimeError("verification failed: digital file missing")
            result["created"]+=1
            result["listings"].append({"source_file":item["file"],"source_id":item["id"],"listing_id":lid,
                "state":state or "draft","title":payload["title"],
                "image_count":len(images.get("results") or []),"file_count":len(files.get("results") or []),
                "batch_id":item.get("batch_id"),"style":item.get("style")})
            time.sleep(.3)
        except Exception as e:
            result["failed"]+=1
            result["failures"].append({"source_file":item.get("file"),"id":item.get("id"),"error":str(e),"traceback":traceback.format_exc(limit=2)})
    Path("output/etsy_upload_result.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
