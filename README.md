# Sovol SV08 Max mods

Unofficial mods for the Sovol SV08 Max from William Tinney / Tinman-FP.

Not affiliated with, or endorsed by, Sovol, Bondtech, Beacon, BIGTREETECH, Gates or Qidi.

## C3: 4040 all-wheel-drive gantry with Bondtech INDX

![The SV08 Max with the C3 gantry, colour-coded: red is printed in PPS-CF, orange in ASA, yellow is bought, green is machined](c3-4040-gantry/c3/SV08_MAX_C3_MODIFIED.png)

A new gantry for the SV08 Max, with five-tool changing. Everything is in [c3-4040-gantry](c3-4040-gantry/).

> **Status: design only.** Nothing has been printed, built or run yet. Parts for the first build were ordered on 30 Oct 2026. Every clearance check so far is a CAD check against Sovol's own model of the printer. Read [SAFETY.md](SAFETY.md) before building any of it.

What it changes:

* **Gantry:** 4040 side beams and X beam on MGN12 rails, with printed PPS-CF joints, corners and X carriage.
* **All-wheel-drive CoreXY:** four LDO 42STH48-2004MAH(S80) 0.9° motors, two per belt. Every motor has a bearing above its pulley (double shear).
* **Belts:** Gates 2MGT 12 mm, on the gantry and on Z.
* **Tool changer:** a Bondtech INDX Smart Head, centred on the X carriage, with five tools on 1515 docks at the front of the frame, 78 mm apart.
* **Probe:** Beacon Rev H, with Z homing and per-tool Z offsets by Beacon contact.
* **Z upgrade:** 12 mm belts and four StepperOnline 17HM19-2004S1 0.9° motors. The Z drive pulleys are reworked from stock 20T pulleys on a lathe.
* **Purge and wipe:** a wiper station beside each tool's dock (five in all), each with a Qidi Plus 4 silicone wiper pad, and one long purge tray under all five that slides out through the door with no fasteners.
* **Top hat:** 136 mm tall, printed in ASA. It lifts Sovol's top cover and holds a 7 inch display, the umbilical take-up and the electronics tray. There is also a new camera mount.
* **Electronics:** a BTT Kraken running mainline Klipper, with a 48 V motor supply.

The 500 mm print height stays. The front 37 mm of the bed, across 424 mm of its width, is kept clear for the docks and wipers, so the slicer's bed shape needs that strip left out. The exact numbers are in the [design notes](c3-4040-gantry/README.md).

### Where to start

All paths are inside `c3-4040-gantry/`.

| File | What it is |
|---|---|
| [`c3/SV08_MAX_C3_ASSEMBLY_GUIDE.pdf`](c3-4040-gantry/c3/SV08_MAX_C3_ASSEMBLY_GUIDE.pdf) | 24-page assembly guide. It covers preparing the parts, stripping the stock gantry, the assembly order, wiring, firmware and commissioning. |
| [`c3/C3_BOM.md`](c3-4040-gantry/c3/C3_BOM.md), [`c3/C3_Z_BOM.md`](c3-4040-gantry/c3/C3_Z_BOM.md) | Bills of materials for the gantry and the Z upgrade (also as `.json`). |
| [`c3/C3_SOURCING.md`](c3-4040-gantry/c3/C3_SOURCING.md) | Example sources (US sellers, 30 Oct 2026) for every part to buy, with notes on cutting and preparing each one. |
| [`c3/C3_PPS-CF_Qidi_Plus4_0.6mm.3mf`](c3-4040-gantry/c3/C3_PPS-CF_Qidi_Plus4_0.6mm.3mf) | Print project with all 55 PPS-CF parts on six plates. |
| [`c3/print/`](c3-4040-gantry/c3/print/) | One STEP and one STL per printed part, in print orientation. |
| [`c3/SV08_MAX_C3_MODIFIED.step`](c3-4040-gantry/c3/SV08_MAX_C3_MODIFIED.step) and `.solidcraft` | The whole printer with C3 fitted, colour-coded as in the picture above. |
| [`c3/C3_GANTRY.step`](c3-4040-gantry/c3/C3_GANTRY.step) and `.FCStd` | Every new and bought part, without Sovol's frame. |
| [`c3/full/`](c3-4040-gantry/c3/full/) | The new parts sorted by category: printed in PPS-CF, printed in ASA, machined. |
| [`klipper_c3/`](c3-4040-gantry/klipper_c3/) | Klipper config for the Kraken, INDX and Beacon, with the bring-up order. |
| [`README.md`](c3-4040-gantry/README.md) | Design notes: layout, dimensions, clearance results, the Z upgrade, the purge stations and open items. |
| `c3_*.py` | The FreeCAD scripts that build, check and release the model. |
| `c3/*.json` | Check reports: clearance, hard stops, Z, purge stations, smooth idlers. |

### Printing

* **PPS-CF parts:** 55 parts, which is 35 for the gantry and stations plus 20 for the Z kit. In the project they slice on a Qidi Plus 4 with a 0.6 mm nozzle to about 66.9 h and 1249 g. The 360 mm purge tray is longer than the Qidi bed, so it lies diagonally on its own plate. The settings are 0.24 mm layers, 6 walls and 45 % infill.
* **Supports:** 16 parts need them. The project already has tree supports on those.
* **The 3MF:** it was saved in Tinman, a fork of OrcaSlicer 2.4.2. It should open in OrcaSlicer 2.4 or later, but that has not been tested. Its printer, filament and process presets are custom ones, so set your own printer and PPS-CF profile before slicing.
* **ASA top hat:** 8 sections, each up to 289 mm long, printed upright, about 2.4 kg in all. These come as STEP and STL only; they are not in the 3MF.

### Downloading

The CAD, mesh, 3MF and PDF files are stored with Git LFS.

To get single files, open them on GitHub and click **Download raw file**.

To clone everything:

```bash
git lfs install
git clone https://github.com/Tinman-FP/sovol-sv08-max.git
```

### Rebuilding the CAD

The model is built by Python scripts run with FreeCAD's Python. They were developed on FreeCAD 1.1.4 on macOS. Run them from `c3-4040-gantry/`.

First set up the shell:

```bash
export C2_STOCK_CACHE="$PWD/c3/_cache"
```

```bash
FC=/Applications/FreeCAD.app/Contents/Resources/bin/python
```

Then run `c3_check.py` first, because its first run converts Sovol's model into the cache that the other scripts read:

```bash
$FC c3_check.py
```

Then build the model:

```bash
$FC c3_build.py
```

Then run the others the same way:

| Script | What it does |
|---|---|
| `c3_zcheck.py`, `c3_purgecheck.py`, `c3_stopsweep.py`, `c3_lanecheck.py` | The other checks. |
| `c3_release.py`, `c3_zrelease.py` | Print files and BOMs. |
| `c3_fullmodel.py` | The category STEPs in `c3/full/`. |

* **Other operating systems:** each script adds `/Applications/FreeCAD.app/Contents/Resources/lib` to its path, so change that line.
* **Smooth idler check:** `c3_idlercheck.py` is plain Python: `python3 c3_idlercheck.py 16`, where 16 is the smooth idler width in mm.
* **Inputs:** the scripts read the models in `inputs/` (see [`inputs/README.md`](c3-4040-gantry/inputs/README.md)).
* **Colour-coded model:** it is assembled in SolidCraft 0.27 from `c3_fullmodel_color.json`. Its file paths are absolute, so edit them to match your folder first.

## Licence

GPL-3.0; see [LICENSE](LICENSE). Some included files come from other projects under their own licences. [ATTRIBUTION.md](ATTRIBUTION.md) lists them and credits the designs this one builds on.

## Changes

See [CHANGELOG.md](CHANGELOG.md). The SHA-256 of every file is in [MANIFEST.tsv](MANIFEST.tsv).
