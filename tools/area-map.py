import json, math, sys
G=sys.argv[2]  # county GeoJSON from public US Census boundaries, e.g. plotly/datasets geojson-counties-fips.json
OUT=sys.argv[1]  # usage: python3 tools/area-map.py map.svg counties.json, then paste the SVG into src/page.html
d=json.load(open(G))
MSA={'48015':'Austin','48039':'Brazoria','48071':'Chambers','48157':'Fort Bend','48167':'Galveston','48201':'Harris','48291':'Liberty','48339':'Montgomery','48473':'Waller'}
feats={f['id']:f for f in d['features'] if f['id'].startswith('48')}
LON0,LON1,LAT0,LAT1=-96.70,-94.30,28.80,30.70
K=math.cos(math.radians(29.75))
W=720; S=W/((LON1-LON0)*K); H=round((LAT1-LAT0)*S)
def P(lon,lat): return ((lon-LON0)*K*S,(LAT1-lat)*S)
def rings(f):
    g=f['geometry']; polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
    for poly in polys:
        for ring in poly: yield ring
def path(f):
    out=[]
    for ring in rings(f):
        pts=[];last=None
        for lon,lat in ring:
            x,y=P(lon,lat);q=(round(x,1),round(y,1))
            if last and abs(q[0]-last[0])<1.2 and abs(q[1]-last[1])<1.2: continue
            pts.append(q);last=q
        if len(pts)<3: continue
        out.append('M'+' '.join('%g %g'%p for p in pts)+'z')
    return ''.join(out)
def inview(f):
    for ring in rings(f):
        for lon,lat in ring:
            if LON0-.5<lon<LON1+.5 and LAT0-.5<lat<LAT1+.5: return True
    return False
ctx=[f for k,f in feats.items() if k not in MSA and inview(f)]
msa=[feats[k] for k in MSA]
towns=[("Houston",29.760,-95.370,"c",1),("Conroe",30.312,-95.456,"r",0),("The Woodlands",30.166,-95.461,"r",0),("Spring",30.065,-95.417,"r",0),
("Tomball",30.097,-95.616,"l",0),("Katy",29.786,-95.824,"l",0),("Cypress",29.969,-95.697,"l",0),
("Sugar Land",29.620,-95.635,"r",0),("Richmond",29.582,-95.761,"l",0),("Pearland",29.564,-95.286,"r",0),("Pasadena",29.691,-95.209,"l",0),
("Baytown",29.736,-94.977,"r",0),("League City",29.507,-95.095,"r",0),("Texas City",29.384,-94.903,"l",0),("Galveston",29.301,-94.798,"r",0),
("Angleton",29.169,-95.432,"l",0),("Hempstead",30.097,-96.078,"l",0),("Bellville",29.950,-96.257,"l",0),("Liberty",30.058,-94.795,"r",0),("Lake Jackson",29.034,-95.434,"l",0),("Magnolia",30.209,-95.750,"l",0),("Cleveland",30.341,-95.086,"r",0)]
MINOR=['Magnolia', 'Hempstead', 'Bellville', 'Cleveland', 'Liberty', 'Kingwood', 'Richmond', 'Texas City', 'Angleton', 'Lake Jackson', 'Tomball', 'Spring', 'Pasadena']
o=[]
o.append(f'<svg class="area-map" viewBox="0 0 {W} {H}" role="img" aria-labelledby="mapTitle"><title id="mapTitle">Map of the Greater Houston area we buy in: Harris, Fort Bend, Montgomery, Brazoria, Galveston, Liberty, Waller, Chambers and Austin counties</title>')
o.append(f'<rect width="{W}" height="{H}" fill="#D9E8F5"/>')
o.append('<g fill="#F4F6F9" stroke="#DCE3EC" stroke-width="1">'+''.join(f'<path d="{path(f)}"/>' for f in ctx)+'</g>')
o.append('<g fill="none" stroke="#BF4A08" stroke-width="7" stroke-linejoin="round">'+''.join(f'<path d="{path(f)}"/>' for f in msa)+'</g>')
o.append('<g fill="#FFFFFF" stroke="#C9D5E6" stroke-width="1.2" stroke-linejoin="round">'+''.join(f'<path d="{path(f)}"/>' for f in msa)+'</g>')
o.append('<g fill="#E9EFF8">'+f'<path d="{path(feats["48201"])}"/>'+'</g>')
o.append('<g class="towns">')
for name,lat,lon,side,big in towns:
    x,y=P(lon,lat)
    if big:
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="#152F70" opacity=".15"/><circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="#152F70" stroke="#fff" stroke-width="2.5"/>')
        o.append(f'<text x="{x+14:.1f}" y="{y-12:.1f}" class="big">Houston</text>')
    else:
        cls=' class="minor"' if name in MINOR else ''
        o.append(f'<g{cls}><circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#BF4A08" stroke="#fff" stroke-width="2"/>')
        tx=x+10 if side=="r" else x-10; anchor="start" if side=="r" else "end"
        o.append(f'<text x="{tx:.1f}" y="{y+5.5:.1f}" text-anchor="{anchor}">{name}</text></g>')
o.append('</g></svg>')
svg=''.join(o)
open(OUT,'w').write(svg)
print(W,H,len(svg))
