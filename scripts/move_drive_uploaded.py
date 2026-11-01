#!/usr/bin/env python3
import os,json,datetime
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES=["https://www.googleapis.com/auth/drive"]
INBOX=(os.environ.get("GOOGLE_DRIVE_INBOX_FOLDER_ID") or "1dg_YipMZrJ5OFydC9GK1qifojdCi5zXw")
ARCHIVE=(os.environ.get("GOOGLE_DRIVE_ARCHIVE_FOLDER_ID") or "148AAzhyN9kZQ4x50JpEHy5_a2PclUnTV")

def main():
    info=json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds=service_account.Credentials.from_service_account_info(info,scopes=SCOPES)
    svc=build("drive","v3",credentials=creds,cache_discovery=False)
    move_path=Path("output/drive_move_map.json"); result_path=Path("output/etsy_upload_result.json")
    if not move_path.exists() or not result_path.exists(): raise SystemExit("missing move map or Etsy upload result")
    move_map={x["name"]:x for x in json.loads(move_path.read_text())}
    result=json.loads(result_path.read_text()); succeeded={x["source_file"] for x in result.get("listings",[])}
    moved=[]
    for name in sorted(succeeded):
        f=move_map.get(name)
        if not f: continue
        svc.files().update(fileId=f["id"],addParents=ARCHIVE,removeParents=INBOX,fields="id,parents").execute()
        moved.append({"id":f["id"],"name":name}); print("archived",name)
    receipt={**result,"drive_archived":moved,"archived_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat()}
    Path("output").mkdir(exist_ok=True)
    receipt_path=Path("output")/"receipt-latest.json"
    receipt_path.write_text(json.dumps(receipt,indent=2),encoding="utf-8")
    print(json.dumps({"archived":len(moved),"receipt":str(receipt_path),"failed":result.get("failed",0)},indent=2))

if __name__=="__main__": main()
