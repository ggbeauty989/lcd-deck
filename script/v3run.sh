#!/bin/bash
# run one v2 stage: prints batch status, errors, per-body volume/faces
cd "$(dirname "$0")" && python3 -I v3gen.py "$1" && timeout 300 python3 -I mcpc.py "v3_$1.json" > "v3_$1.out" 2>&1
grep -E '^== |"error"|"index"|"warning": "|"name": "(Scocca|Coperchio)"|"volume_mm3"|^      "faces"' "v3_$1.out"
