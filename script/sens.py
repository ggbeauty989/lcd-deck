import sys, glob, os, math, numpy as np
sys.argv = [sys.argv[0], sys.argv[1]]
exec(open("meshclash.py").read().split("hosts = ")[0])
D = sys.argv[1]
body = Solid(load(f"{D}/tmp-scocca.stl"))
pcb = load(f"{D}/tmp-c-Elecrow_7LCD_C__2_.stl")
Yf = np.array([0, s, c])
for shift in (0.0, -1.5, +1.6, -0.9, +1.2):
    P = samples(pcb + shift * Yf)
    d = body.depth_inside(P)
    print(f"circuito spostato di {shift:+.1f} mm lungo lo schermo: punti dentro il corpo = {(d > 0.05).sum()}")
# Pi against screen (LCD + PCB as hosts)
hosts = [Solid(load(f"{D}/tmp-c-Elecrow_7LCD_C.stl")), Solid(pcb)]
n = 0
for f in glob.glob(f"{D}/tmp-c-*.stl"):
    b = os.path.basename(f)
    if "Elecrow" in b or b.startswith("tmp-c-__"): continue
    P = samples(load(f))
    for h in hosts:
        if (h.depth_inside(P) > 0.05).any(): n += 1; print("contatto Pi/schermo:", b)
print("pezzi del Pi in contatto con lo schermo:", n)
