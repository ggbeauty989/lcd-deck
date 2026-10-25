#!/bin/bash
# Rebuild deck v11, check the Kuman fit with a print margin, export the STEP and the print-oriented STLs, repair them, check overhangs.
set -u
SP="$(cd "$(dirname "$0")" && pwd)"; O=/home/roberto/Documenti/SolidCraft
cd "$SP"
echo "== costruzione"
for s in A1 A3 A4 B1 B1b C1 C1b B3 A2 A2b B2 C2 C3 C4 D1 D2 D3 D4 D6; do
  ./v11run.sh $s > "p11_$s.log" 2>&1
  if grep -q -E 'ERROR|"error"' "p11_$s.log"; then echo "ERRORE nella tappa $s"; grep -A2 '"error"' "v11_$s.out" | head -3; exit 1; fi
  grep -E '"shells"' "v11_$s.out" | grep -vq '"shells": 1' && { echo "tappa $s: corpo in piu' pezzi"; exit 1; }
done
echo "== montaggio e inserimento del Kuman (0,4 mm di margine di stampa)"
cp "$O/deck-kuman7-pi4-v11.solidcraft" "$O/tmp-v11-check.solidcraft"
python3 -I kcheck_gen.py "$O/tmp-v11-check.solidcraft" 0.4
timeout 900 python3 -I mcpc.py kcheck.json > p11_kcheck.log 2>&1
python3 -I kcheck_report.py p11_kcheck.log
echo "== esportazione"
cat > v11exp.json <<J
[{"name":"open","arguments":{"path":"$O/deck-kuman7-pi4-v11.solidcraft"}},
 {"name":"export","arguments":{"path":"$O/deck-v11-assieme.step"}},
 {"name":"execute","arguments":{"command":"solid.move","params":{"bodies":["Scocca"],"axis":[1,0,0],"angle":"110 deg"},"verbose":false}},
 {"name":"execute","arguments":{"command":"solid.move","params":{"bodies":["Coperchio"],"axis":[1,0,0],"angle":"-90 deg"},"verbose":false}},
 {"name":"export","arguments":{"path":"$O/deck-v11-scocca.stl","bodies":["Scocca"]}},
 {"name":"export","arguments":{"path":"$O/deck-v11-coperchio.stl","bodies":["Coperchio"]}}]
J
timeout 600 python3 -I mcpc.py v11exp.json > p11_exp.log 2>&1; grep -c 'export ok' p11_exp.log
echo "== riparazione mesh"
for p in scocca coperchio; do
  python3 -I meshfix.py "$O/deck-v11-$p.stl" "$O/tmp-rip-$p.stl" || exit 1
  mv "$O/tmp-rip-$p.stl" "$O/deck-v11-$p.stl"
done
rm -f "$O"/tmp-v11-check.solidcraft*
echo "== sbalzi"
python3 -I overhang.py "$O/deck-v11-scocca.stl" -110 | head -1
python3 -I overhang.py "$O/deck-v11-coperchio.stl" 90 | head -1
echo "== fine"
