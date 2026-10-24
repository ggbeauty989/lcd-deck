"""Generate the v6 deck build stages as MCP call lists: python3 v6gen.py <stage> -> v6_<stage>.json"""
import json, sys
D = "/home/roberto/Documenti/SolidCraft/deck-kuman7-pi4-v6.solidcraft"
FACE = {"origin": [0, 24.9675, 68.5976], "x_dir": [1, 0, 0], "y_dir": [0, 0.342020, 0.939693]}
SIDE = {"origin": [96, 24.9675, 68.5976], "x_dir": [0, 0.342020, 0.939693], "y_dir": [0, 0.939693, -0.342020]}
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
        cmd("parameters.add", name="wall", expression="3.5 mm", comment="spessore pareti del corpo"),
    cmd("parameters.add", name="foro_inserto_m3", expression="4.2 mm", comment="foro per inserto a caldo M3x4 diam. est. 5 (4.0-4.4)"),
    cmd("parameters.add", name="foro_inserto_m25", expression="3.2 mm", comment="foro per inserto a caldo M2.5x4 diam. est. 3.5 (3.0-3.4)"),
    cmd("sketch.create", plane="YZ", name="ProfiloCuneo"),
    cmd("sketch.line", points=[[0, 0], [47.0278, 129.2077], [65, 129.2077], [65, 0]], closed=True),
    cmd("sketch.finish"),
    cmd("solid.extrude", distance=180, direction="symmetric", operation="new", body_name="Scocca", name="Cuneo"),
])]
stages["A2"] = [b([
    cmd("solid.fillet", edges=[[90, 56.0139, 129.2077], [-90, 56.0139, 129.2077]], radius=6, name="RaccordiSuperiori"),
])]
stages["A2b"] = [b([
    cmd("solid.chamfer", edges=[[90, 23.5139, 64.6039]], distance=2, name="SmussoFrontale"),
])]
stages["A3"] = [b([
    cmd("solid.shell", faces=[[0, 65, 60]], thickness="wall", direction="inside", name="Svuota"),
    cmd("solid.box", length=180, width=40, height=3.5, center=[0, 80, 1.75], operation="join", targets=S, name="Piede"),
])]
stages["A4"] = [b([
    cmd("solid.fillet", edges=[[90, 100, 1.75], [-90, 100, 1.75]], radius=12, name="RaccordiPiede"),
])]
stages["B1"] = [b([
    cmd("sketch.create", plane=FACE, offset="-3 mm", name="SkAnello1"),
    cmd("sketch.rectangle.two_point", p0=[-88.2, -70], p1=[88.2, 57.6]),
    cmd("sketch.draw.dimensioned", command="sketch.rectangle.center", params={"center": [0, 0], "corner": [82.75, 50.4]}, dimensions={"width": "glass_w + 2*fit", "height": "glass_h + 2*fit"}),
    cmd("sketch.finish"),
    cmd("solid.extrude", distance="pocket_end - 3 mm", direction="negative", operation="join", targets=S, name="AnelloVetro"),
    cmd("sketch.create", plane=FACE, offset="0.5 mm - pocket_end", name="SkAnello2"),
    cmd("sketch.rectangle.two_point", p0=[-88.5, -68], p1=[88.5, 65.5]),
    cmd("sketch.rectangle.two_point", p0=[-84, -65.6], p1=[84, 64.2]),
    cmd("sketch.finish"),
    cmd("solid.extrude", distance="lip + stack - pocket_end + 0.5 mm", direction="negative", operation="join", targets=S, profiles=[{"point": [86, 0]}], name="AnelloCircuito"),
    cmd("sketch.create", plane=FACE, offset="-lip", name="SkTasca"),
    cmd("sketch.rectangle.two_point", p0=[-82.75, -50.4], p1=[82.75, 52.8]),
    cmd("sketch.finish"),
    cmd("solid.extrude", distance="pocket_end - lip + 0.5 mm", direction="negative", operation="cut", targets=S, name="TascaVetro"),
    # the window sits 2 mm above the glass centre: the panel's black border is 4.75 mm on top and 8.7 mm below
    cmd("sketch.create", plane=FACE, offset="1 mm", name="SkFinestra"),
    cmd("sketch.rectangle.rounded", p0=[-78.5, -42.5], p1=[78.5, 46.5], radius=4),
    cmd("sketch.finish"),
    cmd("solid.extrude", distance=4, direction="negative", operation="cut", targets=S, name="FinestraSchermo"),
])]
pads = []
# top tabs: screwed into M2.5 inserts (pad 6.4 mm so the glass can slide up past it during assembly)
for i, (x, y) in enumerate([(78.5, 56.5), (-78.5, 56.5)]):
    pads += [cmd("sketch.create", plane=FACE, offset="-9 mm", name=f"SkBaseSchermo{i+1}"),
             cmd("sketch.circle.center", center=[x, y], radius=3.2),
             cmd("sketch.finish"),
             cmd("solid.extrude", distance=6.5, direction="positive", operation="join", targets=S, name=f"BaseSchermo{i+1}"),
             cmd("sketch.create", plane=FACE, offset="-9 mm", name=f"SkForoSchermo{i+1}"),
             cmd("sketch.circle.center", center=[x, y], radius=1.6),
             cmd("sketch.finish"),
             cmd("solid.extrude", distance=5, direction="positive", operation="cut", targets=S, name=f"ForoSchermo{i+1}")]
# bottom tabs: a plain rest pad in front and a clip behind that overlaps the tab tip by 1.8 mm.
# The clip face sits 0.6 mm behind the board back (lip 2 + stack 9 = 11) and its entry edge has a 0.8 mm
# lead-in, so print sag on that overhang and stack tolerance still let the tab slide under it.
for i, (x, y) in enumerate([(78.5, -58.8), (-78.5, -58.8)]):
    pads += [cmd("sketch.create", plane=FACE, offset="-9 mm", name=f"SkAppoggioSchermo{i+1}"),
             cmd("sketch.circle.center", center=[x, y], radius=3.5),
             cmd("sketch.finish"),
             cmd("solid.extrude", distance=6.5, direction="positive", operation="join", targets=S, name=f"AppoggioSchermo{i+1}"),
             cmd("sketch.create", plane={"origin": [x, 24.9675, 68.5976], "x_dir": [0, 0.342020, 0.939693], "y_dir": [0, 0.939693, -0.342020]}, name=f"SkAggancio{i+1}"),
             cmd("sketch.line", points=[[-66.5, 11.6], [-62.6, 11.6], [-61.8, 12.4], [-61.8, 14.1], [-66.5, 14.1]], closed=True),
             cmd("sketch.finish"),
             cmd("solid.extrude", distance=10.8, direction="symmetric", operation="join", targets=S, name=f"Aggancio{i+1}")]
stages["B1b"] = [b(pads)]
stages["B2"] = [b([
    cmd("solid.chamfer", edges=[[0, 10.4316, 28.6606]], distance=1, name="SmussoFinestra"),
])]
stages["B3"] = [b([
    cmd("sketch.create", plane=SIDE, name="SkConnettori"),
    cmd("sketch.rectangle.rounded", p0=[-12, 3.5], p1=[56, 18], radius=3),
    cmd("sketch.finish"),
    cmd("solid.extrude", distance=13.5, direction="positive", operation="cut", targets=S, name="AperturaConnettori"),
    cmd("sketch.create", plane="YZ", offset="-84 mm", name="SkUSB"),
    cmd("sketch.rectangle.rounded", p0=[40, 26.5], p1=[60, 44], radius=3),
    cmd("sketch.rectangle.rounded", p0=[40, 46], p1=[60, 62], radius=3),
    cmd("sketch.rectangle.rounded", p0=[40, 64], p1=[60, 80], radius=3),
    cmd("sketch.finish"),
    cmd("solid.extrude", distance=10, direction="negative", operation="cut", targets=S, name="AperturaUSB"),
])]
stages["C1"] = [b([
    cmd("solid.box", length=10, width=10, height=10, center=[83, 60, 8], operation="join", targets=S, name="TorrettaBD"),
    cmd("solid.box", length=10, width=10, height=10, center=[-83, 60, 8], operation="join", targets=S, name="TorrettaBS"),
    cmd("solid.box", length=10, width=6, height=9, center=[48, 62, 122.2077], operation="join", targets=S, name="TorrettaAD"),
    cmd("solid.box", length=10, width=6, height=9, center=[-48, 62, 122.2077], operation="join", targets=S, name="TorrettaAS"),
    cmd("solid.cylinder", diameter="foro_inserto_m3", height=6, base=[83, 59.5, 9], axis="Y", operation="cut", targets=S, name="ForoBD"),
    cmd("solid.cylinder", diameter="foro_inserto_m3", height=6, base=[-83, 59.5, 9], axis="Y", operation="cut", targets=S, name="ForoBS"),
    cmd("solid.cylinder", diameter="foro_inserto_m3", height=5.5, base=[48, 60.0, 122.2077], axis="Y", operation="cut", targets=S, name="ForoAD"),
    cmd("solid.cylinder", diameter="foro_inserto_m3", height=5.5, base=[-48, 60.0, 122.2077], axis="Y", operation="cut", targets=S, name="ForoAS"),
])]
gus = []
for x0, nm in ((78, "D"), (-88, "S")):
    gus += [cmd("sketch.create", plane="YZ", offset=f"{x0} mm", name=f"SkRinforzi{nm}"),
            cmd("sketch.line", points=[[56, 3.2], [56, 12.6], [34.4, 3.2]], closed=True),
            cmd("sketch.finish"),
            cmd("solid.extrude", distance=10, direction="positive", operation="join", targets=S, name=f"Rinforzi{nm}")]
stages["C1b"] = [b(gus)]
stages["C2"] = [b([
    cmd("sketch.create", plane="XY", offset="130.0077 mm", name="SkFeritoiaSup"),
    cmd("sketch.slot.overall", p0=[-76, 51.5], p1=[-76, 61.5], width=3),
    cmd("sketch.finish"),
    cmd("solid.extrude", distance=5, direction="negative", operation="cut", targets=S, name="FeritoiaSup"),
    cmd("solid.pattern.rectangular", features=["FeritoiaSup"], dir1=[1, 0, 0], count1=20, spacing1=8, name="FeritoieSup"),
])]
# the engraved front text was dropped: SolidCraft tessellates it with tiny holes in the exported mesh
stages["C4"] = [b([
    cmd("solid.cylinder", diameter=12, height=1.5, base=[x, y, -0.5], operation="cut", targets=S, name=f"Piedino{i+1}")
    for i, (x, y) in enumerate([(72, 12), (-72, 12), (72, 90), (-72, 90)])
])]
cov = [cmd("solid.box", length=180, width=2.5, height=125.7077, center=[0, 66.25, 66.3539], operation="new", body_name="Coperchio", name="Coperchio")]
pi = [(-4, 28.5), (-62, 28.5), (-4, 77.5), (-62, 77.5)]
cov += [cmd("solid.cylinder", diameter=6.4, height=5.3, base=[x, 60, z], axis="Y", operation="join", targets=C, name=f"ColonninaPi{i+1}") for i, (x, z) in enumerate(pi)]
cov += [cmd("solid.cylinder", diameter="foro_inserto_m25", height=5.1, base=[x, 59.9, z], axis="Y", operation="cut", targets=C, name=f"ForoPi{i+1}") for i, (x, z) in enumerate(pi)]
stages["D1"] = [b(cov)]
stages["D2"] = [b([
    cmd("solid.fillet", edges=[[90, 66.25, 129.2077], [-90, 66.25, 129.2077]], radius=6, body="Coperchio", name="RaccordiCoperchio"),
])]
stages["D3"] = [b([
    cmd("solid.hole", position=[x, 67.5, z], diameter=3.4, type="countersink", cs_diameter=6.6, cs_angle=90, targets=C, name=f"ViteCop{i+1}")
    for i, (x, z) in enumerate([(83, 9), (-83, 9), (48, 122.2077), (-48, 122.2077)])
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
        cmd("sketch.rectangle.two_point", p0=[-90, -58], p1=[90, -42]),
        cmd("sketch.rectangle.two_point", p0=[-90, 32], p1=[90, 48]),
        cmd("sketch.finish"),
        cmd("solid.extrude", distance=15, direction="positive", operation="cut", targets=C, name="PuntePilastrini")]
stages["D5"] = [b(pil)]

st = sys.argv[1]
calls = [] if st == "A1" else [{"name": "open", "arguments": {"path": D}}]
calls += stages[st]
calls += [{"name": "measure", "arguments": {}}, {"name": "save", "arguments": {"path": D}}]
json.dump(calls, open(f"v6_{st}.json", "w"))
