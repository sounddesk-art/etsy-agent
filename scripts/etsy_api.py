#!/usr/bin/env python3
import os, json, mimetypes, requests

BASE="https://api.etsy.com/v3"

def require(name):
    v=os.environ.get(name)
    if not v:
        raise RuntimeError(f"Missing environment variable: {name}")
    return v

def api_key_header():
    return f"{require('ETSY_KEYSTRING')}:{require('ETSY_SHARED_SECRET')}"

def refresh_access_token():
    key=require("ETSY_KEYSTRING")
    refresh=require("ETSY_REFRESH_TOKEN")
    r=requests.post(
        f"{BASE}/public/oauth/token",
        data={"grant_type":"refresh_token","client_id":key,"refresh_token":refresh},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()

def auth_headers(access_token):
    return {
        "x-api-key": api_key_header(),
        "Authorization": f"Bearer {access_token}",
    }

def api_headers():
    return {"x-api-key": api_key_header()}

def get_me(access_token):
    r=requests.get(f"{BASE}/application/users/me",headers=auth_headers(access_token),timeout=30)
    r.raise_for_status()
    return r.json()

def user_id_from_token(access_token):
    prefix=access_token.split(".",1)[0]
    if not prefix.isdigit():
        raise RuntimeError("Could not derive Etsy user ID from OAuth access token.")
    return int(prefix)

def get_owner_shop(access_token):
    user_id=user_id_from_token(access_token)
    r=requests.get(
        f"{BASE}/application/users/{user_id}/shops",
        headers=auth_headers(access_token),
        timeout=30,
    )
    r.raise_for_status()
    return r.json()

def get_seller_taxonomy(access_token):
    r=requests.get(
        f"{BASE}/application/seller-taxonomy/nodes",
        headers=auth_headers(access_token),
        timeout=60,
    )
    r.raise_for_status()
    return r.json()

def flatten_taxonomy(nodes):
    out=[]
    def walk(node):
        out.append(node)
        for child in node.get("children") or []:
            walk(child)
    for node in nodes:
        walk(node)
    return out

def find_taxonomy_id(access_token, query):
    data=get_seller_taxonomy(access_token)
    nodes=flatten_taxonomy(data.get("results") or [])
    q=(query or "").strip().lower()
    if not q:
        raise RuntimeError("taxonomy_query is empty")
    exact=[n for n in nodes if (n.get("name") or "").strip().lower()==q]
    if exact:
        exact.sort(key=lambda n:n.get("level",0), reverse=True)
        return exact[0]["id"], exact[0]["name"]
    contains=[n for n in nodes if q in (n.get("name") or "").lower()]
    if contains:
        contains.sort(key=lambda n:n.get("level",0), reverse=True)
        return contains[0]["id"], contains[0]["name"]
    raise RuntimeError(f"No Etsy seller taxonomy node matched: {query}")

def create_draft(access_token, shop_id, payload):
    r=requests.post(
        f"{BASE}/application/shops/{shop_id}/listings",
        headers=auth_headers(access_token),
        data=payload,
        timeout=60,
    )
    if not r.ok:
        try:
            print("Etsy create draft error:", r.json())
        except Exception:
            print("Etsy create draft HTTP", r.status_code, r.text[:500])
    r.raise_for_status()
    return r.json()

def update_listing(access_token, shop_id, listing_id, payload):
    r=requests.patch(
        f"{BASE}/application/shops/{shop_id}/listings/{listing_id}",
        headers=auth_headers(access_token),
        data=payload,
        timeout=60,
    )
    if not r.ok:
        try:
            print("Etsy update listing error:", r.json())
        except Exception:
            print("Etsy update listing HTTP", r.status_code)
    r.raise_for_status()
    return r.json()


def get_listing(access_token,shop_id,listing_id):
    r=requests.get(f"{BASE}/application/listings/{listing_id}",headers=auth_headers(access_token),timeout=30)
    r.raise_for_status()
    return r.json()

def get_listing_images(access_token,shop_id,listing_id):
    r=requests.get(f"{BASE}/application/listings/{listing_id}/images",headers=auth_headers(access_token),timeout=30)
    r.raise_for_status()
    return r.json()

def get_listing_files(access_token,shop_id,listing_id):
    r=requests.get(f"{BASE}/application/shops/{shop_id}/listings/{listing_id}/files",headers=auth_headers(access_token),timeout=30)
    r.raise_for_status()
    return r.json()

def upload_image(access_token, shop_id, listing_id, path, rank=1, alt_text=""):
    with open(path,"rb") as fh:
        r=requests.post(
            f"{BASE}/application/shops/{shop_id}/listings/{listing_id}/images",
            headers=auth_headers(access_token),
            files={"image":(os.path.basename(path),fh)},
            data={"rank":rank,"alt_text":alt_text},
            timeout=120,
        )
    r.raise_for_status()
    return r.json()

def upload_file(access_token, shop_id, listing_id, path, rank=1):
    with open(path,"rb") as fh:
        r=requests.post(
            f"{BASE}/application/shops/{shop_id}/listings/{listing_id}/files",
            headers=auth_headers(access_token),
            files={"file":(
                os.path.basename(path),
                fh,
                mimetypes.guess_type(path)[0] or "application/octet-stream"
            )},
            data={"name":os.path.basename(path),"rank":rank},
            timeout=120,
        )
    if not r.ok:
        try:
            print("Etsy upload file error:", r.json())
        except Exception:
            print("Etsy upload file HTTP", r.status_code)
    r.raise_for_status()
    return r.json()

if __name__=="__main__":
    tokens=refresh_access_token()
    access=tokens["access_token"]
    me=get_me(access)
    shop=get_owner_shop(access)
    print(json.dumps({
        "connection":"ok",
        "user_id":user_id_from_token(access),
        "shop_id":shop.get("shop_id"),
        "shop_name":shop.get("shop_name"),
        "scope":tokens.get("scope"),
    },indent=2))
    returned=tokens.get("refresh_token")
    current=os.environ.get("ETSY_REFRESH_TOKEN")
    if returned and returned != current:
        print("WARNING: Etsy returned a different refresh token. Update ETSY_REFRESH_TOKEN before another refresh run.")
