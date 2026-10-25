#!/bin/bash
# run one v11 stage: prints batch status, errors, per-body volume/faces
cd "$(dirname "$0")" && python3 -I v11gen.py "$1" && timeout 300 python3 -I mcpc.py "v11_$1.json" > "v11_$1.out" 2>&1
grep -E '^== |"error"|"index"|"warning": "|"name": "(Scocca|Coperchio)"|"volume_mm3"|^      "faces"|"shells"' "v11_$1.out"
