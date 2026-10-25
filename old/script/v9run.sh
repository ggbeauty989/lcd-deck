#!/bin/bash
# run one v9 stage: prints batch status, errors, per-body volume/faces
cd "$(dirname "$0")" && python3 -I v9gen.py "$1" && timeout 300 python3 -I mcpc.py "v9_$1.json" > "v9_$1.out" 2>&1
grep -E '^== |"error"|"index"|"warning": "|"name": "(Scocca|Coperchio)"|"volume_mm3"|^      "faces"|"shells"' "v9_$1.out"
