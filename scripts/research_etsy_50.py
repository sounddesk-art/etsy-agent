#!/usr/bin/env python3
"""Live Etsy niche research -> maximum 50 review-ready product briefs.

Uses Etsy Open API findAllListingsActive. It never creates, publishes, renews,
or modifies a listing. Output is research only and must pass the separate
human-review gate before any Etsy upload.
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import math
import os
import re
import statistics
import time
from pathlib import Path

import requests

BASE="https://api.etsy.com/v3/application"
OUT_RESEARCH=Path("data/etsy_market_research.json")
OUT_CANDIDATES=Path("data/researched_listing_candidates.json")
NOW=int(dt.datetime.now(dt.timezone.utc).timestamp())

SEEDS=[
    ("highland cow wall art","cozy-animals","wall_art"),
    ("cozy cat wall art","cozy-animals","wall_art"),
    ("book lover wall art","cozy-animals","wall_art"),
    ("dog lover wall art","cozy-animals","wall_art"),
    ("bunny wall art","cozy-animals","wall_art"),
    ("fox wall art","cozy-animals","wall_art"),
    ("woodland animal wall art","cozy-animals","wall_art"),
    ("owl wall art","cozy-animals","wall_art"),
    ("alpine lake wall art","landscapes","wall_art"),
    ("mountain printable wall art","landscapes","wall_art"),
    ("coastal sunset wall art","landscapes","wall_art"),
    ("mediterranean wall art","landscapes","wall_art"),
    ("forest cabin wall art","landscapes","wall_art"),
    ("lavender field wall art","landscapes","wall_art"),
    ("fjord wall art","landscapes","wall_art"),
    ("waterfall wall art","landscapes","wall_art"),
    ("moon phase wall art","celestial","wall_art"),
    ("sun and moon wall art","celestial","wall_art"),
    ("celestial wall art","celestial","wall_art"),
    ("crescent moon botanical art","celestial","wall_art"),
    ("zodiac wall art","celestial","wall_art"),
    ("constellation wall art","celestial","wall_art"),
    ("eclipse wall art","celestial","wall_art"),
    ("wildflower wall art","botanical-sun","wall_art"),
    ("sunflower wall art","botanical-sun","wall_art"),
    ("eucalyptus wall art","botanical-sun","wall_art"),
    ("lemon kitchen wall art","botanical-sun","wall_art"),
    ("olive branch wall art","botanical-sun","wall_art"),
    ("daisy wall art","botanical-sun","wall_art"),
    ("boho sun wall art","botanical-sun","wall_art"),
]

STOP={
 "and","the","for","with","art","wall","print","printable","digital","download",
 "poster","decor","home","gift","instant","a","an","of","to","in","on","by",
}

def api_header():
    key=os.environ.get("ETSY_KEYSTRING","").strip()
    secret=os.environ.get("ETSY_SHARED_SECRET","").strip()
    if not key or not secret:
        raise RuntimeError("Missing ETSY_KEYSTRING/ETSY_SHARED_SECRET")
    return {"x-api-key":f"{key}:{secret}","User-Agent":"SounddeskEtsyResearch/1.0"}

def money_usd_like(listing):
    # Etsy search results can contain mixed currencies. Keep only numeric amount
    # as a descriptive signal and never use it for financial decisions.
    p=listing.get("price") or {}
    try:
        amount=float(p.get("amount"))/float(p.get("divisor") or 100)
        currency=p.get("currency_code")
        return amount,currency
    except (TypeError,ValueError,ZeroDivisionError):
        return None,None

def words(values):
    c=collections.Counter()
    for value in values:
        for w in re.findall(r"[a-z0-9]+",str(value).lower()):
            if len(w)>2 and w not in STOP:
                c[w]+=1
    return c

def query(session, keyword):
    r=session.get(
        f"{BASE}/listings/active",
        params={"keywords":keyword,"limit":100,"offset":0,"sort_on":"score","sort_order":"desc"},
        headers=api_header(),timeout=40,
    )
    r.raise_for_status()
    payload=r.json()
    return int(payload.get("count") or 0), payload.get("results") or []

def analyse(keyword, series, product, count, listings):
    favorers=[int(x.get("num_favorers") or 0) for x in listings]
    created=[int(x.get("created_timestamp") or x.get("creation_timestamp") or 0) for x in listings]
    recent=sum(1 for t in created if t and NOW-t <= 90*86400)
    all_tags=[]
    titles=[]
    price_by_currency=collections.defaultdict(list)
    for x in listings:
        titles.append(x.get("title") or "")
        all_tags.extend(x.get("tags") or [])
        price,currency=money_usd_like(x)
        if price is not None and currency:
            price_by_currency[currency].append(price)
    tag_counts=collections.Counter(" ".join(str(t).lower().split()) for t in all_tags if t)
    term_counts=words(titles+all_tags)
    medians={cur:round(statistics.median(vals),2) for cur,vals in price_by_currency.items() if vals}
    return {
        "keyword":keyword,"series":series,"product_type":product,
        "competition_count":count,
        "sample_size":len(listings),
        "sample_total_favorers":sum(favorers),
        "sample_median_favorers":statistics.median(favorers) if favorers else 0,
        "sample_top10_favorers":sum(sorted(favorers,reverse=True)[:10]),
        "recent_90d_in_top_sample":recent,
        "common_tags":[{"tag":k,"count":v} for k,v in tag_counts.most_common(20)],
        "common_terms":[{"term":k,"count":v} for k,v in term_counts.most_common(20)],
        "sample_median_price_by_currency":medians,
    }

def score_rows(rows):
    # Relative score within this research batch; no fake search-volume claim.
    max_eng=max([math.log1p(r["sample_top10_favorers"]) for r in rows] or [1])
    comps=[max(1,r["competition_count"]) for r in rows]
    lo,hi=min(math.log1p(x) for x in comps),max(math.log1p(x) for x in comps)
    for r in rows:
        eng=math.log1p(r["sample_top10_favorers"])/max_eng if max_eng else 0
        lc=math.log1p(max(1,r["competition_count"]))
        comp=1-(lc-lo)/(hi-lo) if hi>lo else .5
        freshness=min(1,r["recent_90d_in_top_sample"]/20)
        r["opportunity_score"]=round(100*(.45*eng+.40*comp+.15*freshness),1)
        r["score_basis"]="relative Etsy top-result engagement 45% + lower competition 40% + recent top-sample activity 15%"

def clean_tag(tag):
    tag=" ".join(re.sub(r"[^a-zA-Z0-9 '\-]"," ",tag).lower().split())
    if len(tag) <= 20:
        return tag
    words=tag.split()
    while words and len(" ".join(words)) > 20:
        words.pop()
    return " ".join(words)

def listing_description(row, variant):
    keyword=row["keyword"].title()
    angle="a focused series anchor" if variant==1 else "a complementary long-tail variation"
    series=row["series"].replace("-"," ")
    return f"""${keyword} — Original Digital Wall Art

A high-resolution printable artwork concept developed from current Etsy market research. This candidate is ${angle} within the ${series} collection.

WHAT THE FINAL LISTING WILL INCLUDE
• High-resolution digital artwork
• Print-ready download package
• Clear size/ratio information in the final approved product
• No physical item will be shipped

RESEARCH BASIS
This concept was selected using current Etsy active-listing competition, engagement among top search results, and recent listing activity. Research score: ${row['opportunity_score']} / 100.

CREATIVE PROCESS
This is a research-stage concept only. Before any Etsy upload, the final design must receive direct individual human creative input and review. If AI-assisted tools are used in the final artwork, the final Etsy description will disclose that use.

LICENSE
The final approved download will include personal-use terms and any applicable small-commercial-use terms stated in the final listing.

Digital product. No physical item will be shipped.
"""

def make_candidate(row, variant):
    base=row["keyword"]
    common=[x["tag"] for x in row["common_tags"]]
    chosen=[]
    for x in [base]+common:
        t=clean_tag(x)
        if t and t not in chosen:
            chosen.append(t)
        if len(chosen)>=13:
            break
    angle = "series anchor" if variant==1 else "long-tail companion"
    title = f"{base.title()} | Original {row['series'].replace('-',' ').title()} Digital Download"
    if variant==2:
        terms=[x["term"] for x in row["common_terms"] if x["term"] not in base.lower().split()]
        modifier=" ".join(terms[:2]).title() if terms else "Cozy"
        title=f"{modifier} {base.title()} | Original Digital Download"
    return {
        "id":re.sub(r"[^a-z0-9]+","-",base.lower()).strip("-")+f"-v{variant}",
        "source_keyword":base,
        "series":row["series"],
        "product_type":row["product_type"],
        "research_score":row["opportunity_score"],
        "concept_angle":angle,
        "title_draft":title[:140],
        "description_draft":listing_description(row,variant),
        "tags":chosen,
        "suggested_price":"4.90",
        "research_evidence":{
            "competition_count":row["competition_count"],
            "sample_top10_favorers":row["sample_top10_favorers"],
            "recent_90d_in_top_sample":row["recent_90d_in_top_sample"],
            "score_basis":row["score_basis"],
        },
        "status":"needs_human_review",
        "human_reviewed_at":None,
        "human_reviewed_by":None,
        "human_prompt_or_notes":None,
        "etsy_upload_allowed":False,
    }

def main():
    session=requests.Session()
    rows=[]
    for i,(keyword,series,product) in enumerate(SEEDS,1):
        count,listings=query(session,keyword)
        rows.append(analyse(keyword,series,product,count,listings))
        print(f"[{i}/{len(SEEDS)}] {keyword}: {count} active, sample {len(listings)}")
        time.sleep(.25)
    score_rows(rows)
    rows.sort(key=lambda x:x["opportunity_score"],reverse=True)
    concepts=[]
    for row in rows:
        concepts.append(make_candidate(row,1))
        concepts.append(make_candidate(row,2))
    concepts=sorted(concepts,key=lambda x:x["research_score"],reverse=True)[:50]
    OUT_RESEARCH.write_text(json.dumps({
        "generated_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "source":"Etsy Open API findAllListingsActive",
        "method_note":"No claimed search-volume data. Score uses only current Etsy competition and top-result engagement/freshness proxies.",
        "niches":rows,
    },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    OUT_CANDIDATES.write_text(json.dumps({
        "version":1,
        "generated_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "max_candidates":50,
        "human_review_required":True,
        "items":concepts,
    },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"researched_niches":len(rows),"candidates":len(concepts),
                      "top":[{"keyword":r["keyword"],"score":r["opportunity_score"]} for r in rows[:10]]},
                     ensure_ascii=False))

if __name__=="__main__":
    main()
