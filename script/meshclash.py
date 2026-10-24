"""Point-in-mesh clash check: which component surface points lie inside the deck body or cover.
Usage: meshclash.py <dir with tmp-*.stl>"""
import sys, glob, os, math
import numpy as np
D = sys.argv[1]

def load(p):
    d = open(p, "rb").read(); n = int.from_bytes(d[80:84], "little")
    a = np.frombuffer(d[84:84 + 50 * n], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    return a["v"].reshape(-1, 3, 3).astype(np.float64)

class Solid:
    """Ray parity along +X, triangles binned on a Y/Z grid."""
    def __init__(self, tris, cell=1.0):
        self.t = tris; self.cell = cell
        yz = tris[:, :, 1:]
        lo = np.floor(yz.min(1) / cell).astype(int); hi = np.floor(yz.max(1) / cell).astype(int)
        self.bins = {}
        for i in range(len(tris)):
            for a in range(lo[i, 0], hi[i, 0] + 1):
                for b in range(lo[i, 1], hi[i, 1] + 1):
                    self.bins.setdefault((a, b), []).append(i)
    def depth_inside(self, P):
        """Return for each point the distance along X to the nearest surface if inside, else 0."""
        out = np.zeros(len(P))
        keys = np.floor(P[:, 1:] / self.cell).astype(int)
        order = {}
        for k, key in enumerate(map(tuple, keys)):
            order.setdefault(key, []).append(k)
        for key, idx in order.items():
            tri_idx = self.bins.get(key)
            if not tri_idx: continue
            T = self.t[tri_idx]; Q = P[idx]
            A, B, C = T[:, 0], T[:, 1], T[:, 2]
            # barycentric in YZ
            v0 = (C - A)[:, 1:]; v1 = (B - A)[:, 1:]
            d00 = (v0 * v0).sum(1); d01 = (v0 * v1).sum(1); d11 = (v1 * v1).sum(1)
            den = d00 * d11 - d01 * d01
            ok = np.abs(den) > 1e-12
            v2 = Q[:, None, 1:] - A[None, :, 1:]
            d02 = (v2 * v0[None]).sum(2); d12 = (v2 * v1[None]).sum(2)
            with np.errstate(divide="ignore", invalid="ignore"):
                u = (d11 * d02 - d01 * d12) / den; v = (d00 * d12 - d01 * d02) / den
            hit = ok[None] & (u >= 0) & (v >= 0) & (u + v <= 1)
            xh = A[None, :, 0] + u * (C - A)[None, :, 0] + v * (B - A)[None, :, 0]
            dx = np.where(hit, xh - Q[:, 0:1], np.nan)
            ahead = np.sum(dx > 0, axis=1)
            inside = (ahead % 2) == 1
            near = np.nanmin(np.abs(dx), axis=1, initial=np.inf) if dx.size else np.full(len(Q), np.inf)
            out[np.array(idx)[inside]] = near[inside]
        return out

def samples(tris, n_inner=3):
    pts = [tris.reshape(-1, 3), tris.mean(1)]
    rng = np.random.default_rng(1)
    for _ in range(n_inner):
        r = rng.random((len(tris), 2)); m = r.sum(1) > 1; r[m] = 1 - r[m]
        pts.append(tris[:, 0] + r[:, :1] * (tris[:, 1] - tris[:, 0]) + r[:, 1:] * (tris[:, 2] - tris[:, 0]))
    P = np.concatenate(pts)
    return P + np.array([1.3e-4, 2.7e-4, -1.9e-4])     # jitter off exact edges

c, s = math.cos(math.radians(20)), math.sin(math.radians(20)); Of = np.array([0, 73 * s, 73 * c])
def face(P):
    d = P - Of
    return np.stack([d[:, 0], d[:, 1] * s + d[:, 2] * c, d[:, 1] * c - d[:, 2] * s], 1)

hosts = {"Scocca": Solid(load(f"{D}/tmp-scocca.stl")), "Coperchio": Solid(load(f"{D}/tmp-coperchio.stl"))}
for f in sorted(glob.glob(f"{D}/tmp-c-*.stl")):
    comp = os.path.basename(f)[6:-4]
    P = samples(load(f))
    for hn, H in hosts.items():
        dep = H.depth_inside(P)
        m = dep > 0.05
        if m.any():
            Q = P[m]; F = face(Q)
            print(f"{comp[:42]:42s} DENTRO {hn:9s} punti {m.sum():5d}  prof.max~{dep[m].max():5.2f} mm  "
                  f"mondo x {Q[:,0].min():6.1f}..{Q[:,0].max():6.1f} y {Q[:,1].min():5.1f}..{Q[:,1].max():5.1f} z {Q[:,2].min():5.1f}..{Q[:,2].max():5.1f} | "
                  f"schermo y {F[:,1].min():5.1f}..{F[:,1].max():5.1f} prof {F[:,2].min():5.1f}..{F[:,2].max():5.1f}")
print("fine")
