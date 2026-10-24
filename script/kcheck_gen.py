"""Kuman fit and assembly-path check for deck v5: every dummy must miss the body, except the capture probe."""
import json, math
D = "/home/roberto/Documenti/SolidCraft/deck-kuman7-pi4-v5.solidcraft"
c, s = math.cos(math.radians(20)), math.sin(math.radians(20))
FACE = {"origin": [0, 73 * s, 73 * c], "x_dir": [1, 0, 0], "y_dir": [0, s, c]}
SH = 2.4          # how far the screen goes in above its final place
BACK = 8.0        # last stretch of the approach that is checked

def blk(name, x0, y0, x1, y1, o0, o1):
    return [{"command": "sketch.create", "params": {"plane": FACE, "offset": f"{-o0} mm", "name": "Sk" + name}},
            {"command": "sketch.rectangle.two_point", "params": {"p0": [x0, y0], "p1": [x1, y1]}},
            {"command": "sketch.finish", "params": {}},
            {"command": "solid.extrude", "params": {"distance": o1 - o0, "direction": "negative", "operation": "new", "body_name": name, "name": name}}]

def screen(prefix, dy, o_extra, y_lo=None):
    """Glass, board, tabs and HDMI shifted by dy; o_extra extends every part backwards (approach sweep)."""
    parts = [("vetro", -82.35, -50, 82.35, 50, 2.05, 9.3), ("circuito", -82, -50, 82, 50, 9.3, 10.9),
             ("lingA_d", 74.05, 50, 82.05, 61.45, 9.3, 10.9), ("lingA_s", -82.05, 50, -74.05, 61.45, 9.3, 10.9),
             ("lingB_d", 74.05, -63.6, 82.05, -50, 9.3, 10.9), ("lingB_s", -82.05, -63.6, -74.05, -50, 9.3, 10.9),
             ("hdmi", 68, 34.1, 83.31, 49.37, 8.0, 13.0)]
    out, names = [], []
    for n, x0, y0, x1, y1, o0, o1 in parts:
        lo = y0 + dy if y_lo is None else min(y0, y0 + dy)
        hi = y1 + dy if y_lo is None else max(y1, y1 + dy)
        name = f"{prefix}_{n}"
        out += blk(name, x0, lo, x1, hi, o0, o1 + o_extra)
        names.append(name)
    return out, names

cmds, must_miss = [], []
for prefix, dy, extra, union in (("montato", 0, 0, None), ("avvicinamento", SH, BACK, None), ("scorrimento", SH, 0, True)):
    b, n = screen(prefix, dy, extra, union)
    cmds += b; must_miss += n
cmds += blk("cattura_d", 74.05, -63.6, 82.05, -61.0, 9.3, 12.5) + blk("cattura_s", -82.05, -63.6, -74.05, -61.0, 9.3, 12.5)
calls = [{"name": "open", "arguments": {"path": D}}, {"name": "batch", "arguments": {"verbose": False, "commands": cmds}}]
for n in must_miss + ["cattura_d", "cattura_s"]:
    calls.append({"name": "execute", "arguments": {"command": "solid.combine", "params": {"target": n, "tools": ["Scocca"], "operation": "intersect", "keep_tools": True}, "verbose": False}, "tag": n})
json.dump(calls, open("kcheck.json", "w"))
json.dump(must_miss, open("kcheck_names.json", "w"))
