#!/bin/bash
# Rebuild deck v4, export, repair the STLs, re-run every check. Prints a compact report.
set -u
SP="$(cd "$(dirname "$0")" && pwd)"; O=/home/roberto/Documenti/SolidCraft; MY=/tmp/claude-1000/-home-roberto-lcd-deck/4472b4d5-dcaa-4381-803d-a2b3c8c25541/scratchpad
cd "$SP"
echo "== costruzione"
for s in A1 A3 A4 B1 C1 C1b A2 A2b B2 B3 C2 C4 D1 D2 D3 D4 D5; do
  ./v4run.sh $s > "pl_$s.log" 2>&1
  if grep -q ERROR "pl_$s.log"; then echo "ERRORE nella tappa $s"; grep -A2 '"error"' "pl_$s.log" | head -3; exit 1; fi
done
grep -E '"shells"|"volume_mm3"' v4_D5.out | grep -v '^    ' | paste -s -d' '
echo "== esportazione"
timeout 600 python3 -I mcpc.py v4exp.json > pl_exp.log 2>&1; grep -c 'export ok' pl_exp.log
echo "== riparazione mesh"
for p in scocca coperchio; do
  python3 -I /home/roberto/lcd-deck/script/meshfix.py "$O/deck-v4-$p.stl" "$MY/rip-$p.stl" || exit 1
  python3 -I "$MY/stlcheck.py" "$MY/rip-$p.stl" | sed -n '2,5p'
  cp "$MY/rip-$p.stl" "$O/deck-v4-$p.stl"
done
echo "== modelli reali e interferenze"
timeout 900 python3 -I mcpc.py real4.json > pl_real.log 2>&1; grep -E '^==' pl_real.log | paste -s -d' '
timeout 900 python3 -I mcpc.py mexp4.json > pl_mexp.log 2>&1; echo "export componenti: $(grep -c 'export ok' pl_mexp.log)"
timeout 1500 python3 -I meshclash.py $O/componenti 2>/dev/null
timeout 900 python3 -I standoffdist.py $O/componenti
timeout 900 python3 -I conndist.py $O/componenti
timeout 900 python3 -I pidist.py $O/componenti
rm -f $O/componenti/tmp-*.stl $O/tmp-*.stl $O/tmp-*.3mf
echo "== sbalzi"
python3 -I overhang.py $O/deck-v4-scocca.stl -110 | head -1
python3 -I overhang.py $O/deck-v4-coperchio.stl 90 | head -1
echo "== fine"
