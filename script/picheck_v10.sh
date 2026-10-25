#!/bin/bash
# Put the official Raspberry Pi 4 STEP (componenti/raspberry-pi-4.step, not in the repo) on the v10 cover
# and measure the clearance between the parts under the Pi and the cover standoffs.
set -u
SP="$(cd "$(dirname "$0")" && pwd)"; O=/home/roberto/Documenti/SolidCraft
cd "$SP"
cat > pic10.json <<J
[{"name":"open","arguments":{"path":"$O/deck-kuman7-pi4-v10.solidcraft"}},
 {"name":"execute","arguments":{"command":"file.insert_step","params":{"path":"$O/componenti/raspberry-pi-4.step","name":"RaspberryPi4","matrix":[[-1,0,0,-43],[0,-1,0,59.2],[0,0,1,53]]},"verbose":false}},
 {"name":"measure","arguments":{}},
 {"name":"save","arguments":{"path":"$O/deck-v10-modelli-reali.solidcraft"}}]
J
timeout 900 python3 -I mcpc.py pic10.json > p10_pi.log 2>&1; grep -E '^==' p10_pi.log | paste -s -d' '
python3 -I - "$O" <<'PY'
import json, sys
O=sys.argv[1]
t=open("p10_pi.log").read(); m=t.split("== measure ok\n",1)[1].split("\n== ",1)[0]
names=[b["name"] for b in json.loads(m)["bodies"] if b["name"] not in ("Scocca","Coperchio")]
calls=[{"name":"open","arguments":{"path":f"{O}/deck-v10-modelli-reali.solidcraft"}},
       {"name":"export","arguments":{"path":f"{O}/componenti/tmp-coperchio.stl","bodies":["Coperchio"]}}]
for n in names:
    safe="".join(ch if ch.isalnum() else "_" for ch in n)
    calls.append({"name":"export","arguments":{"path":f"{O}/componenti/tmp-c-{safe}.stl","bodies":[n]}})
json.dump(calls,open("pic10exp.json","w")); print("corpi del Pi:", len(names))
PY
timeout 900 python3 -I mcpc.py pic10exp.json > p10_piexp.log 2>&1; echo "export: $(grep -c 'export ok' p10_piexp.log)"
timeout 900 python3 -I standoffdist.py "$O/componenti"
rm -f "$O"/componenti/tmp-*.stl pic10.json pic10exp.json p10_pi*.log
