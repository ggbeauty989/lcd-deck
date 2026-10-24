"""Clearance from the Elecrow side connectors to the deck body (surface-sample distance)."""
import sys, glob, os, math, numpy as np
D = sys.argv[1]
def load(p):
    d = open(p, "rb").read(); n = int.from_bytes(d[80:84], "little")
    a = np.frombuffer(d[84:84 + 50 * n], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    return a["v"].reshape(-1, 3, 3).astype(np.float64)
def dense(t, k=8):
    r = np.random.default_rng(0).random((len(t), k, 2)); m = r.sum(2) > 1; r[m] = 1 - r[m]
    return (t[:, None, 0] + r[..., :1] * (t[:, None, 1] - t[:, None, 0]) + r[..., 1:] * (t[:, None, 2] - t[:, None, 0])).reshape(-1, 3)
body = load(f"{D}/tmp-scocca.stl"); B = np.concatenate([body.reshape(-1, 3), dense(body, 4)])
c, s = math.cos(math.radians(20)), math.sin(math.radians(20)); Of = np.array([0, 73 * s, 73 * c])
for f in glob.glob(f"{D}/tmp-c-*.stl"):
    t = load(f)
    if t[:, :, 0].min() < 60: continue                     # only the parts on the +X edge of the screen
    P = np.concatenate([t.reshape(-1, 3), dense(t)])
    lo, hi = P.min(0) - 15, P.max(0) + 15
    Q = B[np.all((B > lo) & (B < hi), axis=1)]
    d = np.sqrt(((P[:, None, :] - Q[None, :, :]) ** 2).sum(2)) if len(Q) else np.array([[np.inf]])
    i, j = np.unravel_index(d.argmin(), d.shape)
    F = P - Of
    fy = F[:, 1] * s + F[:, 2] * c; off = F[:, 1] * c - F[:, 2] * s
    print(f"{os.path.basename(f)[6:-4][:34]:34s} schermo-y {fy.min():5.1f}..{fy.max():5.1f}  profondita {off.min():5.1f}..{off.max():5.1f}  distanza minima dal corpo {d[i, j]:.2f} mm")
