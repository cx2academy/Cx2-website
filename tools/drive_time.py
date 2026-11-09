# Approximate one-hour drive area from UH using major roads (Natural Earth) and typical non-rush speeds.
import json, math, heapq, sys
import numpy as np
from scipy.spatial import cKDTree
R=json.load(open(sys.argv[1]))
O=(-95.3422,29.7199)  # University of Houston
DT=(-95.3698,29.7604)
KX=111.32*math.cos(math.radians(29.8)); KY=110.57
def km(a,b): return math.hypot((a[0]-b[0])*KX,(a[1]-b[1])*KY)
FWY_IN, FWY_OUT, MAJ, SEC, LOCAL, RURAL, DETOUR = float(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4]),float(sys.argv[5]),float(sys.argv[6]),float(sys.argv[7]),1.25
def lspeed(xy): return LOCAL if km(xy,DT)<22 else RURAL
MPH=1.609
nodes=[];edges={}
def add(i,j,t):
    edges.setdefault(i,[]).append((j,t));edges.setdefault(j,[]).append((i,t))
for r in R:
    exp=r['expressway']==1 or (r['name'] in ('290','99','288','225','249') and any(x>-96.2 for l in r['lines'] for x,y in l)); maj=r['type'] in('Major Highway','Beltway')
    for line in r['lines']:
        pts=[]
        for a,b in zip(line,line[1:]):
            n=max(1,int(km(a,b)/0.8))
            for k in range(n): pts.append((a[0]+(b[0]-a[0])*k/n,a[1]+(b[1]-a[1])*k/n))
        pts.append(tuple(line[-1]))
        ids=[]
        for p in pts: nodes.append(p); ids.append(len(nodes)-1)
        for i,j in zip(ids,ids[1:]):
            p,q=nodes[i],nodes[j]; mid=((p[0]+q[0])/2,(p[1]+q[1])/2)
            if exp: v=FWY_IN if km(mid,DT)<19 else FWY_OUT
            else: v=(MAJ if maj else SEC) if km(mid,DT)>=19 else LOCAL+8
            add(i,j,km(p,q)/(v*MPH)*60)
P=np.array([((x-O[0])*KX,(y-O[1])*KY) for x,y in nodes])
T=cKDTree(P)
for i,j in T.query_pairs(1.2):  # intersections between roads
    add(i,j,np.hypot(*(P[i]-P[j]))*DETOUR/(lspeed(nodes[i])*MPH)*60+0.5)
dist=[math.inf]*len(nodes);pq=[]
for i in T.query_ball_point([0,0],4):
    d=np.hypot(*P[i])*DETOUR/(LOCAL*MPH)*60+2; dist[i]=d; heapq.heappush(pq,(d,i))
while pq:
    d,i=heapq.heappop(pq)
    if d>dist[i]: continue
    for j,t in edges.get(i,[]):
        if d+t<dist[j]: dist[j]=d+t; heapq.heappush(pq,(d+t,j))
dist=np.array(dist)
def tt(lon,lat):
    q=np.array([(lon-O[0])*KX,(lat-O[1])*KY])
    dd,ii=T.query(q,k=40)
    v=lspeed((lon,lat))
    best=np.min(dist[ii]+dd*DETOUR/(v*MPH)*60+1.5)
    return min(best,np.hypot(*q)*DETOUR/(LOCAL*MPH)*60+2)
if __name__=='__main__':
    towns={"Pearland":(-95.286,29.564),"Sugar Land":(-95.635,29.620),"Baytown":(-94.977,29.736),"Katy":(-95.824,29.786),"Rosenberg":(-95.809,29.557),"Texas City":(-94.903,29.384),"Dayton":(-94.885,30.047),"Brookshire":(-95.951,29.786),"Fulshear":(-95.900,29.693),"Angleton":(-95.432,29.169),"Conroe":(-95.456,30.312),"Waller":(-95.927,30.057),"Galveston":(-94.798,29.301),"Hempstead":(-96.078,30.097),"Liberty":(-94.795,30.058),"Cleveland":(-95.086,30.341),"Magnolia":(-95.750,30.209),"Sealy":(-96.157,29.781),"Willis":(-95.480,30.425),"Lake Jackson":(-95.434,29.034),"Wharton":(-96.102,29.311),"Freeport":(-95.360,28.954),"West Columbia":(-95.645,29.144),"Bellville":(-96.257,29.950),"Huntsville":(-95.551,30.724),"Navasota":(-96.088,30.388),"Columbus":(-96.540,29.706),"Anahuac":(-94.683,29.773),"Winnie":(-94.384,29.820)}
    for n,(x,y) in towns.items(): print(f"{n:14s}{tt(x,y):5.0f}")
