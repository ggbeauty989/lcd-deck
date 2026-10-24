"""Minimal stdio MCP client for solidcraft-cli. Usage: mcpc.py list | mcpc.py calls.json"""
import json, subprocess, sys
CMD = ["/home/roberto/Applications/solidcraft-cli/bin/solidcraft-cli", "mcp", "--allow-path", "/home/roberto/Documenti/SolidCraft"]
p = subprocess.Popen(CMD, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
nid = 0
def rpc(method, params=None, notify=False):
    global nid
    msg = {"jsonrpc": "2.0", "method": method}
    if params is not None: msg["params"] = params
    if not notify:
        nid += 1; msg["id"] = nid
    p.stdin.write(json.dumps(msg) + "\n"); p.stdin.flush()
    if notify: return None
    while True:
        line = p.stdout.readline()
        if not line: raise SystemExit("server closed: " + p.stderr.read())
        r = json.loads(line)
        if r.get("id") == nid: return r
rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "claude-script", "version": "0"}})
rpc("notifications/initialized", notify=True)
if sys.argv[1] == "list":
    r = rpc("tools/list")
    for t in r["result"]["tools"]:
        print("##", t["name"]); print(t.get("description", "")); print(json.dumps(t.get("inputSchema", {}).get("properties", {}), ensure_ascii=False)); print()
    for m in ("resources/list", "prompts/list"):
        print(m, json.dumps(rpc(m), ensure_ascii=False)[:3000])
else:
    calls = json.load(open(sys.argv[1]))
    for c in calls:
        r = rpc("tools/call", {"name": c["name"], "arguments": c.get("arguments", {})})
        res = r.get("result") or r.get("error")
        out = []
        for part in (res.get("content") or []) if isinstance(res, dict) else []:
            if part.get("type") == "image" and c.get("save"):
                import base64; open(c["save"], "wb").write(base64.b64decode(part["data"])); out.append(f"<image saved {c['save']}>")
            else:
                out.append(part.get("text", f"<{part.get('type')}>"))
        print(f"== {c['name']} {'ERROR' if (r.get('error') or (res or {}).get('isError')) else 'ok'}")
        print("\n".join(out) if out else json.dumps(res)[:4000])
p.stdin.close(); p.wait(timeout=30)
