import sys, glob, os, numpy as np
D = sys.argv[1]
def load(p):
    d = open(p, "rb").read(); n = int.from_bytes(d[80:84], "little")
    a = np.frombuffer(d[84:84 + 50 * n], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    return a["v"].reshape(-1, 3, 3).astype(np.float64)
def dense(t, k=6):
    r = np.random.default_rng(0).random((len(t), k, 2)); m = r.sum(2) > 1; r[m] = 1 - r[m]
    return (t[:, None, 0] + r[..., :1] * (t[:, None, 1] - t[:, None, 0]) + r[..., 1:] * (t[:, None, 2] - t[:, None, 0])).reshape(-1, 3)
files = glob.glob(f"{D}/tmp-c-*.stl")
scr_parts, pi_parts = [], []
for f in files:
    t = load(f)
    (scr_parts if ("Elecrow" in f or t[:, :, 0].min() > 40) else pi_parts).append((f, t))
scr = np.concatenate([np.concatenate([t.reshape(-1, 3), dense(t)]) for _, t in scr_parts])
print("pezzi schermo:", len(scr_parts), " pezzi Pi:", len(pi_parts))
best = (1e9, None, None)
for f, t in pi_parts:
    P = np.concatenate([t.reshape(-1, 3), dense(t, 3)])
    lo, hi = P.min(0) - 12, P.max(0) + 12
    Q = scr[np.all((scr > lo) & (scr < hi), axis=1)]
    if not len(Q): continue
    for i in range(0, len(P), 1000):
        d = np.sqrt(((P[i:i + 1000, None, :] - Q[None, :, :]) ** 2).sum(2))
        j = np.unravel_index(d.argmin(), d.shape)
        if d[j] < best[0]: best = (d[j], os.path.basename(f), P[i + j[0]].round(1))
print("distanza minima Pi-schermo: %.2f mm  (pezzo %s, punto %s)" % best)
