"""Add simplified screen + Raspberry Pi 4 bodies to a copy of the v3 deck (deck-v3-componenti.solidcraft)."""
import json
O = "/home/roberto/Documenti/SolidCraft"
FACE = {"origin": [0, 23.25736, 63.89912], "x_dir": [1, 0, 0], "y_dir": [0, 0.342020, 0.939693]}

def cmd(c, **p):
    return {"command": c, "params": p}

def face_block(name, x0, y0, x1, y1, off0, off1):
    """Block on the inclined screen plane: face coords x/y, depth from the front face off0..off1 (mm)."""
    return [cmd("sketch.create", plane=FACE, offset=f"{-off0} mm", name="Sk" + name),
            cmd("sketch.rectangle.two_point", p0=[x0, y0], p1=[x1, y1]),
            cmd("sketch.finish"),
            cmd("solid.extrude", distance=off1 - off0, direction="negative", operation="new", body_name=name, name=name)]

def face_disc(name, x, y, d, off0, off1):
    return [cmd("sketch.create", plane=FACE, offset=f"{-off0} mm", name="Sk" + name),
            cmd("sketch.circle.center", center=[x, y], radius=d / 2),
            cmd("sketch.finish"),
            cmd("solid.extrude", distance=off1 - off0, direction="negative", operation="new", body_name=name, name=name)]

def box(name, x0, x1, y0, y1, z0, z1):
    return [cmd("solid.box", length=x1 - x0, width=y1 - y0, height=z1 - z0,
                center=[(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2], operation="new", body_name=name, name=name)]

screen = []
screen += face_block("Schermo_vetro", -82.35, -50, 82.35, 50, 2.05, 7.65)
screen += face_block("Schermo_circuito", -78, -50, 78, 50, 7.65, 9.25)
screen += face_block("Schermo_HDMI", 66, 42, 79.5, 57, 9.25, 13)
screen += face_block("Schermo_USB_touch", 73, 30, 79.5, 38, 9.25, 12)
screen += face_block("Schermo_USB_power", 73, 17, 79.5, 25, 9.25, 12)
screen += face_block("Schermo_interruttore", 72, 7, 79.5, 14, 9.25, 12.5)
pads = []
for i, (x, y) in enumerate([(79, -45), (-79, -45), (-79, 45), (40, 45)]):
    pads += face_disc(f"Gommino{i+1}", x, y, 8, 9.3, 12)
pi = []
pi += box("Pi_scheda", -83.5, -0.5, 58.4, 60.0, 25, 81)
pi += box("Pi_Ethernet", -86, -65, 44.9, 58.4, 27.25, 43.25)
pi += box("Pi_USB2", -86, -69, 42.4, 58.4, 46.7, 61.3)
pi += box("Pi_USB3", -86, -69, 42.4, 58.4, 64.7, 79.3)
pi += box("Pi_USB_C", -16.2, -7.2, 55.2, 58.4, 74.5, 82)
pi += box("Pi_microHDMI0", -30, -23, 55.4, 58.4, 74.5, 82)
pi += box("Pi_microHDMI1", -43.5, -36.5, 55.4, 58.4, 74.5, 82)
pi += box("Pi_GPIO", -58.4, -7.6, 49.9, 58.4, 26, 31)
pi += box("Pi_SoC", -36.5, -21.5, 55.9, 58.4, 43.5, 58.5)
colors = {"Schermo_vetro": "#0b0f19", "Schermo_circuito": "#1d4ed8", "Schermo_HDMI": "#c9cdd2", "Schermo_USB_touch": "#c9cdd2",
          "Schermo_USB_power": "#c9cdd2", "Schermo_interruttore": "#f5f5f5", "Pi_scheda": "#15803d", "Pi_Ethernet": "#c9cdd2",
          "Pi_USB2": "#c9cdd2", "Pi_USB3": "#2563eb", "Pi_USB_C": "#c9cdd2", "Pi_microHDMI0": "#c9cdd2", "Pi_microHDMI1": "#c9cdd2",
          "Pi_GPIO": "#111111", "Pi_SoC": "#6b7280"}
colors.update({f"Gommino{i+1}": "#facc15" for i in range(4)})
look = [cmd("appearance.assign", bodies=[b], color=c) for b, c in colors.items()]
calls = [{"name": "open", "arguments": {"path": f"{O}/deck-kuman7-pi4-v3.solidcraft"}},
         {"name": "batch", "arguments": {"verbose": False, "commands": screen + pads + pi + look}},
         {"name": "measure", "arguments": {}},
         {"name": "save", "arguments": {"path": f"{O}/deck-v3-componenti.solidcraft"}}]
json.dump(calls, open("comp.json", "w"))
json.dump(sorted(colors), open("comp_bodies.json", "w"))
