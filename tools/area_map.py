# One-hour drive area from UH. Usage: python3 tools/area_map.py <hou_roads.json> <counties.json> <out.svg>
# Roads: Natural Earth ne_10m_roads (public domain), clipped to the Houston area. Counties: US Census boundaries.
# Speeds were calibrated against typical non-rush drive times; the result is an approximation.
import json, math, sys, os
sys.argv=[sys.argv[0],sys.argv[1],'58','70','62','55','32','50']+sys.argv[2:]
sys.path.insert(0,os.path.dirname(__file__))
import drive_time as drive
import numpy as np
from skimage import measure
from scipy.ndimage import gaussian_filter
G=sys.argv[8]; OUT=sys.argv[9]
LON0,LON1,LAT0,LAT1=-96.45,-94.40,28.95,30.62
STEP=0.012
lons=np.arange(LON0-0.1,LON1+0.1,STEP); lats=np.arange(LAT0-0.1,LAT1+0.1,STEP)
grid=np.array([[drive.tt(x,y) for x in lons] for y in lats])
grid=gaussian_filter(grid,1.2)
cs=measure.find_contours(grid,60.0)
c=max(cs,key=len)
ring=[(lons[0]+j*STEP, lats[0]+i*STEP) for i,j in c]
K=math.cos(math.radians(29.75)); W=720; S=W/((LON1-LON0)*K); H=round((LAT1-LAT0)*S)
def P(lon,lat): return ((lon-LON0)*K*S,(LAT1-lat)*S)
def d_ring(pts,tol=1.0):
    out=[];last=None
    for lon,lat in pts:
        x,y=P(lon,lat);q=(round(x,1),round(y,1))
        if last and abs(q[0]-last[0])<tol and abs(q[1]-last[1])<tol: continue
        out.append(q);last=q
    return 'M'+' '.join('%g %g'%p for p in out)+'z'
d=json.load(open(G))
feats=[f for f in d['features'] if f['id'][:2]=='48']
def rings(f):
    g=f['geometry']; polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
    for poly in polys:
        for r in poly: yield r
def inview(f): return any(LON0-.6<x<LON1+.6 and LAT0-.6<y<LAT1+.6 for r in rings(f) for x,y in r)
cty=[f for f in feats if inview(f)]
land=''.join(d_ring(r,1.2) for f in cty for r in rings(f))
area=d_ring(ring,0.8)
towns=[("Conroe",30.312,-95.456,"r",""),("The Woodlands",30.166,-95.461,"r",""),("Spring",30.065,-95.417,"r","m"),("Tomball",30.097,-95.616,"l","m"),
("Cypress",29.969,-95.697,"l",""),("Katy",29.786,-95.824,"l",""),("Sugar Land",29.620,-95.635,"r",""),("Richmond",29.582,-95.761,"l","m"),
("Pearland",29.564,-95.286,"r",""),("Pasadena",29.691,-95.209,"r","m"),("Baytown",29.736,-94.977,"r",""),("League City",29.507,-95.095,"r",""),
("Texas City",29.384,-94.903,"l","m"),("Galveston",29.301,-94.798,"r",""),("Angleton",29.169,-95.432,"l","m"),
("Cleveland",30.341,-95.086,"r","m"),("Dayton",30.047,-94.885,"r","m"),("Humble",29.999,-95.262,"r","m")]
o=[f'<svg class="area-map" viewBox="0 0 {W} {H}" role="img" aria-labelledby="mapTitle"><title id="mapTitle">Map of the area we buy in: about a one-hour drive from central Houston, reaching Conroe, Katy, Sugar Land, Baytown and Galveston</title>',
   f'<defs><clipPath id="landClip"><path d="{land}"/></clipPath></defs>',
   f'<rect width="{W}" height="{H}" fill="#D9E8F5"/>',
   '<g fill="#F4F6F9" stroke="#DCE3EC" stroke-width="1">'+''.join(f'<path d="{d_ring(r,1.2)}"/>' for f in cty for r in rings(f))+'</g>',
   f'<g clip-path="url(#landClip)"><path d="{area}" fill="#FFFFFF" stroke="#BF4A08" stroke-width="3.5" stroke-linejoin="round"/>'
   +'<g fill="none" stroke="#DCE3EC" stroke-width="1">'+''.join(f'<path d="{d_ring(r,1.2)}"/>' for f in cty for r in rings(f))+'</g>'
   +f'<path d="{area}" fill="none" stroke="#BF4A08" stroke-width="3.5" stroke-linejoin="round"/></g>']
ux,uy=P(-95.3422,29.7199)
o.append(f'<circle cx="{ux:.1f}" cy="{uy:.1f}" r="14" fill="#152F70" opacity=".14"/><circle cx="{ux:.1f}" cy="{uy:.1f}" r="7" fill="#152F70" stroke="#fff" stroke-width="2.5"/><text x="{ux+14:.1f}" y="{uy-12:.1f}" class="big">Houston</text>')
for name,lat,lon,side,minor in towns:
    x,y=P(lon,lat); cls=' class="minor"' if minor else ''
    tx=x+10 if side=="r" else x-10; anchor="start" if side=="r" else "end"
    o.append(f'<g{cls}><circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#BF4A08" stroke="#fff" stroke-width="2"/><text x="{tx:.1f}" y="{y+5.5:.1f}" text-anchor="{anchor}">{name}</text></g>')
o.append('</svg>')
open(OUT,'w').write(''.join(o)); print(W,H,len(''.join(o)),len(cs))
