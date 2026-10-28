#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageOps
import json, zipfile
from review_gate import review_errors

ASSETS=Path("assets/generated")
OUT=Path("output/repurposed")
OUT.mkdir(parents=True,exist_ok=True)

PRODUCTS={
 "wall_art":(3000,4500),
 "greeting_card":(1500,2100),
 "postcard":(1800,1200),
 "bookmark":(900,3150),
}

def fit(im,size):
    return ImageOps.fit(im,size,method=Image.Resampling.LANCZOS,centering=(.5,.5))

def main():
    manifest_path=Path("data/generated_manifest.json")
    if not manifest_path.exists():
        raise SystemExit("Missing data/generated_manifest.json")
    data=json.loads(manifest_path.read_text(encoding="utf-8"))
    out=[]
    for item in data["items"]:
        errors=review_errors(item)
        if errors:
            print(f"review-blocked {item.get('id','item')}: {'; '.join(errors)}")
            continue
        src=ASSETS/item["file"]
        if not src.exists():
            print("missing",src); continue
        im=Image.open(src).convert("RGB")
        for product in item.get("products",[]):
            if product not in PRODUCTS: continue
            pdir=OUT/item["id"]/product
            pdir.mkdir(parents=True,exist_ok=True)
            img=fit(im,PRODUCTS[product])
            png=pdir/f"{item['id']}-{product}.png"
            img.save(png,optimize=True)
            zp=pdir/f"{item['id']}-{product}.zip"
            with zipfile.ZipFile(zp,"w",zipfile.ZIP_DEFLATED) as z:
                z.write(png,arcname=png.name)
            out.append({**item,"product":product,"image":str(png),"download":str(zp)})
    Path("output/repurposed_manifest.json").write_text(json.dumps({"items":out},indent=2),encoding="utf-8")
    print(f"Repurposed {len(out)} product variants.")

if __name__=="__main__": main()
