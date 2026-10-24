"""Generate the v2 deck build stages as MCP call lists: python3 v2gen.py <stage> -> v2_<stage>.json"""
import json, sys
D = "/home/roberto/Documenti/SolidCraft/deck-kuman7-pi4-v2.solidcraft"
FACE = {"origin": [0, 23.25736, 63.89912], "x_dir": [1, 0, 0], "y_dir": [0, 0.342020, 0.939693]}
SIDE = {"origin": [96, 23.25736, 63.89912], "x_dir": [0, 0.342020, 0.939693], "y_dir": [0, 0.939693, -0.342020]}
S, C = ["Scocca"], ["Coperchio"]

def b(cmds):
    return {"name": "batch", "arguments": {"verbose": False, "commands": cmds}}

def cmd(c, **p):
    return {"command": c, "params": p}

stages = {}
stages["A1"] = [b([
    cmd("parameters.add", name="glass_w", expression="164.7 mm", comment="larghezza vetro misurata"),
    cmd("parameters.add", name="glass_h", expression="100 mm", comment="altezza vetro misurata"),
    cmd("parameters.add", name="fit", expression="0.4 mm", comment="gioco per lato del vetro nella tasca (0.2-0.8)"),
    cmd("parameters.add", name="lip", expression="2 mm", comment="spessore del bordino frontale"),
    cmd("parameters.add", name="stack", expression="9 mm", comment="spessore schermo vetro+circuito, connettori esclusi"),
    cmd("parameters.add", name="pocket_end", expression="7 mm", comment="profondita fine tasca vetro dalla faccia frontale"),
    cmd("parameters.add", name="cav_w", expression="168 mm", comment="larghezza vano circuito dietro al vetro"),
    cmd("parameters.add", name="cav_h", expression="114 mm", comment="altezza vano circuito dietro al vetro"),
    cmd("parameters.add", name="wall", expression="3.5 mm", comment="spessore pareti del corpo"),
    cmd("sketch.create", plane="YZ", name="ProfiloCuneo"),
    cmd("sketch.line", points=[[0, 0], [44.1206, 121.2204], [65, 121.2204], [65, 0]], closed=True),
    cmd("sketch.finish"),
    cmd("solid.extrude", distance=180, direction="symmetric", operation="new", body_name="Scocca", name="Cuneo"),
])]
stages["A2"] = [b([
    cmd("solid.fillet", edges=[[90, 22.0603, 60.6102], [-90, 22.0603, 60.6102], [90, 54.5603, 121.2204], [-90, 54.5603, 121.2204], [0, 44.1206, 121.2204]], radius=6, name="RaccordiEsterni"),
])]
stages["A3"] = [b([
    cmd("solid.shell", faces=[[0, 65, 60]], thickness="wall", direction="inside", name="Svuota"),
    cmd("solid.box", length=180, width=35, height=3.5, center=[0, 82.5, 1.75], operation="join", targets=S, name="Piede"),
])]
stages["A4"] = [b([
    cmd("solid.fillet", edges=[[90, 100, 1.75], [-90, 100, 1.75]], radius=12, name="RaccordiPiede"),
])]
stages["B1"] = [b([
    cmd("sketch.create", plane=FACE, offset="-3 mm", name="SkAnello1"),
    cmd("sketch.rectangle.two_point", p0=[-88, -64], p1=[88, 58]),
    cmd("sketch.draw.dimensioned", command="sketch.rectangle.center", params={"center": [0, 0], "corner": [82.75, 50.4]}, dimensions={"width": "glass_w + 2*fit", "height": "glass_h + 2*fit"}),
    cmd("sketch.finish"),
    cmd("solid.extrude", distance="pocket_end - 3 mm", direction="negative", operation="join", targets=S, profiles=[{"point": [85.5, 0]}], name="AnelloVetro"),
    cmd("sketch.create", plane=FACE, offset="0.5 mm - pocket_end", name="SkAnello2"),
    cmd("sketch.rectangle.two_point", p0=[-88.5, -63.5], p1=[88.5, 58.5]),
    cmd("sketch.draw.dimensioned", command="sketch.rectangle.center", params={"center": [0, 0], "corner": [84, 57]}, dimensions={"width": "cav_w", "height": "cav_h"}),
    cmd("sketch.finish"),
    cmd("solid.extrude", distance="lip + stack - pocket_end + 0.5 mm", direction="negative", operation="join", targets=S, profiles=[{"point": [86, 0]}], name="AnelloCircuito"),
    cmd("sketch.create", plane=FACE, offset="-lip", name="SkTasca"),
    cmd("sketch.draw.dimensioned", command="sketch.rectangle.center", params={"center": [0, 0], "corner": [82.75, 50.4]}, dimensions={"width": "glass_w + 2*fit", "height": "glass_h + 2*fit"}),
    cmd("sketch.finish"),
    cmd("solid.extrude", distance=2, direction="negative", operation="cut", targets=S, name="TascaVetro"),
    cmd("sketch.create", plane=FACE, offset="1 mm", name="SkFinestra"),
    cmd("sketch.rectangle.rounded", p0=[-78.5, -44.5], p1=[78.5, 44.5], radius=4),
    cmd("sketch.finish"),
    cmd("solid.extrude", distance=4, direction="negative", operation="cut", targets=S, name="FinestraSchermo"),
])]
stages["B2"] = [b([
    cmd("solid.fillet", edges=[[0, 8.0370, 22.0800]], radius=1.5, name="SmussoFinestra"),
])]
stages["B3"] = [b([
    cmd("sketch.create", plane=SIDE, name="SkConnettori"),
    cmd("sketch.rectangle.rounded", p0=[2, 7], p1=[56, 25], radius=4),
    cmd("sketch.finish"),
    cmd("solid.extrude", distance=16, direction="positive", operation="cut", targets=S, name="AperturaConnettori"),
    cmd("sketch.create", plane="YZ", offset="-84 mm", name="SkUSB"),
    cmd("sketch.rectangle.rounded", p0=[40, 25], p1=[60, 81], radius=4),
    cmd("sketch.finish"),
    cmd("solid.extrude", distance=10, direction="negative", operation="cut", targets=S, name="AperturaUSB"),
])]
stages["C1"] = [b([
    cmd("solid.box", length=8, width=10, height=10, center=[83, 60, 8], operation="join", targets=S, name="TorrettaBD"),
    cmd("solid.box", length=8, width=10, height=10, center=[-83, 60, 8], operation="join", targets=S, name="TorrettaBS"),
    cmd("solid.box", length=8, width=6, height=8, center=[83, 62, 114.2204], operation="join", targets=S, name="TorrettaAD"),
    cmd("solid.box", length=8, width=6, height=8, center=[-83, 62, 114.2204], operation="join", targets=S, name="TorrettaAS"),
    cmd("solid.cylinder", diameter=2.5, height=10, base=[83, 55.5, 9], axis="Y", operation="cut", targets=S, name="ForoBD"),
    cmd("solid.cylinder", diameter=2.5, height=10, base=[-83, 55.5, 9], axis="Y", operation="cut", targets=S, name="ForoBS"),
    cmd("solid.cylinder", diameter=2.5, height=6, base=[83, 59.5, 114.2204], axis="Y", operation="cut", targets=S, name="ForoAD"),
    cmd("solid.cylinder", diameter=2.5, height=6, base=[-83, 59.5, 114.2204], axis="Y", operation="cut", targets=S, name="ForoAS"),
])]
stages["C2"] = [b([
    cmd("sketch.create", plane="XY", offset="122 mm", name="SkFeritoiaSup"),
    cmd("sketch.slot.overall", p0=[-76, 49.5], p1=[-76, 60.5], width=3),
    cmd("sketch.finish"),
    cmd("solid.extrude", distance=5, direction="negative", operation="cut", targets=S, name="FeritoiaSup"),
    cmd("solid.pattern.rectangular", features=["FeritoiaSup"], dir1=[1, 0, 0], count1=20, spacing1=8, name="FeritoieSup"),
])]
stages["C3"] = [b([
    cmd("sketch.create", plane=FACE, name="SkScritta"),
    cmd("sketch.text", text="AGENTS DECK", at=[0, -60], height=6, align="center", letter_spacing=1.5),
    cmd("sketch.finish"),
    cmd("solid.extrude", distance=0.6, direction="negative", operation="cut", targets=S, name="Scritta"),
])]
stages["C4"] = [b([
    cmd("solid.cylinder", diameter=12, height=1.5, base=[x, y, -0.5], operation="cut", targets=S, name=f"Piedino{i+1}")
    for i, (x, y) in enumerate([(72, 12), (-72, 12), (72, 90), (-72, 90)])
])]
cov = [cmd("solid.box", length=180, width=2.5, height=117.7204, center=[0, 66.25, 62.3602], operation="new", body_name="Coperchio", name="Coperchio")]
pi = [(-4, 28.5), (-62, 28.5), (-4, 77.5), (-62, 77.5)]
cov += [cmd("solid.cylinder", diameter=6, height=5.3, base=[x, 60, z], axis="Y", operation="join", targets=C, name=f"ColonninaPi{i+1}") for i, (x, z) in enumerate(pi)]
cov += [cmd("solid.cylinder", diameter=2.2, height=5, base=[x, 59.5, z], axis="Y", operation="cut", targets=C, name=f"ForoPi{i+1}") for i, (x, z) in enumerate(pi)]
stages["D1"] = [b(cov)]
stages["D2"] = [b([
    cmd("solid.fillet", edges=[[90, 66.25, 121.2204], [-90, 66.25, 121.2204]], radius=6, body="Coperchio", name="RaccordiCoperchio"),
])]
stages["D3"] = [b([
    cmd("solid.hole", position=[x, 67.5, z], diameter=3.4, type="countersink", cs_diameter=6.6, cs_angle=90, targets=C, name=f"ViteCop{i+1}")
    for i, (x, z) in enumerate([(83, 9), (-83, 9), (83, 114.2204), (-83, 114.2204)])
])]
stages["D4"] = [b([
    cmd("sketch.create", plane="XZ", offset="68 mm", name="SkFeritoiaCop"),
    cmd("sketch.slot.overall", p0=[-72, -35], p1=[-72, -61], width=4),
    cmd("sketch.finish"),
    cmd("solid.extrude", distance=4, direction="negative", operation="cut", targets=C, name="FeritoiaCop"),
    cmd("solid.pattern.rectangular", features=["FeritoiaCop"], dir1=[1, 0, 0], count1=19, spacing1=8, name="FeritoieCop"),
])]
pil = [cmd("solid.cylinder", diameter=8, height=h, base=[x, y0, z], axis="Y", operation="join", targets=C, name=f"Pilastrino{i+1}")
       for i, (x, y0, z, h) in enumerate([(79, 15, 17.51, 50.3), (-79, 15, 17.51, 50.3), (-79, 46, 102.09, 19.3), (40, 46, 102.09, 19.3)])]
pil += [cmd("sketch.create", plane=FACE, offset="-(lip + stack + 1 mm)", name="SkPunte"),
        cmd("sketch.rectangle.two_point", p0=[-90, -53], p1=[90, -37]),
        cmd("sketch.rectangle.two_point", p0=[-90, 37], p1=[90, 53]),
        cmd("sketch.finish"),
        cmd("solid.extrude", distance=15, direction="positive", operation="cut", targets=C, name="PuntePilastrini")]
stages["D5"] = [b(pil)]

st = sys.argv[1]
calls = [] if st == "A1" else [{"name": "open", "arguments": {"path": D}}]
calls += stages[st]
calls += [{"name": "measure", "arguments": {}}, {"name": "save", "arguments": {"path": D}}]
json.dump(calls, open(f"v2_{st}.json", "w"))
