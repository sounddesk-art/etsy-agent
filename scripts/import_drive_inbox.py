#!/usr/bin/env python3
import os, io, json, re, time
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES=["https://www.googleapis.com/auth/drive"]
INBOX=(os.environ.get("GOOGLE_DRIVE_INBOX_FOLDER_ID") or "1dg_YipMZrJ5OFydC9GK1qifojdCi5zXw")
MANIFESTS=(os.environ.get("GOOGLE_DRIVE_MANIFESTS_FOLDER_ID") or "1_rdYUXofqyfXqD1Rijhfypc4hk9oWyLW")

WORK=Path("drive_inbox")
ASSETS=Path("assets/generated")
WORK.mkdir(parents=True,exist_ok=True)
ASSETS.mkdir(parents=True,exist_ok=True)

def service():
    info=json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds=service_account.Credentials.from_service_account_info(info,scopes=SCOPES)
    return build("drive","v3",credentials=creds,cache_discovery=False)

def list_files(svc,folder):
    q="'{}' in parents and trashed=false".format(folder)
    out=[]; token=None
    while True:
        r=svc.files().list(q=q,pageSize=1000,pageToken=token,orderBy="createdTime",
            fields="nextPageToken,files(id,name,mimeType,parents,createdTime,modifiedTime,size)").execute()
        out+=r.get("files",[])
        token=r.get("nextPageToken")
        if not token: return out

def download(svc,file_id,dest):
    req=svc.files().get_media(fileId=file_id)
    with io.FileIO(dest,"wb") as fh:
        dl=MediaIoBaseDownload(fh,req); done=False
        while not done: _,done=dl.next_chunk()

def slugify(name):
    s=re.sub(r"\.[^.]+$","",name)
    s=re.sub(r"[^a-zA-Z0-9]+","-",s).strip("-").lower()
    return s[:90] or "art-{}".format(int(time.time()))

def infer_series(name):
    n=name.lower()
    if any(x in n for x in ["moon","zodiac","star","lunar","celestial","eclipse"]): return "celestial"
    if any(x in n for x in ["flower","botan","sun","daisy","olive","lemon","eucalyptus"]): return "botanical-sun"
    if any(x in n for x in ["mountain","lake","coast","beach","landscape","forest","fjord","alpine","canyon","hill"]): return "landscapes"
    return "other"

def manifests(svc):
    by_file={}
    for f in list_files(svc,MANIFESTS):
        if not (f["mimeType"]=="application/json" or f["name"].lower().endswith(".json")): continue
        p=WORK/f["name"]; download(svc,f["id"],p)
        try:
            data=json.loads(p.read_text(encoding="utf-8"))
            root_auth={}
            if isinstance(data,dict):
                for k in ("owner_batch_authorized_at","owner_batch_authorized_by","owner_prompt_or_notes","batch_id","style"):
                    root_auth[k]=data.get(k)
                for item in data.get("items",[]):
                    key=item.get("file") or item.get("filename")
                    if key: by_file[key]={**root_auth,**item}
        except Exception as e:
            print("Manifest warning:",f["name"],e)
    return by_file

def main():
    svc=service(); meta_map=manifests(svc)
    images=[f for f in list_files(svc,INBOX) if f["mimeType"].startswith("image/")]
    items=[]; move_map=[]
    for i,f in enumerate(images,1):
        ext=Path(f["name"]).suffix.lower()
        if ext not in [".png",".jpg",".jpeg",".webp"]: continue
        print("[{}/{}] {}".format(i,len(images),f["name"]))
        local=ASSETS/f["name"]; download(svc,f["id"],local)
        meta=meta_map.get(f["name"],{})
        series=meta.get("series") or infer_series(f["name"])
        display=meta.get("display_name") or Path(f["name"]).stem.replace("_"," ").replace("-"," ").title()
        tags=meta.get("tags") or [series.replace("-"," "),display.lower(),"printable wall art","digital download"]
        item={
            "id":meta.get("id") or slugify(f["name"]),
            "display_name":display,"series":series,"file":f["name"],
            "products":meta.get("products") or ["wall_art"],"tags":tags,
            "keyword":meta.get("keyword"),"title":meta.get("title"),"price":meta.get("price","4.90"),
            "status":meta.get("status","needs_review"),"drive_file_id":f["id"],
            "batch_id":meta.get("batch_id"),"style":meta.get("style"),
            "owner_batch_authorized_at":meta.get("owner_batch_authorized_at"),
            "owner_batch_authorized_by":meta.get("owner_batch_authorized_by"),
            "owner_prompt_or_notes":meta.get("owner_prompt_or_notes"),
            "human_reviewed_at":meta.get("human_reviewed_at"),
            "human_reviewed_by":meta.get("human_reviewed_by"),
            "human_prompt_or_notes":meta.get("human_prompt_or_notes")
        }
        items.append(item); move_map.append({"id":f["id"],"name":f["name"]})
    Path("data/generated_manifest.json").write_text(json.dumps({"version":4,"items":items},indent=2),encoding="utf-8")
    Path("output").mkdir(exist_ok=True)
    Path("output/drive_move_map.json").write_text(json.dumps(move_map,indent=2),encoding="utf-8")
    print("Prepared {} new Drive image(s).".format(len(items)))

if __name__=="__main__": main()
