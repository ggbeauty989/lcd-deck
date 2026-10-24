import json, sys
names = json.load(open("kcheck_names.json")) + ["cattura_d", "cattura_s"]
parts = open(sys.argv[1]).read().split("== execute")[1:]
ok = True
for n, p in zip(names, parts):
    hit = p.startswith(" ok")
    want_hit = n.startswith("cattura")
    good = hit == want_hit
    ok &= good
    if not good or want_hit:
        print(f"  {'OK ' if good else 'NO '} {n}: {'tocca il corpo' if hit else 'libero'}{' (atteso: sotto il dentino)' if want_hit else ''}")
print("  tutte le altre", len(names) - 2, "prove: libere" if ok else "", "" if ok else "-> PROBLEMI sopra")
