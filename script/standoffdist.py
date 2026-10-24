"""Clearance between Pi parts and the cover (standoffs) excluding the PCB face that rests on them."""
import sys, glob, os, numpy as np
D = sys.argv[1]
def load(p):
    d = open(p, "rb").read(); n = int.from_bytes(d[80:84], "little")
    a = np.frombuffer(d[84:84 + 50 * n], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    return a["v"].reshape(-1, 3, 3).astype(np.float64)
def dense(t, k=6):
    r = np.random.default_rng(0).random((len(t), k, 2)); m = r.sum(2) > 1; r[m] = 1 - r[m]
    return (t[:, None, 0] + r[..., :1] * (t[:, None, 1] - t[:, None, 0]) + r[..., 1:] * (t[:, None, 2] - t[:, None, 0])).reshape(-1, 3)
cov = load(f"{D}/tmp-coperchio.stl"); C = np.concatenate([cov.reshape(-1, 3), dense(cov, 4)])
C = C[C[:, 1] < 65.01]                                   # standoffs and pillars only (in front of the plate)
best = (1e9, None, None)
for f in glob.glob(f"{D}/tmp-c-*.stl"):
    t = load(f)
    if t[:, :, 0].min() > 40 or "Elecrow" in f or "CornerRadius" in f: continue   # skip screen parts and the Pi PCB itself
    P = np.concatenate([t.reshape(-1, 3), dense(t, 3)])
    P = P[P[:, 1] > 59.0]                                 # parts behind the Pi board, towards the cover
    if not len(P): continue
    lo, hi = P.min(0) - 8, P.max(0) + 8
    Q = C[np.all((C > lo) & (C < hi), axis=1)]
    if not len(Q): continue
    for i in range(0, len(P), 2000):
        d = np.sqrt(((P[i:i + 2000, None, :] - Q[None, :, :]) ** 2).sum(2))
        j = np.unravel_index(d.argmin(), d.shape)
        if d[j] < best[0]: best = (d[j], os.path.basename(f)[6:-4], P[i + j[0]].round(1))
print("distanza minima tra componenti sotto il Pi e colonnine/coperchio: %.2f mm (%s a %s)" % best)
