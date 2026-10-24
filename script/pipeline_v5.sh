#!/bin/bash
# Rebuild deck v5 (Kuman fit), export, repair the STLs, check against a Kuman model and the Pi 4. Prints a compact report.
set -u
SP="$(cd "$(dirname "$0")" && pwd)"; O=/home/roberto/Documenti/SolidCraft; MY=/tmp/claude-1000/-home-roberto-lcd-deck/4472b4d5-dcaa-4381-803d-a2b3c8c25541/scratchpad
cd "$SP"
echo "== costruzione"
for s in A1 A3 A4 B1 B1b C1 C1b B3 A2 A2b B2 C2 C4 D1 D2 D3 D4; do
  ./v5run.sh $s > "p5_$s.log" 2>&1
  if grep -q ERROR "p5_$s.log"; then echo "ERRORE nella tappa $s"; grep -A2 '"error"' "p5_$s.log" | head -3; exit 1; fi
  grep -E '"shells"' "v5_$s.out" | grep -vq '"shells": 1' && { echo "tappa $s: corpo in piu' pezzi"; exit 1; }
done
python3 -I - <<'PY'
import json
t=open("v5_D4.out").read(); m=t.split("== measure ok\n",1)[1].split("\n== ",1)[0]
for b in json.loads(m)["bodies"]: print(f'   {b["name"]}: {b["volume_mm3"]:.1f} mm3')
PY
echo "== montaggio e inserimento del Kuman"
timeout 900 python3 -I mcpc.py kcheck.json > p5_kcheck.log 2>&1
python3 -I kcheck_report.py p5_kcheck.log
echo "== esportazione"
timeout 600 python3 -I mcpc.py v5exp.json > p5_exp.log 2>&1; grep -c 'export ok' p5_exp.log
echo "== riparazione mesh"
for p in scocca coperchio; do
  python3 -I /home/roberto/lcd-deck/script/meshfix.py "$O/deck-v5-$p.stl" "$MY/rip5-$p.stl" || exit 1
  python3 -I "$MY/stlcheck.py" "$MY/rip5-$p.stl" | sed -n '3,4p'
  cp "$MY/rip5-$p.stl" "$O/deck-v5-$p.stl"
done
echo "== Kuman (dalle misure) e Raspberry Pi"
timeout 900 python3 -I mcpc.py real5.json > p5_real.log 2>&1; grep -E '^==' p5_real.log | paste -s -d' '
python3 -I - "$O" <<'PY'
import json, sys
O=sys.argv[1]
t=open("p5_real.log").read(); m=t.split("== measure ok\n",1)[1].split("\n== ",1)[0]
names=[b["name"] for b in json.loads(m)["bodies"]]
calls=[{"name":"open","arguments":{"path":f"{O}/deck-v5-modelli-reali.solidcraft"}},
       {"name":"export","arguments":{"path":f"{O}/componenti/tmp-scocca.stl","bodies":["Scocca"]}},
       {"name":"export","arguments":{"path":f"{O}/componenti/tmp-coperchio.stl","bodies":["Coperchio"]}}]
for n in names:
    if n in ("Scocca","Coperchio"): continue
    safe="".join(ch if ch.isalnum() else "_" for ch in n)
    calls.append({"name":"export","arguments":{"path":f"{O}/componenti/tmp-c-{safe}.stl","bodies":[n]}})
json.dump(calls,open("mexp5.json","w"))
PY
timeout 900 python3 -I mcpc.py mexp5.json > p5_mexp.log 2>&1; echo "export componenti: $(grep -c 'export ok' p5_mexp.log)"
timeout 1500 python3 -I meshclash.py $O/componenti 2>/dev/null
timeout 900 python3 -I standoffdist.py $O/componenti
timeout 900 python3 -I conndist.py $O/componenti
timeout 900 python3 -I pidist.py $O/componenti
rm -f $O/componenti/tmp-*.stl $O/tmp-*.stl $O/tmp-*.3mf
echo "== sbalzi"
python3 -I overhang.py $O/deck-v5-scocca.stl -110 | head -1
python3 -I overhang.py $O/deck-v5-coperchio.stl 90 | head -1
echo "== fine"
