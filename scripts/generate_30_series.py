#!/usr/bin/env python3
from pathlib import Path
import json, math, random
import cairosvg

W,H=2000,3000
SVG=Path("output/source_svg"); PNG=Path("assets/generated")
SVG.mkdir(parents=True,exist_ok=True); PNG.mkdir(parents=True,exist_ok=True)

SPECS=[
("cozy-01","Sleepy Ginger Cat","cozy-animals","cat",["cozy cat art","sleepy cat print","warm wall decor","cat lover gift"]),
("cozy-02","Best Friends Dog and Cat","cozy-animals","dogcat",["dog cat art","best friends print","pet lover decor","cozy animal art"]),
("cozy-03","Daisy Meadow Bunny","cozy-animals","bunny",["bunny wall art","rabbit printable","daisy decor","cottagecore animal"]),
("cozy-04","Highland Cow in Wildflowers","cozy-animals","cow",["highland cow art","cow wall decor","wildflower print","farmhouse printable"]),
("cozy-05","Sleepy Fox in Autumn","cozy-animals","fox",["fox wall art","autumn printable","woodland decor","cozy fox print"]),
("cozy-06","Happy Hedgehog Garden","cozy-animals","hedgehog",["hedgehog art","garden printable","cute animal decor","woodland wall art"]),
("cozy-07","Little Owl and Flowers","cozy-animals","owl",["owl wall art","floral owl print","woodland nursery","cozy printable"]),
("cozy-08","Raccoon Evening Garden","cozy-animals","raccoon",["raccoon art","woodland print","cute animal wall art","garden decor"]),
("land-01","Alpine Lake Sunrise","landscapes","alpine",["mountain wall art","alpine lake print","sunrise printable","nature decor"]),
("land-02","Mediterranean Coast Sunset","landscapes","coast",["coastal wall art","mediterranean print","sunset decor","travel printable"]),
("land-03","Forest Cabin by the Lake","landscapes","cabin",["cabin wall art","forest printable","lake house decor","cozy landscape"]),
("land-04","Golden Dune Beach","landscapes","beach",["beach wall art","ocean printable","coastal decor","sunset beach print"]),
("land-05","Lavender Hills at Sunset","landscapes","lavender",["lavender wall art","provence printable","flower field art","sunset landscape"]),
("land-06","Nordic Fjord Morning","landscapes","fjord",["fjord wall art","nordic landscape","mountain lake print","scandinavian decor"]),
("land-07","Autumn Waterfall","landscapes","waterfall",["waterfall wall art","autumn landscape","forest print","nature printable"]),
("land-08","Tropical Cove Sunrise","landscapes","tropical",["tropical wall art","island printable","beach decor","ocean sunrise"]),
("cel-01","Golden Moon Phases","celestial","phases",["moon phase art","celestial print","lunar wall decor","boho moon"]),
("cel-02","Sun and Moon Harmony","celestial","sunmoon",["sun moon art","celestial decor","mystic printable","boho wall art"]),
("cel-03","Golden Zodiac Wheel","celestial","zodiac",["zodiac wall art","astrology print","celestial poster","star sign decor"]),
("cel-04","Botanical Crescent Moon","celestial","crescent",["crescent moon art","botanical moon","celestial floral","mystic wall decor"]),
("cel-05","Lunar Mountain Reflection","celestial","lunarland",["moon mountain art","night landscape","lunar wall art","celestial lake"]),
("cel-06","Constellation Garden","celestial","stars",["constellation art","star wall decor","celestial botanical","night sky print"]),
("cel-07","Golden Eclipse","celestial","eclipse",["eclipse art","sun moon print","celestial wall art","mystical decor"]),
("bot-01","Sunflower Golden Hour","botanical-sun","sunflower",["sunflower wall art","golden hour print","flower printable","warm botanical"]),
("bot-02","Wildflower Meadow","botanical-sun","wildflower",["wildflower wall art","meadow printable","cottagecore flowers","botanical decor"]),
("bot-03","Eucalyptus Sun","botanical-sun","eucalyptus",["eucalyptus print","boho sun art","botanical wall decor","sage green art"]),
("bot-04","Lemon Grove","botanical-sun","lemon",["lemon wall art","citrus printable","kitchen botanical","mediterranean decor"]),
("bot-05","Olive Branch Sun","botanical-sun","olive",["olive branch art","mediterranean print","boho botanical","sun wall decor"]),
("bot-06","Daisy Bouquet","botanical-sun","daisy",["daisy wall art","flower bouquet print","cottagecore decor","botanical printable"]),
("bot-07","Boho Sun Garden","botanical-sun","sun",["boho sun art","sun wall decor","botanical sun","warm neutral print"]),
]

def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def defs(bg1,bg2,accent):
    return f'''<defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/></linearGradient>
    <radialGradient id="sun"><stop offset="0" stop-color="#fff7d2"/><stop offset=".55" stop-color="{accent}"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
    <filter id="shadow"><feDropShadow dx="0" dy="18" stdDeviation="22" flood-opacity=".18"/></filter>
    <filter id="soft"><feGaussianBlur stdDeviation="18"/></filter>
    </defs>'''

def grain():
    dots=[]
    rnd=random.Random(7)
    for _ in range(180):
        x=rnd.randrange(W); y=rnd.randrange(H); r=rnd.choice([2,3,4,5]); o=rnd.uniform(.025,.08)
        dots.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#5a402d" opacity="{o:.3f}"/>')
    return "".join(dots)

def flower(x,y,s,petal="#f3e8cf",center="#d79b43"):
    petals=[]
    for a in range(0,360,45):
        rad=math.radians(a); px=x+math.cos(rad)*s*.55; py=y+math.sin(rad)*s*.55
        petals.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{s*.22:.1f}" ry="{s*.5:.1f}" fill="{petal}" transform="rotate({a+90} {px:.1f} {py:.1f})"/>')
    return "".join(petals)+f'<circle cx="{x}" cy="{y}" r="{s*.28}" fill="{center}"/>'

def leaves(seed=1,base="#5f7d64"):
    rnd=random.Random(seed); out=[]
    for i in range(34):
        x=rnd.randint(40,W-40); y=rnd.randint(int(H*.35),H-70); s=rnd.randint(18,55)
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="{s}" ry="{s*2}" fill="{base}" opacity="{rnd.uniform(.35,.78):.2f}" transform="rotate({rnd.randint(-70,70)} {x} {y})"/>')
    return "".join(out)

def svg_wrap(body,bg1="#fff6e8",bg2="#e7c6a7",accent="#f1a34d"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{defs(bg1,bg2,accent)}<rect width="100%" height="100%" fill="url(#bg)"/>{body}{grain()}</svg>'

def animal(kind,seed):
    rnd=random.Random(seed)
    palettes={"cat":("#d78a45","#7a4b2a"),"dogcat":("#d99a54","#7f5537"),"bunny":("#d9c7b2","#9b826e"),"cow":("#a86436","#5b3a2a"),"fox":("#cf6d32","#7c3d27"),"hedgehog":("#9d7048","#5d4938"),"owl":("#c9a56f","#6d5943"),"raccoon":("#8e8b82","#3e4549")}
    fur,dark=palettes[kind]
    body=f'<circle cx="1000" cy="1780" r="610" fill="{fur}" filter="url(#shadow)"/>'
    # ears
    body+=f'<path d="M530 1450 L650 680 L900 1300 Z" fill="{fur}"/><path d="M1470 1450 L1350 680 L1100 1300 Z" fill="{fur}"/>'
    # muzzle and eyes
    body+=f'<ellipse cx="1000" cy="1920" rx="370" ry="300" fill="#f3d9bc"/><ellipse cx="760" cy="1640" rx="90" ry="115" fill="{dark}"/><ellipse cx="1240" cy="1640" rx="90" ry="115" fill="{dark}"/><circle cx="1000" cy="1870" r="76" fill="#4b342c"/>'
    body+=f'<path d="M900 2030 Q1000 2140 1100 2030" fill="none" stroke="#5a3a32" stroke-width="28" stroke-linecap="round"/>'
    if kind=="cow":
        body+=f'<path d="M610 1330 Q330 1010 500 760" fill="none" stroke="#ede2cc" stroke-width="85" stroke-linecap="round"/><path d="M1390 1330 Q1670 1010 1500 760" fill="none" stroke="#ede2cc" stroke-width="85" stroke-linecap="round"/>'
    if kind in ("raccoon","owl"):
        body+=f'<path d="M580 1580 Q1000 1320 1420 1580 Q1000 1800 580 1580" fill="{dark}" opacity=".55"/>'
    if kind=="hedgehog":
        for a in range(200,341,10):
            rad=math.radians(a); x=1000+math.cos(rad)*720; y=1770+math.sin(rad)*720
            body+=f'<path d="M{x:.0f} {y:.0f} l {math.cos(rad)*150:.0f} {math.sin(rad)*150:.0f}" stroke="{dark}" stroke-width="35" stroke-linecap="round"/>'
    # cozy foreground blanket + flowers
    body+=f'<path d="M0 2350 Q480 2180 900 2380 T2000 2320 L2000 3000 L0 3000 Z" fill="#d9b89a" opacity=".9"/>'
    for i in range(13):
        x=rnd.randint(100,1900); y=rnd.randint(2150,2800); s=rnd.randint(30,70)
        body+=flower(x,y,s, rnd.choice(["#f8f0dc","#f2d6c8","#f7e2a7"]), "#d59736")
    body+=f'<circle cx="1550" cy="650" r="280" fill="url(#sun)" opacity=".8"/>'
    return svg_wrap(body,"#fff0d9","#e8b98d","#f4a04a")

def landscape(kind,seed):
    rnd=random.Random(seed)
    sky1,sky2=("#8ec5e8","#ffd6a0") if kind not in ("fjord","waterfall") else ("#91b6c8","#d7d4c5")
    body=f'<circle cx="1500" cy="780" r="360" fill="url(#sun)"/>'
    # distant mountains
    body+=f'<path d="M0 1700 L330 1260 L610 1510 L930 960 L1280 1460 L1580 1080 L2000 1610 L2000 3000 L0 3000 Z" fill="#637b78"/>'
    body+=f'<path d="M0 1880 L420 1500 L780 1700 L1120 1280 L1490 1640 L1810 1390 L2000 1580 L2000 3000 L0 3000 Z" fill="#314f50" opacity=".93"/>'
    if kind in ("alpine","cabin","fjord","waterfall"):
        body+=f'<path d="M0 2050 Q500 1880 1000 2030 T2000 1980 L2000 3000 L0 3000 Z" fill="#3d8694"/>'
        body+=f'<path d="M0 2290 Q520 2120 1020 2260 T2000 2180 L2000 3000 L0 3000 Z" fill="#7fc0c0" opacity=".6"/>'
    else:
        body+=f'<path d="M0 2100 Q500 1970 1000 2090 T2000 2020 L2000 3000 L0 3000 Z" fill="#4ca1b5"/>'
        for y in range(2170,2700,110):
            body+=f'<path d="M0 {y} Q400 {y-70} 800 {y} T1600 {y} T2200 {y}" fill="none" stroke="#e9fbff" stroke-width="18" opacity=".65"/>'
    # vegetation/flowers
    for i in range(26):
        x=rnd.randint(50,1950); y=rnd.randint(2260,2940); s=rnd.randint(16,42)
        body+=flower(x,y,s,rnd.choice(["#f4e9d5","#e8a0a7","#f4cf6b","#bf84bc"]),"#d49339")
    if kind=="cabin":
        body+=f'<rect x="760" y="1770" width="520" height="360" rx="8" fill="#6e412d"/><path d="M690 1790 L1020 1510 L1350 1790 Z" fill="#3e2f29"/><rect x="900" y="1900" width="110" height="130" fill="#ffd487"/><rect x="1090" y="1900" width="110" height="130" fill="#ffd487"/>'
    if kind=="lavender":
        for x in range(80,2000,90):
            body+=f'<path d="M{x} 3000 L{x+60} 2240" stroke="#6b765b" stroke-width="12"/><circle cx="{x+60}" cy="2240" r="28" fill="#8f70b6"/>'
    return svg_wrap(body,sky1,sky2,"#ffbd65")

def celestial(kind,seed):
    rnd=random.Random(seed); body=""
    for i in range(100):
        x=rnd.randint(40,1960); y=rnd.randint(40,2920); r=rnd.choice([2,3,5,8])
        body+=f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f4cb73" opacity="{rnd.uniform(.5,1):.2f}"/>'
    if kind=="phases":
        for i,x in enumerate([340,610,880,1150,1420,1690]):
            rr=120+(20 if i in (2,3) else 0); body+=f'<circle cx="{x}" cy="1050" r="{rr}" fill="#e8b95f"/>'
            if i<3: body+=f'<circle cx="{x+55}" cy="1020" r="{rr}" fill="#0b1c2c"/>'
            elif i>3: body+=f'<circle cx="{x-55}" cy="1020" r="{rr}" fill="#0b1c2c"/>'
    elif kind=="zodiac":
        body+=f'<circle cx="1000" cy="1380" r="650" fill="none" stroke="#d9a84f" stroke-width="18"/><circle cx="1000" cy="1380" r="470" fill="none" stroke="#d9a84f" stroke-width="8"/>'
        for a in range(0,360,30):
            rad=math.radians(a); x=1000+math.cos(rad)*560; y=1380+math.sin(rad)*560
            body+=f'<circle cx="{x:.0f}" cy="{y:.0f}" r="34" fill="#d9a84f"/><line x1="1000" y1="1380" x2="{x:.0f}" y2="{y:.0f}" stroke="#d9a84f" stroke-width="5" opacity=".5"/>'
        body+=f'<circle cx="1000" cy="1380" r="190" fill="#d9a84f"/>'
    elif kind in ("sunmoon","eclipse"):
        body+=f'<circle cx="830" cy="1220" r="430" fill="#dca94f"/><circle cx="1140" cy="1160" r="430" fill="#0b1c2c"/><circle cx="1140" cy="1160" r="425" fill="none" stroke="#f2cc76" stroke-width="16"/>'
        for a in range(0,360,15):
            rad=math.radians(a); x1=830+math.cos(rad)*480; y1=1220+math.sin(rad)*480; x2=830+math.cos(rad)*620; y2=1220+math.sin(rad)*620
            body+=f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#dca94f" stroke-width="16"/>'
    elif kind=="crescent":
        body+=f'<circle cx="1000" cy="1250" r="620" fill="#e6bd6e"/><circle cx="1260" cy="1070" r="620" fill="#0b1c2c"/>'
    elif kind=="lunarland":
        body+=f'<circle cx="1000" cy="760" r="390" fill="#e6bd6e"/><path d="M0 2050 L400 1600 L690 1850 L1030 1350 L1420 1860 L1750 1500 L2000 1850 L2000 3000 L0 3000 Z" fill="#162e40"/><path d="M0 2250 Q500 2130 1000 2230 T2000 2180 L2000 3000 L0 3000 Z" fill="#173f58"/>'
    elif kind=="stars":
        for a in range(0,360,30):
            rad=math.radians(a); x=1000+math.cos(rad)*620; y=1400+math.sin(rad)*620
            body+=f'<line x1="1000" y1="1400" x2="{x:.0f}" y2="{y:.0f}" stroke="#d9a84f" stroke-width="5" opacity=".5"/><circle cx="{x:.0f}" cy="{y:.0f}" r="18" fill="#f3cf80"/>'
    # botanical gold framing
    for i in range(18):
        x=120+(i%2)*1600+rnd.randint(-40,40); y=650+i*110
        body+=f'<ellipse cx="{x}" cy="{y}" rx="38" ry="90" fill="#d7a64f" opacity=".8" transform="rotate({-35 if x<1000 else 35} {x} {y})"/>'
    return svg_wrap(body,"#071421","#0c2638","#e5b760")

def botanical(kind,seed):
    rnd=random.Random(seed)
    body=f'<circle cx="1000" cy="900" r="420" fill="none" stroke="#d39b3a" stroke-width="22"/>'
    for a in range(0,360,15):
        rad=math.radians(a); x1=1000+math.cos(rad)*470; y1=900+math.sin(rad)*470; x2=1000+math.cos(rad)*650; y2=900+math.sin(rad)*650
        body+=f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#d39b3a" stroke-width="16" stroke-linecap="round"/>'
    if kind=="lemon":
        for i in range(10):
            x=rnd.randint(250,1750); y=rnd.randint(1450,2700); body+=f'<ellipse cx="{x}" cy="{y}" rx="105" ry="145" fill="#e9bd39" transform="rotate({rnd.randint(-35,35)} {x} {y})"/>'
    elif kind=="olive":
        for i in range(24):
            x=rnd.randint(220,1780); y=rnd.randint(1450,2750); body+=f'<ellipse cx="{x}" cy="{y}" rx="38" ry="72" fill="#4d513c"/><circle cx="{x+50}" cy="{y+45}" r="32" fill="#383a2e"/>'
    elif kind in ("sunflower","wildflower","daisy"):
        for i in range(24):
            x=rnd.randint(100,1900); y=rnd.randint(1500,2900); s=rnd.randint(35,85)
            pet="#e1a331" if kind=="sunflower" else rnd.choice(["#f4eee1","#e9b3b8","#d9a2c6","#f0bf5b"])
            body+=flower(x,y,s,pet,"#8c612f")
    else:
        body+=leaves(seed,"#55765c")
        for i in range(12):
            x=rnd.randint(120,1880); y=rnd.randint(1550,2850); s=rnd.randint(35,70); body+=flower(x,y,s,"#f3ead7","#c28a36")
    return svg_wrap(body,"#fffaf0","#ead9bd","#f0b35d")

def make(spec,idx):
    id_,name,series,kind,tags=spec
    if series=="cozy-animals": svg=animal(kind,idx)
    elif series=="landscapes": svg=landscape(kind,idx)
    elif series=="celestial": svg=celestial(kind,idx)
    else: svg=botanical(kind,idx)
    sp=SVG/f"{id_}.svg"; pp=PNG/f"{id_}.png"
    sp.write_text(svg,encoding="utf-8")
    cairosvg.svg2png(bytestring=svg.encode(),write_to=str(pp),output_width=3000,output_height=4500)
    products=["wall_art","greeting_card","postcard"]
    if series in ("celestial","botanical-sun"): products.append("bookmark")
    return {"id":id_,"display_name":name,"series":series,"file":pp.name,"products":products,"tags":tags,"status":"approved"}

items=[make(s,i+1) for i,s in enumerate(SPECS)]
Path("data/generated_manifest.json").write_text(json.dumps({"version":2,"items":items},indent=2),encoding="utf-8")
print(f"Generated {len(items)} source artworks; planned {sum(len(x['products']) for x in items)} Etsy drafts.")
