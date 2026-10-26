#!/usr/bin/env python3
import os, io, json, re, time
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES=["https://www.googleapis.com/auth/drive"]
INBOX="1dg_YipMZrJ5OFydC9GK1qifojdCi5zXw"
UPLOADED="1IziCTuYTfNpmWP8Yzzi8eDw0-M0Z-bWV"
MANIFESTS="1_rdYUXofqyfXqD1Rijhfypc4hk9oWyLW"

WORK=Path("drive_inbox")
ASSETS=Path("assets/generated")
WORK.mkdir(parents=True,exist_ok=True)
ASSETS.mkdir(parents=True,exist_ok=True)

DEFAULT_PRODUCTS={
  "cozy-animals":["wall_art","greeting_card","postcard"],
  "landscapes":["wall_art","greeting_card","postcard"],
  "celestial":["wall_art","greeting_card","postcard","bookmark"],
  "botanical-sun":["wall_art","greeting_card","postcard","bookmark"]
}

def service():
    info=json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds=service_account.Credentials.from_service_account_info(info,scopes=SCOPES)
    return build("drive","v3",credentials=creds,cache_discovery=False)

def list_files(svc,folder):
    q=f"'{folder}' in parents and trashed=false"
    out=[]; token=None
    while True:
        r=svc.files().list(
            q=q,pageSize=1000,pageToken=token,orderBy="createdTime",
            fields="nextPageToken,files(id,name,mimeType,parents,createdTime,modifiedTime,size)"
        ).execute()
        out+=r.get("files",[])
        token=r.get("nextPageToken")
        if not token: return out

def download(svc,file_id,dest):
    req=svc.files().get_media(fileId=file_id)
    with io.FileIO(dest,"wb") as fh:
        dl=MediaIoBaseDownload(fh,req)
        done=False
        while not done: _,done=dl.next_chunk()

def slugify(name):
    s=re.sub(r"\.[^.]+$","",name)
    s=re.sub(r"[^a-zA-Z0-9]+","-",s).strip("-").lower()
    return s[:70] or f"art-{int(time.time())}"

def infer_series(name):
    n=name.lower()
    if any(x in n for x in ["moon","zodiac","star","lunar","celestial","eclipse"]): return "celestial"
    if any(x in n for x in ["flower","botan","sun","daisy","olive","lemon","eucalyptus"]): return "botanical-sun"
    if any(x in n for x in ["mountain","lake","coast","beach","landscape","forest","fjord","alpine"]): return "landscapes"
    return "cozy-animals"

def manifests(svc):
    by_file={}
    for f in list_files(svc,MANIFESTS):
        if not (f["mimeType"]=="application/json" or f["name"].lower().endswith(".json")):
            continue
        p=WORK/f["name"]; download(svc,f["id"],p)
        try:
            data=json.loads(p.read_text(encoding="utf-8"))
            for item in data.get("items",[]):
                key=item.get("file") or item.get("filename")
                if key: by_file[key]=item
        except Exception as e:
            print("Manifest warning:",f["name"],e)
    return by_file

def main():
    svc=service()
    meta_map=manifests(svc)
    images=[f for f in list_files(svc,INBOX) if f["mimeType"].startswith("image/")]
    items=[]; move_map=[]

    for i,f in enumerate(images,1):
        ext=Path(f["name"]).suffix.lower()
        if ext not in [".png",".jpg",".jpeg",".webp"]:
            continue
        print(f"[{i}/{len(images)}] {f['name']}")
        local=ASSETS/f["name"]
        download(svc,f["id"],local)

        meta=meta_map.get(f["name"],{})
        series=meta.get("series") or infer_series(f["name"])
        display=meta.get("display_name") or Path(f["name"]).stem.replace("_"," ").replace("-"," ").title()
        products=meta.get("products") or DEFAULT_PRODUCTS.get(series,["wall_art","greeting_card","postcard"])
        tags=meta.get("tags") or [series.replace("-"," "),display.lower(),"printable art","digital download"]

        items.append({
            "id":meta.get("id") or slugify(f["name"]),
            "display_name":display,
            "series":series,
            "file":f["name"],
            "products":products,
            "tags":tags,
            "status":"approved",
            "drive_file_id":f["id"]
        })
        move_map.append({"id":f["id"],"name":f["name"]})

    Path("data/generated_manifest.json").write_text(
        json.dumps({"version":3,"items":items},indent=2),encoding="utf-8")
    Path("output").mkdir(exist_ok=True)
    Path("output/drive_move_map.json").write_text(
        json.dumps(move_map,indent=2),encoding="utf-8")
    print(f"Prepared {len(items)} new Drive image(s).")

if __name__=="__main__":
    main()
