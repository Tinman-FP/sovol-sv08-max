# Attribution

This repository is an unofficial set of Sovol SV08 Max mods. It does not claim ownership of Sovol's printer design or of any third-party part below.

## This design

* **C3 gantry design, CAD scripts, printed parts, BOM, assembly guide and Klipper config:** William Tinney / Tinman-FP.
* **Help with design, CAD scripting and documentation:** Claude Code (Anthropic).
* **Licence:** GPL-3.0 (see [LICENSE](LICENSE)).

## Designs it builds on

| Source | What is used | Licence |
|---|---|---|
| **Sovol**, SV08 Max ([github.com/Sovol3d/SV08MAX](https://github.com/Sovol3d/SV08MAX)) | Sovol's "SV08 Max Unmodified" STEP model of the printer. It is the frame every part is designed to, it is in the full printer model (`c3/SV08_MAX_C3_MODIFIED.*`), and it is converted for the scripts in `inputs/stock_printer/`. The Z tensioner block and seat are Sovol's parts with the belt slots widened. | Sovol publishes the SV08 Max files on GitHub with no licence file. Its SV08 repository is GPL-3.0 and describes the SV08 as a derivative of the Voron 2.4. |
| **Nadir @ CN3D**, "Sovol SV08 MAX Gantry V2 (NEMA17, Double Shear)", [Printables 1404311](https://www.printables.com/model/1404311) | Layout reference for the gantry: a Voron-2.4-style flying-gantry layout with double-shear motors. No files or geometry are copied from it. | GPL-3.0 |
| **Voron Design**, Voron 2.4 ([github.com/VoronDesign/Voron-2](https://github.com/VoronDesign/Voron-2)) | The CoreXY gantry layout that the SV08 and the layout above derive from. | GPL-3.0 |

## Third-party files included

| Files | From | Licence |
|---|---|---|
| `c3-4040-gantry/inputs/vendor_references/bondtech/`: INDX simplified STEP, tool dock STLs | Bondtech, [github.com/BondtechAB/INDX](https://github.com/BondtechAB/INDX) | GPL-3.0 (copy of the licence in that folder) |
| `c3-4040-gantry/klipper_c3/printer_data/config/indx/`: INDX macros and config | Bondtech's INDX macros at commit 05018b2, with the C3 values changed as the file headers say | GPL-3.0 |
| `c3-4040-gantry/inputs/vendor_references/beacon/`: Beacon Rev H STEP | Beacon ([beacon3d.com](https://beacon3d.com/)) | MIT (`CAD_LICENSE` in that folder; the Molex sub-assembly is under Molex's terms) |
| INDX Smart Head, docks and Beacon geometry inside `c3/C3_GANTRY.*` and `c3/SV08_MAX_C3_MODIFIED.*` | The same Bondtech and Beacon files | As above |

## Software the config is written for

* [Klipper](https://github.com/Klipper3d/klipper) (GPL-3.0).
* Bondtech's [indx_klipper](https://github.com/BondtechAB/indx_klipper).
* [beacon_klipper](https://github.com/beacon3d/beacon_klipper).
* Moonraker, Mainsail, KlipperScreen and Katapult.

None of these are included here. Install them from their own repositories, as `klipper_c3/README.md` describes.

## Bought parts

Gates, KB-3D, LDO, StepperOnline, BIGTREETECH, Qidi (the wiper pads), HIWIN-style MGN12 and the other bought parts are named only to identify them. The models of them in the CAD are simplified shapes drawn for fit, except the Bondtech and Beacon parts above. No manufacturer catalogues or drawings are included; the design notes cite them by name.
