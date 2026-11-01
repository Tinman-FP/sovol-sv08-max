# Clean 4040 gantry for the SV08 Max (INDX, 5 tools, Beacon, 12 mm belts) — C3 AWD + top hat

Started 2026-10-30 after the owner rejected the earlier 4040 design. The brief:
* a Voron-2.4 / Printables 1404311 style gantry, 4040 for rigidity;
* Gates 12 mm 2GT belts;
* the INDX Smart Head centred on the X carriage on the 4040 (not hung below);
* light, few parts, clean, as many PPS-CF printed parts as possible;
* double-shear motor shafts;
* five Bondtech docks from the owner's kit;
* Beacon Rev H;
* USB hub and Link Board on the enclosure top cover.

Revisions:
* **C2** (same day) was the 2-motor design.
* **C3** adds all-wheel drive (owner, 2026-10-30): "2 x and 2 Y motors", using the owner's set of four
  LDO 42STH48-2004MAH(S80) motors. It also adds the top hat with the 7 inch display, and the camera on a fixed front-right mount.

**Status: design model (C3). Parts ordered 2026-10-30; nothing printed or installed.**

## Layout (stock-pose frame of Sovol's model; seen from the front, +X is to the left, x<0 is the right)

| Item | Value |
|---|---|
| Motors | 4 x LDO 42STH48-2004MAH(S80), 0.9 deg, 2.0 A, 80 mm shaft. Upper belt: B (rear right) + B2 (front right); lower belt: A (rear left) + A2 (front left) |
| Rear motors | as C2: hang below the rear corners (X +-263, Y -45), 180 deg wrap via a 15 mm reverse idler, 625ZZ above each pulley; printed covers over the long shafts |
| Front motors | replace C2's front idlers: axes X +-314.4, Y 553, faces Z 170, bodies hang below between the side beam end and the Z-carriage arm; 625ZZ above the pulley, closed hood over the shaft |
| Double shear | every motor: pulley between the motor's own front bearing and a 625ZZ above it. Gap from pulley top to 625ZZ: B rear 1.5 mm; A rear 18.5 mm (belt B crosses above that pulley); B2 front 7.5 mm (the joint carriers pass under the cap at docking); A2 front 1.5 mm |
| Belt tension | each front motor sits on a slider (travel -1..+3 mm) clamped by 4x M4 and pulled forward by an M3 x 40 from the front of the dock bracket |
| Side beams | 4040 x 561 (C2: 610.5), ending behind the front motors; a printed cradle ties each beam end to the Z-carriage arm around the motor |
| X beam / rails | 4040 x 556 at Z 157; MGN12 552 (X) and 2 x 555 (Y) |
| Belt length | **2509 mm each** including 22 mm clamp tails, constant over the whole travel (AWD does not shorten the loop) |
| Nozzle | Z 127.0, 6 mm inside the Z carriages' reach to the bed |
| Travel | X -252..+252, Y 64.4..563.5 print, docking to Y 570.6. Front keep-out for the slicer: nozzle Y <= 535.2 between X -238 and +186 (docks and wiper stations, `c3/C3_PURGE_KEEPOUT.json`) |
| Docks | 5 Bondtech 1515 docks at X -203/-125/-47/31/109 (78 mm apart, each tool with its own wiper station; 42 mm apart until 2026-10-31) on a 15x15 rail (588 mm), fronts at Y 619 |
| Purge / wipe | 5 wiper stations, one per tool, 42 mm on the +X side of each dock (X -161/-83/-5/73/151), on a 1515 station bar in front of the PEI edge, below the nozzle tip. Each has a gravity-return slider on two dowel pins with a Qidi Plus 4 silicone wiper pad (27 x 15 x 4.7 mm) and a purge chute; it lifts off the PEI at the first layers. One slide-out purge tray on the chamber floor under all five stations (360 mm long), loose (no fasteners). See "Purge and wipe stations" |
| Beacon | Rev H under the carriage, turned 90 deg, coil 40 mm behind the nozzle |
| Camera | stock camera reused; printed clip over the front profile's inner lip at the front right (between the corner bracket and Sovol's LED bar), aimed at the bed centre |
| Top hat | 195 mm tall on the frame top (Z 591.3; was 136 until 2026-11-01, raised for the piano-wire arcs), 40 mm walls in 8 interlocking printed sections. Its top repeats the frame's 7.5 mm top band, so the owner's Sovol top cover moves up onto it unchanged. iPistBit 7 inch display flush in the front-right corner |
| Tubes and cables | ten micro chains hang in the 14-16 mm gaps beside the side beams (the only space the gantry never sweeps) and carry every tube and cable to the gantry. PTFE: in through couplers on the side panels, up side masts on the side beams, then a piano-wire arc to each tool (Snapmaker U1 style). Head wiring: Link Board on a mast on the rear beam, Link cable and Beacon USB to the head as a piano-wire umbilical (Rat Rig V-Core 4 style). Motor cables in their own chains (`c3_routing.py`). See "Tubes and cables" |
| Clearance | full stock model, 7 XY poses (corners, end docks, nominal): 0 clashes, 0 belt contacts. Whole gantry swept first layer to 500 mm against the frame, camera, top hat and chain anchors: 0 clashes. Camera mount and top hat vs frame: 0 (`c3/C3_CLEARANCE.json`). Chains over Z, harness against the head and the piano-wire arcs: `c3/C3_ROUTE_CHECK.json` |

### Why it looks the way it does (C3 additions)
* **Front motor placement.** The front 180 deg turn is directly above the side beam, so a front motor there can only hang below if the side beam stops short of it.
  * Body-up does not fit: at full Z it would hit the front corner brackets of the stock top frame.
  * Inboard positions are swept by the Smart Head at the front corners.
  * The beam therefore ends at Y 529, and a U-shaped cradle carries the load from the beam end to the stock arm.
* **Slider plate height.** At the docking pose the joint pulley carriers pass 2.5 mm over the slider plate. The cap and 625ZZ sit just above the carriers' top. A notch lets the X carriage's wing pass at the front-corner travel limits.
* **Shaft length.** The S80 shafts reach Z 250 (front) and 257-259 (rear).
  * The front hoods stay below the frame top at full Z.
  * The rear covers rise about 4-6 mm above it, inside the frame opening. The top hat ribs are cut back at 45 deg from 7.5 to 40 mm, so anything up to about 20 mm above the frame near the walls clears.
  * Cutting the shafts to 55 mm and leaving the covers off also works.
* **Top hat height.** The INDX head top reaches Z 587 at 500 mm print height. The piano-wire arcs rise to about Z 770 there, so the top hat is 195 mm tall (top Z 786.3).

### Found by the SolidCraft cross-check
The X carriage's under-beam arm and the Beacon reached the XY joint plate's lower flange in the last 4-6 mm of X travel on each side, by up to 390 mm³ at X +252. This came over from C2: the FreeCAD check never compared the head with the parts that move with the X beam.
* **Fix:** the lower flange now stops at Y_XB+3, behind the carriage's under-beam parts, and keeps one bottom M5. The two top M5s and the Y-block bolts are unchanged.
* **Check:** `c3_check.py` now also checks the head against the X beam and joints.

### Removed stock parts
* The drag chain plate.
* The camera bracket on the old gantry.
* The stock filament guide and PU-4 fittings on the right top rail. The INDX PTFE tubes come in through the side panels.
* Sovol's spool holder on the right side (2026-10-31): a filament box feeds the tubes.

## Printed parts
Qidi Plus 4, 0.6 mm nozzle. **Tinman project with every PPS-CF part laid out: `c3/C3_PPS-CF_Qidi_Plus4_0.6mm.3mf`** (see "Tinman print project" below).
* **Supports needed:** Tinman's slice check flags 16 parts, so they have tree supports in the project. The earlier "support-free" note was wrong for most of them.
  * camera mount;
  * wiper sliders;
  * front cradles;
  * rear bearing caps;
  * X carriage;
  * XY pulley carriers;
  * rear mast (umbilical channel), harness rear post, chain entry plates (angled coupler bosses);
  * Z tensioner seats.
* **Purge tray:** it prints rim-down, diagonally on its own plate (360 mm is longer than the Qidi bed). Floor-down, their floor would start on the feet in mid-air.
* **PPS-CF:**
  * X carriage;
  * XY joint plate x2 and pulley carrier x2;
  * rear motor mount x2, bearing cap x2 and shaft cover x2;
  * front base x2, cradle x2 and motor slider x2;
  * camera mount;
  * routing: rear mast (with the Link Board plate), side mast right and left, umbilical head saddle, chain brackets (ptfe right x3, ptfe left x2, motor right x2, motor left, power left, USB), chain anchors and entry plates (ptfe right x3, ptfe left x2, cable right x2, cable left x3), harness side post left x2, harness rear post left;
  * purge and wipe: station bar clip x2, wiper station bracket x5 and slider x5 (one print file each), and one 360 mm purge tray that prints diagonally.
  * About 2.1 kg at solid volume (`c3/C3_BOM.md`).
* **ASA:** top hat, 4 corner pieces + 4 straights, each ≤ 289 mm long and 195 mm tall, printed upright.

Masses are in `c3/C3_BOM.md`.

## Tinman print project (PPS-CF, Qidi Plus 4, 0.6 mm nozzle)
`c3/C3_PPS-CF_Qidi_Plus4_0.6mm.3mf`:
* **Contents:** all 88 PPS-CF parts. That is the 68 C3 parts (five each of the wiper bracket and slider; three and two of each mirrored chain fitting; the 360 mm tray alone on the last plate, diagonally), plus the Z kit at 2 of each variant file, in their print orientation.
* **Presets:**
  * printer: Qidi X-Plus 4 0.6 nozzle - TinMan Codex;
  * filament: PPS-CF Codex-Bambu - Qidi X-Plus 4 (320 °C nozzle, 110 °C bed, 65 °C chamber);
  * process: 0.24mm Tank (6 walls, 45 % infill, 8 top and bottom layers);
  * plate: Textured PEI.
* **Layout:** one plate per subsystem, 20 mm between parts (your Tinman arrange setting), clear of the Qidi's excluded bed areas. Every part is named after its print file.
* **Check:** the Tinman CLI slices all eight plates with no warnings (2026-11-01). Supports are on for the 36 parts that need them. The chain entries print standing: laid flat, their coupler bosses made the tree supports fail. The release now drops each part onto the bed by its exact lowest point: the camera mount's published files had floated 3.5 mm.

| Plate | Parts | Time | PPS-CF |
|---|---|---|---|
| 1 Gantry A | 11 | 21.3 h | 422 g |
| 2 Gantry B | 6 | 10.1 h | 195 g |
| 3 Z upgrade 12 mm | 20 | 12.9 h | 209 g |
| 4 Purge and wipe | 12 | 4.3 h | 72 g |
| 5 Camera, masts and harness A | 3 | 36.5 h | 695 g |
| 6 Camera, masts and harness B | 5 | 15.3 h | 268 g |
| 7 Cable chain fittings | 30 | 17.0 h | 314 g |
| 8 Purge tray (diagonal) | 1 | 3.1 h | 60 g |
| **Total** | **88** | **120.4 h** | **2236 g** |

The eight ASA top-hat sections are not in this PPS-CF project.

## Full printer model, colour-coded
`c3/SV08_MAX_C3_MODIFIED.step` (and `.solidcraft`) is Sovol's "SV08 Max Unmodified" model with C3 applied.
* **Removed:** Sovol's parts that leave or are replaced.
* **Added:** every new part, with the gantry at the middle of its travel. Each part is named, with what to do with it in brackets, e.g. `x beam 4040 556 [machine: cut to 556]`.
* **Colours (by top-level component):**
  * red: print in PPS-CF;
  * orange: print in ASA (top hat);
  * yellow: buy (or already owned);
  * green: machine. That means the 4040, 1515 and 2020 extrusions cut to length (the dock rail's ends tapped M3) and the Z drive pulleys faced down to 12.6 mm or less.
  * Sovol's parts keep their own look; the stock camera sits on its new mount.
* **Source of truth:** `c3_fullmodel.py` writes one STEP per category to `c3/full/`, and `c3_fullmodel_color.json` (SolidCraft) colours and combines them. Sovol's original STEP is unchanged.

## Assembly guide
`c3/SV08_MAX_C3_ASSEMBLY_GUIDE.pdf` (24 pages, updated 2026-10-31 for the Qidi pad) covers:
* preparing the parts: prints, heat-set inserts, cut list and Z pulleys;
* stripping the stock gantry;
* assembly in order: the 12 mm Z upgrade, rear corners, side beams and front corners, X beam and carriage, the AWD belt routing, docks, wiper stations, top hat;
* wiring, firmware and slicer notes;
* commissioning checks;
* appendices: the parts lists and the screws for each joint.

Its renders use the same colours as the full model (red print, yellow buy, green machine, orange ASA).

**BOM fixes made while writing it** (`c3/C3_BOM.md`, `c3_release.py`):
* added the MGN12 rail screws and T-nuts (M3 x 10 + slot-8 T-nuts, 66 each);
* added the four M3 x 16 that hold the Smart Head;
* added four M5 sleeves for the XY-joint idlers;
* corrected the M5 slot-8 T-nuts to 28 and the M5 x 10 beam screws to 22;
* removed "tensioner seats" from the Z BOM's reused list, since the printed seats replace them.

## Klipper config (BTT Kraken, INDX, Beacon)
`klipper_c3/` (2026-10-30, not installed): the full mainline Klipper config (no Sovol firmware), KlipperScreen and Orca machine G-code. `klipper_c3/PIN_ASSIGNMENTS.md` maps every stock SV08 Max function, including the chamber heater, to the Kraken, the INDX Smart Head or the host. `klipper_c3/README.md` has the bring-up order and the items to decide before power-up.
* **Kraken drivers:** S1-S4 drive the AWD X/X1/Y/Y1 motors, S5-S8 the four Z motors, all on the HV motor input.
* **Smart Head:** carries the extruder, nozzle heat, part fan, accelerometer, load cell and the X endstop.
* **Chamber heater:** stays on Sovol's controller (mains module, switched inside it), on the Kraken's CAN bus. Motor supply 48 V.
* **Homing:** X and Y sensorless (owner, 2026-10-30), Z by Beacon contact inside Bondtech's homing sequence. Per-tool Z offsets also come from Beacon contact.
* **Hard stops (`c3_stopsweep.py`, `c3/C3_HARD_STOP_SWEEP.json`):**
  * **X** stops where the X carriage meets the joint pulley carrier, 1.0-1.25 mm past travel.
  * **Y (rear)** stops on the **rear Y stop pads** (`Y_STOP_PAD = 1.25` in `c3_params.py`; `rear_corner()` in `c3_build.py`). Each is a 9 x 7 mm pad on the front edge of a rear-corner motor plate, at |X| 277-286.
    * The joint plates land on them 0.5 mm past travel.
    * Without them, the plates met the motor plates at 1.75 mm and the X beam reached the motor cans 0.25 mm later.
  * Re-checked with the pads (2026-10-30): `c3_check.py` gives 0 at all 7 poses, over the Z sweep and for the enclosure. The stop sweep puts first Y contact at 0.5 mm, with the beam clear until at least 1.75 mm.
  * Print files, the Tinman project (re-sliced: 62.4 h, 1167.6 g, same as before), the coloured model and the assembly guide are updated.
* **START_PRINT:** the stock machine's bed-first, mesh-stability heat soak and contact-gate contract, with the chamber HVAC logic ported over.
* **Offline check (`klipper_c3/tools/check_config.py`):** options against the Kalico and Beacon sources, pins, 155 templates and 16 behaviour cases. All pass.

## Files
* `c3_params.py` – every dimension and the CoreXY belt-path solver (AWD: the front motors replace the front idlers).
* `c3_build.py` – builds the model. Writes `c3/C3_GANTRY.FCStd` and `c3/C3_GANTRY.step` (every new and bought part).
* `c3_enclosure.py` – camera mount and top hat (with the display bay and the rear-wall PG9 gland).
* `c3_check.py` – clearance against the full stock printer (`c3/C3_CLEARANCE.json`). The wiper sliders lift, so its plain Z sweep leaves them to `c3_purgecheck.py`.
* `c3_purge.py` – wiper stations, station bar and clips, purge trays. `c3_purgecheck.py` checks them (`c3/C3_PURGE_CLEARANCE.json`); with `C3_KEEPOUT=1` it maps the front keep-out for the slicer (`c3/C3_PURGE_KEEPOUT.json`).
* `c3_release.py` – per-part STEP/STL in print orientation and the BOM (`c3/C3_BOM.md`).
* `c3_routing.py` – cable chains, chain anchors and brackets, side masts, rear mast with the Link Board, harness and piano-wire arcs; `c3_elastica.py` solves the arc shapes; `c3_routecheck.py` checks the chains over Z, the harness against the head and the arcs at every head position (`c3/C3_ROUTE_CHECK.json`).
* `c3_lanecheck.py` – how close a dock or a wiper station may sit beside a lane the head drives into (`c3/C3_LANE_SPACING.json`); it sets the 78 mm dock row.
* `c3_idlercheck.py` – the ordered Gates 12 mm smooth idler on the reverse-idler axles, and the M5 spacer lengths for every rear idler (`c3/C3_SMOOTH_IDLER_CHECK.json`). Pass the measured smooth idler width to recompute: `python3 c3_idlercheck.py 16`.
* `c3/C3_SOURCING.md` – example sources (US sellers, 2026-10-30) for every part to buy, with notes on preparing each one.
* The C2 (2-motor) files are not published here.

## Z upgrade: 12 mm belts and 17HM19-2004S1 (C3-Z, designed 2026-10-30)
The four Z corners are mirror images about X 0 and Y 273.5. Sovol's Z drive per corner, kept unless noted:
* the motor lies along +Y under the base and drives a 12T pulley;
* a 6 mm GT2 186 mm loop turns an ~80T reduction pulley on a stepped cross shaft (5 mm at two 625ZZ, 6 mm under the pulleys, 7 mm collar between them);
* a 20T drive pulley on that shaft drives the belt up the tower to a spring-tensioned 20T idler;
* the belt is clamped on the Z carriage, which carries our gantry arm.

**New parts (`c3_zdrive.py`), per corner:**
| Part | What changed |
|---|---|
| Z carriage plate (printed) | Replaces Sovol's "ab 2" seat with the same MGW9H block screws (4x M3, counterbored) and arm screws (2x M3 x 20, now into heat-set inserts). It has a 12 mm free-run window and a toothed clamp channel that holds both belt ends (teeth toward the pulley axis), 9 teeth each. |
| Belt clamp cover (printed) | Closes the channel; one M3 x 10 between the belt ends, a tongue in the gap stops it turning. Sovol's side screws would pass through a 12 mm belt. |
| Tensioner block (printed) | Sovol's block with the idler gap widened from 13.5 to 17.1 mm; Sovol's 5 mm shaft, springs and tension screw are reused. |
| Tensioner seat (printed) | Sovol's seat with 13 mm slots for both belt runs. Sovol's model shows no belt slots, so the real ones may only fit 9-10 mm; it bolts to the tower as before. |
| 20T idler, 12 mm (bought) | KB3D G2GT-I-20-12 class, 5 mm bore, no more than 16.4 mm wide, **flanges no more than 16 mm across** (the seat's side walls are 8.5 mm from the axis; Sovol's idler is 15 mm). SolidCraft caught a 17 mm flange touching the seat. |
| Drive pulley, 12 mm (custom) | Only 12.8 mm is free between the shaft collar (Y 598.4) and the bottom bracket's front wall (Y 611.2). It must be 20T, 6 mm bore, hubless and flangeless, no more than 12.6 mm long, with an M3 grub through the teeth like Sovol's. No catalogue part fits; see "Drive pulley" below. The flanged top idler and the fixed clamp keep the belt tracking. |
| Motor | 17HM19-2004S1 (48 mm) on Sovol's bracket and 12T pulley; the extra 8 mm of body is clear. |
| Motor end support (printed, optional) | A bridge carrying an MR105ZZ (5 x 10 x 4) 0.5 mm past the 12T pulley, on the motor's two +X screws (M3 x 30), inside the bracket walls. The 24 mm shaft gives the MR105ZZ full engagement with about 0.2 mm spare. If the real shaft measures 26 mm from the face, a 625ZZ fits instead. |

**Drive pulley, two ways to get it:**
* **Buy:** a 20T 2GT pulley for 12 mm belt, 6 mm bore, hubless and flangeless, cut to 12.6 mm, with an M3 set screw through a tooth root (Misumi and similar can configure this).
* **Make:** a standard 20T 12 mm pulley with its hub and flanges faced off, bored to 6 mm, and an M3 hole tapped through a tooth root.

Klipper: `full_steps_per_rotation: 400` on the four Z steppers (0.9 deg); `rotation_distance` is unchanged (same 20T pulley and reduction).
The gantry's Z-belt notches widen by 1.5 mm each side: rear motor mounts and caps Y -64.5..-50.5, front bases Y 597.5..611.5.

**Belts:** 4 x 1.5 m (1.6 m for margin) of Gates 2MGT 12 mm. Each loop is 1425 mm around the two 20T wheels, plus about 30 mm for the clamp ends.

**Clearance (`c3_zcheck.py`, `c3/C3_Z_CLEARANCE.json`):** against the full stock model with the replaced stock parts removed, and against the C3 gantry.
* **Static fit at the stock pose:** 0 clashes. Our tensioner seat and block are Sovol's bodies with slots cut, so they keep 28 small contacts Sovol's own model already has (springs, screws, idler shaft, top frame seat). Those are reported separately with the stock value.
* **Belt runs vs everything:** 0.
* **Carriage parts swept from the first layer to 500 mm:** 0.
* **Whole gantry swept past the 12 mm belts and the new fixed parts:** 0.
* **New Z parts against each other:** 0.
* **SolidCraft interference on the front-right corner** (independent of FreeCAD): 0, after it caught the idler flange.
* **Fixes the check found:** the bottom bracket wall at Y 611.2 (pulley limit 12.6 mm); the end-support legs moved to Y 582; the arm insert holes deepened for the M3 x 20 tips; and Sovol's seat had no belt slots in the model, hence the printed seat.

**Files:**
* `c3_zdrive.py` (parts), `c3_zcheck.py` (clearance), `c3_zrelease.py` (print files and BOM).
* `c3/print/Z_*_A/B_PPS-CF.stl|step`: variant A is front right + rear left, variant B is front left + rear right; print two of each.
* `c3/C3_Z_BOM.md`.

## Tubes and cables: side chains, masts and piano-wire arcs (C3-R, 2026-11-01)
Owner's direction: head wiring from the back middle on a piano-wire umbilical (Rat Rig V-Core 4 IDEX), motor wiring from the bottom in the smallest chain per motor, PTFE tubes in from the sides at about 250-300 mm print height and over the top of each tool on piano wire (Snapmaker U1), no tube sliding in and out of the chamber. It replaces the weighted PTFE loops of 2026-10-31.

**What the space allows (measured):**
* Over its 500 mm of Z the gantry sweeps the whole inside of the frame except a 14-16 mm gap between each side beam (outer face |X| 338) and the frame face (|X| 354.5), from Y 97 to 450. The back is full: with the bridge at its rearmost the X beam comes within 4 mm of the rear beam (Sovol's own Z chain sat where the C3 rear beam now runs). The front is full too: the docks reach the frame face.
* So nothing can hang behind the bed; every tube and cable reaches the gantry through a chain in one of the side gaps.
* The U1 and the Rat Rig move their beds, so their arcs only have to follow XY. Here the chains take the Z travel and the arcs ride on the gantry.

**Layout (`c3_routing.py`):**
* **Chains:** micro chains, 7 x 7 mm inside and no more than 11.5 mm wide outside, one tube or cable bundle each, hanging in the side gaps (plane |X| 346.25, 2.75 mm from the beam and from the frame face). Right, from the rear: rear motor, T2, T1, T0, front motor. Left: rear motor with the Link Board's 24 V pair, two USB cables (Link Board and Beacon), T4, T3, front motor. PTFE chains bend at 28 mm, cable chains at 18 mm.
  * Fixed ends: on the side panel at frame Z 252 (print Z 288), each through-bolted to an entry plate outside. PTFE comes in through a PC4-M10 coupler on that plate, crossing the panel 30 deg from vertical (about print Z 330); cables come up the outside from the electronics.
  * Moving ends: brackets on the side beam's top outer slot. The U hangs below and moves half as far as the gantry; at the first layer it stays 5 mm above Sovol's carry handles.
* **Side masts (PTFE):** each tube leaves its chain in one S-bend out of the gap (radius about 66 mm; inboard of the side top rail by the time the gantry is at full height, and above the belt and the XY joint carrier), rises in a mast at |X| 306 standing on two arms from the side beam, and turns 155 deg (35 mm) to leave 65 deg down, heading 30 deg forward of inboard, on its own 0.8 mm piano wire. Leaving straight inboard, a parked tube's spare length looped into the middle and met the other side's tubes; angled 60 deg forward it looped into the top hat's front wall. At 30 deg the parked tubes stay apart and every arc clears the top hat. Its tool's tube is tied to the wire down to about 12 mm above the inlet.
* **Rear mast (head wiring):** on the middle of the rear beam. The Link Board sits on its plate (the board's size is not published: the plate takes up to 110 x 60 mm). The INDX Link cable and the Beacon USB leave it in loom on a 1.5 mm piano wire, 70 deg down (at 50 deg its loop rose above the top hat with the head at the rear centre), to a saddle that clips over the INDX PCB cover at the head's centre, as on the Rat Rig. Its lips stop above the XY joints, so the head still reaches both ends of X; a clamp on the side of the X carriage did not. The Link Board's power and USB cables run from the left chains along the left side beam (two posts), over the rear corner (one post) to the board.
* **Arcs:** each solved as an elastic rod of fixed length, both ends clamped, under its own weight (`c3_elastica.py`). Free lengths: T0 627, T1 633, T2 676, T3 617, T4 644 mm (the farthest reach plus 8 %; longer, a parked tube loops into the top hat's front wall); umbilical 635 mm (plus 10 %). Parked tools' tubes come down into them from above; the active tool's tube follows the head.
* **Top hat:** 195 mm tall (was 136) for the arcs at full height. The end ribs at the eight joints are now cut back at 45 deg like the other ribs: at full height the left USB line, rising out of its chain, clipped the full-depth end rib at the rear-left joint.
* **Removed:** the loop heads, weight towers and sleds, the dock guides and their bar and hanger, the cable loop, the 2020 spine and its saddles, the drop ring, and the Link Board / USB hub tray. (The four-loop "4th PTFE" on the right was the Link + Beacon cable loop.)

**Friction (the reason for the side masts):** a tube turns through 32 deg at its entry, 180 in its chain, 228 in its side mast and 160-340 in its arc (depending on where the head is): 600-780 deg. By the capstan rule with mu about 0.15 that is 5-8 times the spool's own drag at the extruder. Sending the tubes to one mast at the back as well would have added about 200 deg (8-12 times). The loops of 2026-10-31 were lower, about 450-500 deg, but their sleds could not bend the tubes (see the 2026-11-01 entry). Use free-running spools, or a filament box with its own feeder, and test one full path with the stiffest filament first.

**Checks:**
* `c3_check.py`: 0 clashes at the 7 poses, 0 belt contacts, 0 over the whole Z sweep and for the enclosure, with every chain anchor, bracket, mast, post and harness line in.
* `c3_routecheck.py` (`c3/C3_ROUTE_CHECK.json`):
  * chains at 13 gantry heights from the first layer to 500 mm, with the bridge at the rear, middle and docking position: 0 clashes;
  * harness, masts, brackets and the Link Board against the head and bridge at 25 head positions: 0;
  * arcs, for each tool on the head in turn at 12 bed positions and its own docking pose (65 cases): 0 contacts with the gantry, the parked tools or the head, and 0 with the top hat or frame at 500 mm print height. The highest arc reaches Z 750 there; the top hat's top is Z 786.3.
  * Tube on tube: three pairs of parked tubes rest lightly against each other (T0-T1, T1-T3, T2-T3, up to 2.7 mm into the 4.4 mm envelope); they do not move against each other. The moving arcs (the active tube and the umbilical) brush another arc in 61 of the 585 checked pairs (about 10 %).
* Found and fixed on the way: the umbilical's first clamp, on the side of the X carriage, hit the XY joint at X +252 (now the saddle on the PCB cover); a full-depth top hat end rib clipped the left USB line at full height (end ribs now cut back at 45 deg); at 50 deg the umbilical's loop rose above the top hat with the head at the rear centre (now 70 deg); parked tubes leaving straight inboard met in the middle, and at 60 deg forward they hit the top hat's front wall (now 30 deg).

## Purge and wipe stations (C3-P, designed 2026-10-30)
The owner's brief:
* a robust wiper like the Qidi Plus 4's, near the tools;
* a prime tower for colour changes;
* a bucket between the bed and the door, well below the gantry, that slides out the front;
* only the filament-load purge goes in the bucket;
* no notch in the PEI sheet.

**What limits it (measured in Sovol's model and the C3 build):**
* The PEI sheet's front edge is at Y 572 across the middle (X -198..188), 6 mm past the steel plate. Two corner tabs, about 60 mm wide, reach Y 584.
* The nozzle's furthest forward point is Y 571.0, set by the Y rail end at the docking pose. It never gets past the sheet edge, so the wiper and the purge catcher have to sit over the sheet's front lip and ride on the gantry.
* The parked tools hang 2 mm above the active nozzle, 2.2 mm above the sheet at the first layer.
* The head's front body reaches 48 mm ahead of the nozzle and cannot pass a parked tool. The front strip of the bed in the dock lanes was already out of reach for printing.

**Design (`c3_purge.py`):**
* **Docks (changed 2026-10-31, owner: each tool with its own wiper and purge tray):** 78 mm apart, at X -203/-125/-47/31/109. The row runs dock, station, dock, station: each station is 42 mm on the +X side of its tool's dock and 36 mm from the next dock.
  * Measured with a surface-sampled sweep of the head driving into a lane (`c3_lanecheck.py`, `c3/C3_LANE_SPACING.json`): the head needs 34.1 mm (+X) / 40.2 mm (-X) from a dock with its parked tool, and 35.0 / 32.4 mm from a slider lifted for the first layer. A parked tool needs 21.4 mm from a lifted slider. So the old 71 mm between the end docks and the stations was far more than needed.
  * The stations' brackets must stay inside the sheet's middle zone (X -198..188); the row leaves 7 mm at each end.
  * This way round (docks on the -X side of their stations) the slicer's front strip is 424 mm wide; the other way round it would be 450 mm.
* **Five stations:** at X -161/-83/-5/73/151, one per tool. Each tool wipes, purges and loads filament only at its own station. Wipe strokes step 8 mm toward the tool's own dock, which is empty while its tool wipes, never toward the next dock 36 mm away. Until 2026-10-31 there were two stations, at X -160 and +150, shared by all five tools.
* **Station bar:** a 1515 x 566 mm bar runs in front of the PEI edge (Y 586..601) and below the nozzle tip (Z tip-13..tip+2), under the head's lowest parts. A printed clip at each end holds it on the front cradle's inner web, with 2 countersunk M3 into short inserts. The cradles gain those 4 insert pockets and nothing else.
* **Station bracket (fixed):** a back plate on the bar's rear slot (2 x M3 + T-nuts), with top and bottom lugs holding two 3 x 20 mm dowel pins. Everything stays at Y >= 575, in front of the sheet edge.
* **Station slider (moving):**
  * It rides on the pins and carries the pad pocket and the chute.
  * It rests on two M3 set screws in the bottom lugs, which set the pad height.
  * When the gantry comes within about 9 mm of the bed, its foot (under the pad, over the supported part of the sheet, not the 6 mm lip) sets down on the PEI, and the slider rides up the pins.
  * Lift needed: up to 9.6 mm at the lowest sweep step. Travel: 10.8 mm. No springs, nothing driven.
* **Wiper pad:** Qidi's silicone nozzle wiper for the Plus 4 and Q2 (sold as "Plus4 Wiper Silicone Case", 5 pack). It measures 27 x 15 x 4.7 mm high (owner's measurement, 2026-10-31).
  * It lies 27 mm across X, so the nozzle crosses its 15 mm on each stroke. Glue it into the pocket with high-temperature red RTV. Three key holes in the pocket floor hold the RTV, and 2.5 mm of the pad sits inside the pocket walls.
  * Its top stands 1.2 mm above the nozzle tip, as on the Qidi. The pocket floor is 3.5 mm below the tip.
  * It replaces the 30 x 12.7 x 3.2 mm pad cut from McMaster-Carr 1462N14 strip (2026-10-31). The pocket is now 2.3 mm longer toward the bed and 1.5 mm deeper, and the wipe ends at Y 548.7 instead of 551.
  * Qidi publishes no temperature rating for it. The nozzle runs hot for PPS-CF, as on Qidi's own printers, and contact lasts a fraction of a second per stroke. Replace the pad when it hardens or tears.
* **Purge chute:** the nozzle purges at Y 571, 4 mm in front of the pad. The strand drops 7 mm onto the chute floor, which carries it past the PEI edge and drops it from Y 577 into the tray below.
* **Purge tray (2026-10-31, owner):** one printed tray, 360 x 46 x 12 mm, about 140 cm3, on the chamber floor in front of the bed, under all five stations (X -185..175). It replaces five 48 mm trays and keeps their height and depth.
  * The owner asked about a rim 0.5 mm below the build plate's underside (Z -47.2). At the first layer the station brackets come down to Z -56.5 over the tray, 9.3 mm below that, so the rim stays at Z -57.0.
  * Each rim is 1 mm below the lowest gantry part over it at the first layer.
  * 20 small feet, where the five single trays had theirs, keep it off the floor's screw heads. The bed's front cover plates stop it at the back. Two pull tabs.
  * No fasteners: it sits loose on its feet. Open the door and slide it straight out to empty it. Nothing in Sovol's model stands in front of them at tray height (the bottom front profile tops out at Z -71.7, under the 1 mm floor sheet).

**Checks (`c3_purgecheck.py`, `c3/C3_PURGE_CLEARANCE.json`), all 0:**

| Check | Result |
|---|---|
| Lift sweep, first layer to 500 mm (5 mm steps): the lifted slider and pad vs the frame and trays; the fixed bar, clips, brackets and pins vs the frame and trays | 0; lift 9.6 mm max of 10.8 |
| Head and bridge vs every gantry part at every station (purge position), mid-wipe (centre and 8 mm toward the own dock), wipe end | 0; only the nozzle touches the pad, 4.15 mm3 mid-stroke and none at the wipe end |
| Sliders lifted as at the first layer vs the head docking at all 5 docks and at both front print corners | 0 |
| Trays, bar, clips, brackets vs the stock printer | 0 |
| SolidCraft clearance at the right station's purge pose (68 bodies, independent of FreeCAD) | no overlap involving a purge part; the head stays more than 1 mm from them. Nearest designed gaps: slider to pins 0.15 mm, slider to bracket 0.2 mm |
| `c3_check.py` with the purge parts in (7 poses, Z sweep, frame-fixed parts) | 0 |

Re-run with five stations and the 78 mm dock row (2026-10-31): the FreeCAD rows above are all 0 (27 head poses; lift 9.6 mm of 10.8; trays and purge parts vs the stock printer 0). SolidCraft (independent of FreeCAD) at station 1's purge pose and with the head docking at dock 1 beside lifted sliders: no overlap involving a purge part, and the head touches no parked tool except the one it is docking.

Re-run with the Qidi pad and the new slider pocket (2026-10-31): every row above is still 0, with the lift at 9.6 mm of 10.8. SolidCraft at the left station's purge and mid-wipe poses agrees: no overlap involving a purge part except the nozzle in the pad (4.11 mm3 mid-wipe), and the same designed gaps.

**Front keep-out for the slicer (`C3_KEEPOUT=1`, `c3/C3_PURGE_KEEPOUT.json`):**
* For each nozzle X, the check found the furthest-forward nozzle Y at which the head clears the docks, parked tools, stations and front corners. It compares the head's front-most and the parts' rear-most surface points per 1 mm column, widened by one column, minus 0.5 mm.
* **Docks alone:** nozzle Y <= 545.4 in the dock lanes, between X -236 and +142. That is 26.6 mm of the PEI's front.
* **Wiper stations at rest:** nozzle Y <= 548.3 in their lanes.
* **Stations lifted (first ~9 mm of a print):** nozzle Y <= 535.2 across the row, X -188..178, easing to the edges at X -236 and 184. The back of the lifted slider sets it, so the Qidi pad (2026-10-31) moved it 2.3 mm back from 537.5.
* **Slicer bed shape, one rule for all heights:** leave out nozzle Y > 535.2 between X -238 and +186. That is the front 37 mm of the sheet across 424 mm (380 mm with the two shared stations, 35 mm deep before the Qidi pad). The +X front corner keeps the full depth to Y 563.5..571; the -X corner keeps only X -252..-238.

**Firmware rules (for the INDX macros; nothing installed):**
* Approach a station like a dock: travel in X with the nozzle at Y <= 533 (behind every keep-out), then go straight forward in the station lane.
* Wipe: forward to Y 571 and back to Y 548.7 across the pad (3.5 mm past it), two or three strokes, alternating between the station centre and 8 mm toward the tool's own dock.
* Skip station wipes below Z 12 mm: the sliders are lifted there. The prime tower covers those layers.
* Filament load: raise to Z >= 30, go to the tool's own station, purge at Y 571, wait a few seconds, then wipe on the way back.

## Open items
1. **Belts: ordered** (owner, 2026-10-30): Gates 2MGT 12 mm, gantry 2 x 2600 mm (each belt needs 2509 mm, 2504 mm with the Gates smooth idlers) and Z 4 x 1600 mm (each loop needs about 1455 mm).
2. **Parts: nothing left to buy** (owner, 2026-10-30). 24 items ordered, 8 more picked to close the gaps, everything else in stock; sources in `c3/C3_SOURCING.md`.
   * Extrusion and MGN12 rails come as stock lengths to cut. The MGN12 rails are generic 600 mm: cut half off each end so 22 holes stay at 13-15 mm from the ends.
   * Smooth idlers: Gates 2GT 12 mm (12 mm belt surface, not the 15 mm the axles were laid out for). `c3_idlercheck.py` shows the moving runs and kinematics are unchanged. The fixed runs beside each reverse idler tilt 1.2° and 4.4°, wraps stay at 174° or more, and each belt is 4.6 mm shorter. No part changes; measure its width for the spacer lengths.
   * Wiper pads: Qidi Plus 4 silicone wipers, 27 x 15 x 4.7 mm (owner, 2026-10-31). They replace pads cut from silicone strip.
   * Second round: the screws the kits leave out (M3x10, M3x40, M4x18, M4x35, an M5 kit for x12/x20, M3x8 countersunk), short M3 inserts and four generic 20T 6 mm-bore pulleys for 15 mm belt to rework into the Z drive pulleys (item 5).
   * In stock (owner): the Pi (model not yet given) and its cooler, card, 5 V supply and cables, the Kraken fan, RTV and PC4-M10 couplers. The routing of 2026-11-01 adds ten micro chains, piano wire, loom, two thin USB cables and an 18 AWG pair (`c3/C3_SOURCING.md`).
3. **Sovol top cover:** it is not in Sovol's CAD model. The top hat repeats the frame's top band, but the cover's real outline needs confirming. Measure its outer size and thickness, and note what it rests on and any pins, screws or hinges.
4. **Display:** iPistBit 7 inch (owner's Amazon link B0CRRB1GFN). The bay is 165.5 x 125 x 17 mm from listings (about 165 x 125 x 15). Check it against the real module.
5. **Z drive pulleys:** four 20T 12 mm pulleys, 6 mm bore, hubless and flangeless, <= 12.6 mm long. Owner picked generic 20T 6 mm-bore pulleys for 15 mm belt (Amazon B0GN4SPFJ8) to rework: cut off the hub and both flanges, face the teeth to 12.4-12.6 mm, then drill 2.5 mm and tap M3 into the bottom of one tooth groove, halfway along. Use the grub screw from Sovol's stock 9 mm drive pulley (same 20T, 6 mm bore, so its length sits below the teeth). Also measure one 17HM19 shaft from the face (24 mm: MR105ZZ; 26 mm: 625ZZ).
6. **Wiper and purge parts:** all ordered, picked or in stock (2026-10-30), with the RTV in stock. The pads are now Qidi Plus 4 wipers (2026-10-31).
7. **Door and trays:** Sovol's model has no door. The tray sits loose on the chamber floor, 2.5 mm behind the floor's front edge, and nothing in Sovol's model blocks it sliding straight out. Check that the door's bottom seal lets it pass, and that the door opening is wider than 360 mm.
8. **Tubes and cables:** check the micro chains' outer width (11.5 mm or less) and end-link holes, the side panels' material (the anchors bolt through them), the Link Board's size against its 110 x 60 mm plate, and Link cable plus USB length (about 0.8 + 1.6 m) against Bondtech's 2 m. Test one full PTFE path with the stiffest filament for drag before building all five, and shape the arcs by hand at every corner and dock, at the bottom and top of Z.
9. **Klipper:** written in `klipper_c3/` (mainline Klipper, Kraken V1.1, sensorless X/Y, Beacon contact Z, 48 V motor supply). What remains is in its README: the Pi model, the INDX heater PID question for Bondtech, and the values only the machine can give (CAN UUIDs, serial paths, dock positions, Beacon offsets, StallGuard tuning).
