#!/usr/bin/env python3
import os,json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES=["https://www.googleapis.com/auth/drive"]
INBOX="1dg_YipMZrJ5OFydC9GK1qifojdCi5zXw"
UPLOADED="1IziCTuYTfNpmWP8Yzzi8eDw0-M0Z-bWV"

def main():
    info=json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds=service_account.Credentials.from_service_account_info(info,scopes=SCOPES)
    svc=build("drive","v3",credentials=creds,cache_discovery=False)
    p=Path("output/drive_move_map.json")
    if not p.exists(): return
    for f in json.loads(p.read_text()):
        svc.files().update(
            fileId=f["id"],
            addParents=UPLOADED,
            removeParents=INBOX,
            fields="id,parents"
        ).execute()
        print("moved",f["name"])

if __name__=="__main__": main()
