# lcd-deck

**[Italiano](#italiano) · [English](#english)**

![Deck v4](screenshot-v4/01_deck.png)

---

## Italiano

Supporto da scrivania stampabile in 3D per un display touch HDMI da 7″ 1024×600 (Kuman SC7BC / Elecrow 7″ C) con un Raspberry Pi 4 montato all'interno. Pensato come "deck" sempre acceso accanto al monitor, per un pannello di stato come [agents-deck](https://github.com/ggbeauty989/agents-deck).

Modellato con [SolidCraft](https://github.com/tangency-labs/solidcraft) tramite il suo server MCP.

### Cosa stampare (v4)

| File | Ingombro | Orientamento | Supporti |
|---|---|---|---|
| `deck-v4-scocca.stl` | 180 × 144 × 94 mm | frontale appoggiato sul piano (già orientato) | solo dentro l'apertura dei connettori sul fianco destro |
| `deck-v4-coperchio.stl` | 180 × 126 × 50 mm | faccia esterna sul piano (già orientato) | nessuno |

Consigliati PETG o PLA, strati da 0,2 mm, 3 perimetri, riempimento 15–20 %. Serve un piano da almeno 220 × 220 mm.

### Materiale

- 4 inserti a caldo in ottone **M3 × 4 mm** (diametro esterno 5 mm) nelle torrette del corpo
- 4 inserti a caldo in ottone **M2,5 × 4 mm** (diametro esterno 3,5 mm) nelle colonnine del coperchio
- 4 viti **M3 × 6** a testa svasata per chiudere il coperchio
- 4 viti **M2,5 × 5** per il Raspberry Pi
- 4 gommini o pezzetti di spugna adesiva da 3–5 mm per le punte dei pilastrini
- 4 piedini in gomma adesivi da 12 mm (opzionali, negli incavi sotto la base)
- cavo corto micro-HDMI → HDMI, cavo corto micro-USB per il touch, alimentatore USB-C per il Pi

I diametri dei fori per gli inserti sono parametri del progetto (`foro_inserto_m3` = 4,2 mm, `foro_inserto_m25` = 3,2 mm): se gli inserti entrano troppo duri o troppo lenti si correggono lì.

### Montaggio

1. Scalda e inserisci gli inserti M3 nelle torrette del corpo e gli M2,5 nelle colonnine del coperchio.
2. Inserisci lo schermo nella cornice da dietro: il vetro va nella sua tasca, con i connettori (HDMI, micro-USB, interruttore) sul lato destro guardando il deck da davanti.
3. Avvita il Raspberry Pi sulle colonnine del coperchio, componenti verso lo schermo, con le porte USB/Ethernet verso il fianco sinistro.
4. Collega i cavi: passano tutti dall'apertura laterale destra.
5. Metti i gommini sulle punte dei pilastrini e chiudi il coperchio con le 4 viti M3.

![Schermo e Raspberry Pi nel deck](screenshot-v4/02_trasparente.png)

### Struttura del repository

- `deck-kuman7-pi4-v4.solidcraft`: progetto SolidCraft della versione attuale (parametrico)
- `deck-v4-assieme.step`: assieme corpo + coperchio in STEP
- `deck-v4-scocca.stl`, `deck-v4-coperchio.stl`: file da stampare, già riparati e verificati a tenuta
- `screenshot-v4/`: immagini della v4
- `old/`: versioni precedenti, solo per riferimento (la v4 è quella da stampare)
  - `old/v1/`, `old/v2/`, `old/v3/`: progetto, STEP, STL e immagini di ciascuna versione
  - `old/script/`: gli script che hanno costruito le versioni 2 e 3
- `script/`: script con cui la v4 è stata costruita e verificata
  - `mcpc.py`: client minimo per il server MCP di SolidCraft
  - `v4gen.py` + `v4run.sh` + `pipeline_v4.sh`: ricostruzione, esportazione e controlli della v4
  - `meshfix.py`: ripara i piccoli difetti di tassellazione degli STL esportati e si rifiuta di scrivere un file non a tenuta
  - `overhang.py`, `meshclash.py`, `conndist.py`, `standoffdist.py`, `pidist.py`: controlli di sbalzi, interferenze e spazi
  - gli script contengono ancora i percorsi della macchina su cui sono stati usati

### Modelli di terzi (non inclusi)

Le verifiche di ingombro sono state fatte con due modelli STEP di terzi, che non sono inclusi per motivi di licenza. Si trovano nella libreria GrabCAD:

- Raspberry Pi 4 Model B (`raspberry-pi-4-model-b-1`)
- Elecrow 7inch LCD Display (C) (`elecrow-7inch-lcd-display-c-1`)

Messi in `componenti/` come `raspberry-pi-4.step` ed `elecrow-7lcd-c.step`, permettono di rigenerare l'assieme con i componenti.

### Versioni

- **v1**: prima forma a cuneo inclinato di 20°
- **v2**: pareti più spesse, bordi arrotondati, finestra raccordata
- **v3**: correzioni per la stampa (smussi a 45° sul bordo a contatto col piano, finestre USB separate, rinforzi sotto le torrette)
- **v4**: vano adattato al circuito con linguette dell'Elecrow/Kuman (123 mm), apertura connettori corretta, fori per inserti in ottone, mesh esportata a tenuta

---

## English

A 3D-printable desk stand for a 7″ 1024×600 HDMI touch display (Kuman SC7BC / Elecrow 7″ C) with a Raspberry Pi 4 mounted inside. Meant as an always-on "deck" next to your monitor, for a status board such as [agents-deck](https://github.com/ggbeauty989/agents-deck).

Modelled in [SolidCraft](https://github.com/tangency-labs/solidcraft) through its MCP server.

### What to print (v4)

| File | Size | Orientation | Supports |
|---|---|---|---|
| `deck-v4-scocca.stl` (body) | 180 × 144 × 94 mm | front face on the bed (already oriented) | only inside the connector opening on the right side |
| `deck-v4-coperchio.stl` (back cover) | 180 × 126 × 50 mm | outer face on the bed (already oriented) | none |

PETG or PLA recommended, 0.2 mm layers, 3 perimeters, 15–20 % infill. Needs a bed of at least 220 × 220 mm.

### Parts

- 4 brass heat-set inserts **M3 × 4 mm** (5 mm outer diameter) in the body's screw bosses
- 4 brass heat-set inserts **M2.5 × 4 mm** (3.5 mm outer diameter) in the cover's Pi standoffs
- 4 **M3 × 6** countersunk screws to close the cover
- 4 **M2.5 × 5** screws for the Raspberry Pi
- 4 rubber bumpers or 3–5 mm adhesive foam pads for the tips of the screen pillars
- 4 adhesive 12 mm rubber feet (optional, in the recesses under the base)
- short micro-HDMI → HDMI cable, short micro-USB cable for touch, USB-C power supply for the Pi

The insert hole diameters are design parameters (`foro_inserto_m3` = 4.2 mm, `foro_inserto_m25` = 3.2 mm): if your inserts go in too tight or too loose, adjust them there.

### Assembly

1. Heat-set the M3 inserts into the body's bosses and the M2.5 inserts into the cover's standoffs.
2. Fit the screen into the frame from behind: the glass sits in its pocket, with the connectors (HDMI, micro-USB, switch) on the right side as seen from the front.
3. Screw the Raspberry Pi onto the cover's standoffs, components facing the screen, USB/Ethernet ports towards the left side.
4. Plug in the cables: they all pass through the right-hand side opening.
5. Put the bumpers on the pillar tips and close the cover with the 4 M3 screws.

![Screen and Raspberry Pi inside the deck](screenshot-v4/02_trasparente.png)

### Repository layout

- `deck-kuman7-pi4-v4.solidcraft`: SolidCraft design of the current version (parametric)
- `deck-v4-assieme.step`: body + cover assembly as STEP
- `deck-v4-scocca.stl` (body), `deck-v4-coperchio.stl` (cover): print files, already repaired and checked watertight
- `screenshot-v4/`: images of v4
- `old/`: earlier versions, for reference only (v4 is the one to print)
  - `old/v1/`, `old/v2/`, `old/v3/`: design, STEP, STL and images of each version
  - `old/script/`: the scripts that built versions 2 and 3
- `script/`: scripts that built and checked v4
  - `mcpc.py`: minimal client for the SolidCraft MCP server
  - `v4gen.py` + `v4run.sh` + `pipeline_v4.sh`: rebuild, export and checks of v4
  - `meshfix.py`: repairs the small tessellation defects of exported STLs and refuses to write a file that is not watertight
  - `overhang.py`, `meshclash.py`, `conndist.py`, `standoffdist.py`, `pidist.py`: overhang, interference and clearance checks
  - the scripts still contain paths from the machine they were run on

### Third-party models (not included)

Fit checks were done with two third-party STEP models, which are not included for licensing reasons. They are in the GrabCAD library:

- Raspberry Pi 4 Model B (`raspberry-pi-4-model-b-1`)
- Elecrow 7inch LCD Display (C) (`elecrow-7inch-lcd-display-c-1`)

Placed in `componenti/` as `raspberry-pi-4.step` and `elecrow-7lcd-c.step`, they let you rebuild the assembly with the components.

### Versions

- **v1**: first wedge shape, tilted 20°
- **v2**: thicker walls, rounded edges, rounded screen window
- **v3**: printability fixes (45° chamfers on the edge touching the bed, separate USB windows, gussets under the screw bosses)
- **v4**: cavity resized for the Elecrow/Kuman board with its mounting tabs (123 mm), fixed connector opening, holes for brass inserts, watertight exported mesh
