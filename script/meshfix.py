"""Repair the small tessellation defects SolidCraft leaves in an exported STL.

Usage: python3 meshfix.py input.stl output.stl

Steps, all of which leave the shape unchanged:
  1. weld vertices closer than 0.001 mm
  2. drop zero-area (collinear) triangles
  3. split triangles at T-junctions (a vertex lying on another triangle's open edge)
  4. close the remaining small holes (every boundary loop under 2 mm across)
It refuses to write the file unless the result is closed and consistently oriented.
"""
import sys
from collections import Counter, defaultdict

import numpy as np

WELD = 1e-3
MAX_HOLE = 2.0


def weld(P, tol):
    """Merge points closer than tol (grid hashing + union-find, so pairs across a cell border merge too)."""
    parent = list(range(len(P)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    cells = defaultdict(list)
    keys = np.floor(P / tol).astype(np.int64)
    for i, k in enumerate(map(tuple, keys)):
        cells[k].append(i)
    for (x, y, z), members in cells.items():
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for j in cells.get((x + dx, y + dy, z + dz), ()):
                        for i in members:
                            if i < j and np.linalg.norm(P[i] - P[j]) < tol:
                                parent[find(i)] = find(j)
    roots = np.array([find(i) for i in range(len(P))])
    uniq, inv = np.unique(roots, return_inverse=True)
    return P[uniq], inv


def load(path):
    d = open(path, "rb").read()
    n = int.from_bytes(d[80:84], "little")
    a = np.frombuffer(d[84:84 + 50 * n], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    return a["v"].reshape(-1, 3, 3).astype(np.float64)


def save(path, V, F):
    T = V[F].astype(np.float32)
    nrm = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-12)
    rec = np.zeros(len(F), dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    rec["n"] = nrm
    rec["v"] = T.reshape(-1, 9)
    with open(path, "wb") as f:
        f.write(b"deck-v4 meshfix".ljust(80, b" "))
        f.write(len(F).to_bytes(4, "little"))
        f.write(rec.tobytes())


def area(V, F):
    return 0.5 * np.linalg.norm(np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]]), axis=1)


def half_edges(F):
    h = Counter()
    for a, b, c in F:
        h[(a, b)] += 1; h[(b, c)] += 1; h[(c, a)] += 1
    return h


def open_edges(F):
    h = half_edges(F)
    return [(u, v) for (u, v) in h if (v, u) not in h]


def split_t_junctions(V, F):
    """Split each triangle whose edge is open and has another open-edge vertex lying on it."""
    changed = True
    while changed:
        changed = False
        opens = open_edges(F)
        bverts = {v for e in opens for v in e}
        for (u, v) in opens:
            A, B = V[u], V[v]
            L = np.linalg.norm(B - A)
            if L < 1e-9:
                continue
            d = (B - A) / L
            on = []
            for w in bverts - {u, v}:
                t = np.dot(V[w] - A, d)
                if 1e-6 < t < L - 1e-6 and np.linalg.norm(A + t * d - V[w]) < 1e-4:
                    on.append((t, w))
            if not on:
                continue
            on.sort()
            for i, (a, b, c) in enumerate(F):
                for x, y, z in ((a, b, c), (b, c, a), (c, a, b)):
                    if (x, y) == (u, v):
                        chain = [u] + [w for _, w in on] + [v]
                        new = [[chain[k], chain[k + 1], z] for k in range(len(chain) - 1)]
                        F = np.vstack([np.delete(F, i, axis=0), new])
                        changed = True
                        break
                if changed:
                    break
            if changed:
                break
    return F


def close_holes(V, F):
    existing = {(min(u, v), max(u, v)) for (u, v) in half_edges(F)}
    opens = open_edges(F)
    nxt = defaultdict(list)
    for u, v in opens:
        nxt[u].append(v)
    used, new = set(), []
    for u, v in opens:
        if (u, v) in used:
            continue
        loop, cur = [u], (u, v)
        while True:
            used.add(cur)
            if cur[1] == loop[0]:
                break
            loop.append(cur[1])
            cands = [w for w in nxt[cur[1]] if (cur[1], w) not in used]
            if not cands:
                raise SystemExit(f"open boundary that is not a loop near {V[cur[1]].round(3)}")
            cur = (cur[1], cands[0])
        P = V[loop]
        span = np.linalg.norm(P.max(0) - P.min(0))
        if span > MAX_HOLE:
            raise SystemExit(f"hole {span:.2f} mm across near {P.mean(0).round(1)}: too big to close safely")
        # fan from the first vertex whose diagonals are not already edges of the mesh
        n = len(loop)
        for s in range(n):
            ring = loop[s:] + loop[:s]
            diag = {(min(ring[0], ring[k]), max(ring[0], ring[k])) for k in range(2, n - 1)}
            if not diag & existing:
                break
        else:
            raise SystemExit(f"cannot close the hole near {P.mean(0).round(1)} without duplicating an edge")
        existing |= diag
        # the loop runs along the existing half-edges; the patch must run the other way
        for k in range(1, n - 1):
            new.append([ring[0], ring[k + 1], ring[k]])
    return np.vstack([F, new]) if new else F


def main(src, dst):
    T = load(src)
    V, inv = weld(T.reshape(-1, 3), WELD)
    F = inv.reshape(-1, 3)
    vol0 = np.sum(np.einsum("ij,ij->i", T[:, 0], np.cross(T[:, 1], T[:, 2]))) / 6
    F = F[(F[:, 0] != F[:, 1]) & (F[:, 1] != F[:, 2]) & (F[:, 0] != F[:, 2])]
    F = F[area(V, F) > 1e-10]
    F = split_t_junctions(V, F)
    F = F[area(V, F) > 1e-10]
    F = close_holes(V, F)
    h = half_edges(F)
    bad = [e for e, k in h.items() if k != 1 or (e[1], e[0]) not in h]
    if bad:
        raise SystemExit(f"still not closed: {len(bad)} bad half-edges")
    vol1 = np.sum(np.einsum("ij,ij->i", V[F[:, 0]], np.cross(V[F[:, 1]], V[F[:, 2]]))) / 6
    save(dst, V, F)
    print(f"{src} -> {dst}: {len(T)} -> {len(F)} triangles, volume {vol0:.1f} -> {vol1:.1f} mm3, closed and oriented")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
