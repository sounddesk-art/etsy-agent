#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json, math, zipfile, textwrap

OUT=Path("output/collection")
OUT.mkdir(parents=True,exist_ok=True)
W,H=3000,5000

def font(size,bold=False):
    paths=[
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        try:return ImageFont.truetype(p,size)
        except:pass
    return ImageFont.load_default()

def center_text(d, text, y, size, fill, bold=False, maxw=2500):
    f=font(size,bold)
    lines=[]
    for raw in text.split("\n"):
        words=raw.split()
        line=""
        for w in words:
            cand=(line+" "+w).strip()
            if d.textbbox((0,0),cand,font=f)[2] <= maxw:
                line=cand
            else:
                if line: lines.append(line)
                line=w
        if line: lines.append(line)
    cy=y
    for line in lines:
        box=d.textbbox((0,0),line,font=f)
        x=(W-(box[2]-box[0]))//2
        d.text((x,cy),line,font=f,fill=fill)
        cy+=int(size*1.18)
    return cy

def gradient(top,bottom):
    img=Image.new("RGB",(W,H))
    px=img.load()
    for y in range(H):
        t=y/(H-1)
        c=tuple(int(top[i]*(1-t)+bottom[i]*t) for i in range(3))
        for x in range(W): px[x,y]=c
    return img

def heart(d,x,y,s,fill):
    d.ellipse((x-s,y-s,x,y),fill=fill); d.ellipse((x,y-s,x+s,y),fill=fill)
    d.polygon([(x-s,y-s//2),(x+s,y-s//2),(x,y+s)],fill=fill)

def rgb(v, default=(35,28,24)):
    if v is None: v=default
    while isinstance(v,(list,tuple)) and len(v)==1 and isinstance(v[0],(list,tuple)):
        v=v[0]
    if not isinstance(v,(list,tuple)) or len(v) < 3:
        v=default
    return tuple(int(x) for x in v[:3])

def poster(spec):
    bg=spec["bg"]
    bg=(rgb(bg[0],(245,240,230)), rgb(bg[1],(220,210,195)))
    img=gradient(bg[0],bg[1])
    d=ImageDraw.Draw(img)
    fg=rgb(spec.get("fg"),(35,28,24))
    accent=rgb(spec.get("accent"),(180,100,70))
    y=350
    y=center_text(d,spec["headline"],y,220,fg,True)
    y+=70
    center_text(d,spec.get("subline",""),y,105,fg,False)

    kind=spec["kind"]
    if kind=="cow":
        cx,cy=1500,3100
        d.ellipse((800,2200,2200,3900),fill=(180,130,80),outline=fg,width=24)
        d.polygon([(900,2450),(350,2100),(720,2750)],fill=(120,90,60),outline=fg)
        d.polygon([(2100,2450),(2650,2100),(2280,2750)],fill=(120,90,60),outline=fg)
        d.ellipse((1120,2750,1880,3500),fill=(220,175,125),outline=fg,width=18)
        d.ellipse((1100,2600,1250,2750),fill=fg); d.ellipse((1750,2600,1900,2750),fill=fg)
        d.ellipse((1350,3300,1450,3400),fill=fg); d.ellipse((1550,3300,1650,3400),fill=fg)
        d.rounded_rectangle((1100,3650,1900,4350),radius=80,fill=(245,235,215),outline=fg,width=22)
        heart(d,1500,4000,110,accent)
    elif kind=="beach":
        d.rectangle((0,3000,W,H),fill=(232,196,142))
        d.rectangle((0,2450,W,3050),fill=(77,170,205))
        d.ellipse((1250,1900,1750,2400),fill=(244,178,90))
        heart(d,1500,3550,240,accent)
    elif kind=="cat_books":
        for i in range(5):
            d.rounded_rectangle((650,3300-i*260,2350,3500-i*260),radius=40,fill=(110+i*18,70+i*10,48),outline=fg,width=12)
        d.ellipse((1050,1800,1950,3000),fill=(130,110,95),outline=fg,width=20)
        d.polygon([(1100,1950),(1220,1500),(1380,2050)],fill=(130,110,95),outline=fg)
        d.polygon([(1900,1950),(1780,1500),(1620,2050)],fill=(130,110,95),outline=fg)
        d.arc((1260,2300,1740,2750),0,180,fill=fg,width=20)
    elif kind=="mountain":
        d.polygon([(200,3900),(1000,2200),(1600,3900)],fill=(95,115,120))
        d.polygon([(900,3900),(1850,1900),(2800,3900)],fill=(70,90,100))
        d.polygon([(1500,2700),(1850,1900),(2200,2700)],fill=(245,245,240))
        d.ellipse((400,3700,2600,4700),fill=(75,150,165))
    elif kind=="dog":
        d.ellipse((850,2050,2150,3900),fill=(205,145,75),outline=fg,width=22)
        d.ellipse((1150,2500,1350,2700),fill=fg); d.ellipse((1650,2500,1850,2700),fill=fg)
        d.ellipse((1350,2900,1650,3150),fill=(70,55,45))
        d.arc((1200,3050,1800,3550),0,180,fill=fg,width=28)
        d.ellipse((1350,3250,1650,3700),fill=(210,95,100))
    elif kind=="flowers":
        for i in range(24):
            x=250+(i*113)%2500; y=2300+(i*197)%2100
            stem=(70,120,75)
            d.line((x,H-300,x,y),fill=stem,width=10)
            petals=[(x+math.cos(a)*80,y+math.sin(a)*80) for a in [0,1.047,2.094,3.141,4.188,5.235]]
            for px,py in petals:d.ellipse((px-45,py-45,px+45,py+45),fill=(245,220-(i%3)*25,110+(i%4)*30))
            d.ellipse((x-35,y-35,x+35,y+35),fill=(120,80,45))
    elif kind=="turtle":
        d.ellipse((800,2450,2200,3650),fill=(85,155,125),outline=fg,width=20)
        d.ellipse((1250,2700,1750,3300),fill=(145,195,150),outline=fg,width=14)
        d.ellipse((2150,2800,2600,3200),fill=(85,155,125))
        d.ellipse((450,2600,900,3000),fill=(85,155,125))
        for x,y in [(400,3900),(800,4200),(2300,4000),(2600,4400)]:
            d.ellipse((x,y,x+80,y+80),outline=(220,245,250),width=14)
    elif kind=="cool_cat":
        d.ellipse((900,2100,2100,3800),fill=(190,120,65),outline=fg,width=20)
        d.polygon([(980,2250),(1150,1700),(1350,2300)],fill=(190,120,65),outline=fg)
        d.polygon([(2020,2250),(1850,1700),(1650,2300)],fill=(190,120,65),outline=fg)
        d.rounded_rectangle((1050,2500,1450,2750),radius=60,fill=(30,30,30))
        d.rounded_rectangle((1550,2500,1950,2750),radius=60,fill=(30,30,30))
        d.line((1450,2600,1550,2600),fill=fg,width=25)
    elif kind=="moons":
        cx=1500
        for i in range(7):
            y=1800+i*430
            r=150
            d.ellipse((cx-r,y-r,cx+r,y+r),fill=(230,190,105),outline=(250,225,160),width=8)
            if i<3:
                d.ellipse((cx-r+55+i*22,y-r,cx+r+55+i*22,y+r),fill=bg[0])
            elif i>3:
                d.ellipse((cx-r-55-(i-4)*22,y-r,cx+r-55-(i-4)*22,y+r),fill=bg[0])
        for x,y in [(500,2000),(2450,2350),(600,3900),(2350,4200)]:
            d.line((x-35,y,x+35,y),fill=(245,215,140),width=9); d.line((x,y-35,x,y+35),fill=(245,215,140),width=9)
    elif kind=="sun":
        cx,cy=1500,2950; r=620
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(180,125,60),width=30)
        d.ellipse((cx-340,cy-340,cx+340,cy+340),outline=(180,125,60),width=18)
        for a in range(0,360,15):
            x1=cx+math.cos(math.radians(a))*720; y1=cy+math.sin(math.radians(a))*720
            x2=cx+math.cos(math.radians(a))*1100; y2=cy+math.sin(math.radians(a))*1100
            d.line((x1,y1,x2,y2),fill=(180,125,60),width=18)
        for x,y in [(450,3850),(2400,4100),(550,4350),(2250,4550)]:
            d.ellipse((x,y,x+120,y+220),outline=(85,125,85),width=12)

    # subtle border
    d.rounded_rectangle((80,80,W-80,H-80),radius=35,outline=(255,255,255),width=18)
    return img

specs=[
{"slug":"coffee-first-highland-cow","headline":"COFFEE\nFIRST","subline":"cozy mornings & good moods","kind":"cow","bg":[(246,226,197),(224,190,150)],"accent":[176,85,60]},
{"slug":"good-vibes-only-beach","headline":"GOOD VIBES\nONLY","subline":"sunset state of mind","kind":"beach","bg":[(245,196,190),(147,199,222)],"accent":[205,105,95]},
{"slug":"just-one-more-chapter-cat","headline":"JUST ONE MORE\nCHAPTER","subline":"for book lovers & sleepy cats","kind":"cat_books","bg":[(97,67,53),(210,163,112)],"fg":[(250,238,220)],"accent":[230,190,120]},
{"slug":"adventure-awaits-mountain","headline":"ADVENTURE\nAWAITS","subline":"find your next horizon","kind":"mountain","bg":[(247,194,184),(141,190,210)],"accent":[185,90,78]},
{"slug":"life-better-with-dog","headline":"LIFE IS BETTER\nWITH A DOG","subline":"home is where the paws are","kind":"dog","bg":[(247,239,225),(223,198,160)],"accent":[190,90,70]},
{"slug":"stay-kind-wildflowers","headline":"STAY KIND","subline":"grow gently","kind":"flowers","bg":[(246,241,224),(226,236,215)],"accent":[190,125,80]},
{"slug":"slow-down-sea-turtle","headline":"SLOW DOWN","subline":"breathe • float • be here","kind":"turtle","bg":[(115,198,221),(25,110,155)],"fg":[(250,250,245)],"accent":[235,220,150]},
{"slug":"good-things-take-time-cat","headline":"GOOD THINGS\nTAKE TIME","subline":"stay cool & keep going","kind":"cool_cat","bg":[(238,223,188),(190,215,178)],"accent":[175,80,65]},
{"slug":"trust-the-process-moon","headline":"TRUST THE\nPROCESS","subline":"phases change • keep going","kind":"moons","bg":[(17,25,42),(32,38,54)],"fg":[(244,220,160)],"accent":[230,190,100]},
{"slug":"radiate-good-energy-sun","headline":"RADIATE\nGOOD ENERGY","subline":"warmth in • warmth out","kind":"sun","bg":[(247,240,218),(235,223,192)],"accent":[(180,125,60)]}
]

listing_data=[
{
"title":"Highland Cow Coffee Printable Wall Art | Coffee First Funny Kitchen Decor | Digital Download",
"price":"4.90",
"tags":["highland cow art","coffee wall art","cow kitchen decor","funny coffee print","rustic wall decor","printable wall art","farmhouse printable","cozy kitchen art","digital download","highland cow print","coffee lover gift","cottagecore decor","instant download"]
},
{
"title":"Good Vibes Only Beach Printable | Sunset Coastal Wall Art | Positive Quote Digital Download",
"price":"4.90",
"tags":["good vibes print","beach wall art","sunset printable","coastal wall decor","positive quote art","summer wall art","ocean printable","printable wall art","digital download","boho beach decor","feel good poster","instant download","beach lover gift"]
},
{
"title":"Just One More Chapter Cat Printable | Book Lover Wall Art | Cozy Reading Digital Download",
"price":"4.90",
"tags":["book lover print","cat wall art","reading printable","bookish wall decor","cozy reading art","library wall art","cat lover gift","printable wall art","digital download","book nook decor","reader gift","instant download","cozy cat print"]
},
{
"title":"Adventure Awaits Mountain Printable | Alpine Lake Wall Art | Travel Quote Digital Download",
"price":"4.90",
"tags":["mountain wall art","adventure print","alpine printable","lake wall decor","travel quote art","nature wall art","hiking decor","printable wall art","digital download","mountain poster","outdoor lover gift","instant download","cabin wall decor"]
},
{
"title":"Life Is Better With a Dog Printable | Dog Lover Wall Art | Happy Dog Digital Download",
"price":"4.90",
"tags":["dog lover print","dog wall art","pet lover decor","happy dog print","dog quote art","pet wall decor","printable wall art","digital download","dog owner gift","golden dog art","instant download","cute dog poster","home with dogs"]
},
{
"title":"Stay Kind Wildflower Printable | Botanical Wall Art | Positive Quote Digital Download",
"price":"4.90",
"tags":["stay kind print","wildflower art","botanical print","flower wall art","positive quote","cottagecore art","printable wall art","digital download","floral wall decor","kindness poster","instant download","boho flower print","garden lover gift"]
},
{
"title":"Slow Down Sea Turtle Printable | Ocean Wall Art | Mindful Quote Digital Download",
"price":"4.90",
"tags":["sea turtle art","ocean wall art","slow down print","coastal printable","mindful wall art","turtle lover gift","printable wall art","digital download","ocean decor","beach house print","instant download","calm wall decor","marine life art"]
},
{
"title":"Good Things Take Time Cat Printable | Funny Cat Wall Art | Positive Digital Download",
"price":"4.90",
"tags":["cat wall art","cat quote print","funny cat decor","positive wall art","cool cat print","cat lover gift","printable wall art","digital download","motivational cat","instant download","cute cat poster","cozy wall decor","cat sunglasses"]
},
{
"title":"Trust The Process Moon Phase Printable | Celestial Wall Art | Boho Digital Download",
"price":"4.90",
"tags":["moon phase art","celestial print","trust the process","boho wall art","moon wall decor","spiritual decor","printable wall art","digital download","lunar wall art","celestial poster","instant download","mystic wall decor","moon lover gift"]
},
{
"title":"Radiate Good Energy Sun Printable | Boho Sun Wall Art | Positive Quote Digital Download",
"price":"4.90",
"tags":["sun wall art","good energy print","boho sun print","positive wall art","celestial decor","sunshine poster","printable wall art","digital download","boho wall decor","radiate positivity","instant download","sun lover gift","warm neutral art"]
}
]

manifest=[]
for spec,meta in zip(specs,listing_data):
    slug=spec["slug"]
    img=poster(spec)
    png=OUT/f"{slug}.png"
    preview=OUT/f"{slug}-preview.jpg"
    zpath=OUT/f"{slug}-download.zip"
    img.save(png,optimize=True)
    prev=img.copy(); prev.thumbnail((1800,3000)); prev.save(preview,quality=92,optimize=True)
    with zipfile.ZipFile(zpath,"w",zipfile.ZIP_DEFLATED) as z:
        z.write(png,arcname=f"{slug}-3000x5000.png")
    desc=(
        f"{meta['title'].split('|')[0].strip()}\n\n"
        "Instant digital download printable wall art. No physical item will be shipped.\n\n"
        "YOU RECEIVE\n• 1 high-resolution PNG file, 3000 × 5000 px\n• Delivered in a ZIP file\n\n"
        "Perfect for home, office, reading nook, gift printing or personal decor. "
        "Colors may vary slightly between screens and printers.\n\n"
        "AI DISCLOSURE\nThis design was created with AI-assisted creative tools and then curated, composed and prepared for sale by NiceDesignStudios.\n\n"
        "PERSONAL USE\nFor personal use only. Please do not resell or redistribute the digital file."
    )
    manifest.append({
        "slug":slug,"title":meta["title"],"description":desc,"price":meta["price"],
        "quantity":999,"taxonomy_query":"Digital Prints","who_made":"i_did","when_made":"2020_2026",
        "is_supply":False,"tags":meta["tags"],"image":str(preview),"file":str(zpath),
        "alt_text":meta["title"].split("|")[0].strip()
    })

Path("output/listing_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
print(f"Generated {len(manifest)} listing packages.")
