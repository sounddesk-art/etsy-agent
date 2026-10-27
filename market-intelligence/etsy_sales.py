"""Read-only Etsy shop sales collector. No buyer data is stored."""
import argparse,csv,json,os,urllib.parse,urllib.request
from collections import defaultdict
from pathlib import Path

BASE="https://openapi.etsy.com/v3/application"
def money(obj):
 if not isinstance(obj,dict) or not obj.get("divisor"):return None
 return float(obj["amount"])/float(obj["divisor"])
def fetch_pages(url,headers,fetch=None):
 fetch=fetch or request
 offset=0
 while True:
  params=urllib.parse.urlencode({"limit":100,"offset":offset})
  data=fetch(url+"?"+params,headers)
  records=data.get("results",[])
  if not isinstance(records,list):raise ValueError("invalid Etsy payload")
  yield from records
  offset+=len(records)
  if not records or offset>=data.get("count",offset):break
def request(url,headers):
 req=urllib.request.Request(url,headers=headers,method="GET")
 with urllib.request.urlopen(req,timeout=25) as resp:
  return json.load(resp)
def aggregate_transactions(transactions,listing_keywords):
 out=defaultdict(lambda:dict(orders=0,units=0,revenue=0.0,currency=None))
 seen=set()
 for t in transactions:
  tid=t.get("transaction_id");lid=str(t.get("listing_id",""))
  if not tid or tid in seen:continue
  seen.add(tid)
  if lid not in listing_keywords:continue
  price=t.get("price") or {}
  amount=money(price)
  if amount is None:continue
  currency=price.get("currency_code","")
  key=(listing_keywords[lid],currency)
  rec=out[key];qty=int(t.get("quantity") or 0)
  rec["orders"]+=1;rec["units"]+=qty;rec["revenue"]+=amount*qty;rec["currency"]=currency
 return [dict(keyword=k[0],**v) for k,v in sorted(out.items())]
def collect(shop_id,key,token,mapping,fetch=None):
 headers={"x-api-key":key,"Authorization":"Bearer "+token}
 url=f"{BASE}/shops/{int(shop_id)}/transactions"
 return aggregate_transactions(fetch_pages(url,headers,fetch),mapping)
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--mapping",required=True,help="CSV columns listing_id,keyword")
 p.add_argument("--output",required=True)
 a=p.parse_args()
 with open(a.mapping,encoding="utf-8-sig",newline="") as f:
  mapping={str(r["listing_id"]).strip():r["keyword"].strip().lower() for r in csv.DictReader(f)}
 for name in ("ETSY_KEYSTRING","ETSY_SHARED_SECRET","ETSY_REFRESH_TOKEN"):
  if not os.getenv(name):raise SystemExit(f"Missing secret {name}")
 import sys
 sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
 from etsy_api import refresh_access_token,get_owner_shop
 token_data=refresh_access_token()
 scopes=token_data.get("scope","")
 if "transactions_r" not in (scopes.split() if isinstance(scopes,str) else scopes):
  raise SystemExit("OAuth missing transactions_r scope; reauthorize Etsy before sales sync")
 token=token_data["access_token"]
 shop=get_owner_shop(token)
 key=os.environ["ETSY_KEYSTRING"]+":"+os.environ["ETSY_SHARED_SECRET"]
 data=collect(shop["shop_id"],key,token,mapping)
 Path(a.output).parent.mkdir(parents=True,exist_ok=True)
 Path(a.output).write_text(json.dumps({"source":"etsy_own_shop","metric":"gross transaction sales, fees excluded","data":data},indent=2)+"\n")
 print(f"Aggregated {len(data)} keyword/currency groups (no buyer information exported).")
if __name__=="__main__":main()
