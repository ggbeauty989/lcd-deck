"""Overhang report for a binary STL in print orientation (Z up, bed at min Z).
Usage: overhang.py file.stl rot_x_deg   (rot_x_deg: rotation that maps print coords back to world coords, for labelling)"""
import struct, sys, math
from collections import defaultdict
path, back = sys.argv[1], math.radians(float(sys.argv[2]))
data = open(path, "rb").read()
n = struct.unpack("<I", data[80:84])[0]
tris = []
for i in range(n):
    v = struct.unpack("<12f", data[84 + 50 * i: 84 + 50 * i + 48])
    tris.append((v[3:6], v[6:9], v[9:12]))
zmin = min(p[2] for t in tris for p in t)
def norm_area(t):
    a, b, c = t
    u = [b[k] - a[k] for k in range(3)]; w = [c[k] - a[k] for k in range(3)]
    nx, ny, nz = u[1]*w[2]-u[2]*w[1], u[2]*w[0]-u[0]*w[2], u[0]*w[1]-u[1]*w[0]
    l = math.sqrt(nx*nx + ny*ny + nz*nz)
    return (nx/l, ny/l, nz/l) if l else (0, 0, 0), l / 2
cb, sb = math.cos(back), math.sin(back)
groups = defaultdict(lambda: [0.0, 0.0, [1e9, -1e9], 0.0, [1e9,1e9,1e9], [-1e9,-1e9,-1e9]])
for t in tris:
    (nx, ny, nz), A = norm_area(t)
    if A < 1e-6: continue
    zc = sum(p[2] for p in t) / 3
    if zc - zmin < 0.3: continue          # on the bed
    ang = math.degrees(math.acos(max(-1, min(1, -nz))))  # 0 = facing straight down
    if ang >= 45: continue                # self-supporting
    cx, cy = sum(p[0] for p in t)/3, sum(p[1] for p in t)/3
    # world coords (undo the print rotation about X)
    wy, wz = cy*cb - zc*sb, cy*sb + zc*cb
    key = (round(cx/12), round(wy/12), round(wz/12), 'flat' if ang < 10 else 'steep')
    g = groups[key]; g[0] += A; g[1] = max(g[1], A); g[2][0] = min(g[2][0], zc); g[2][1] = max(g[2][1], zc); g[3] += ang*A
    for k,val in enumerate((cx,wy,wz)): g[4][k]=min(g[4][k],val); g[5][k]=max(g[5][k],val)
rows = sorted(groups.items(), key=lambda kv: -kv[1][0])
tot = sum(g[0] for _, g in rows)
print(f"{path.split('/')[-1]}: overhang area <45deg from down = {tot:.0f} mm2 in {len(rows)} clusters")
for k, g in rows[:60]:
    print(f"  area {g[0]:7.1f} mm2  ang~{g[3]/g[0]:4.0f}deg  print-z {g[2][0]:5.1f}..{g[2][1]:5.1f}  world x {g[4][0]:6.1f}..{g[5][0]:6.1f} y {g[4][1]:6.1f}..{g[5][1]:6.1f} z {g[4][2]:6.1f}..{g[5][2]:6.1f}")
