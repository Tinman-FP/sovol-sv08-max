# Changelog

## 2026-10-31: first publication

C3 design as of 30 Oct 2026. It has not been built yet.

* **Published:**
  * printed parts, as STEP and STL;
  * the PPS-CF print project;
  * the full colour-coded printer model;
  * the gantry model;
  * BOMs and example sources;
  * the assembly guide;
  * the Klipper config;
  * the check reports;
  * the FreeCAD scripts and their inputs.
* **Build script:** `c3_build.py` now loads the Beacon model from `inputs/vendor_references/beacon/`, so the folder builds on its own.

## 2026-10-30: C3 design

* **C3:** all-wheel drive with four LDO 0.9° motors (the C2 design had two). Added the ASA top hat with the 7 inch display, the camera mount and the umbilical take-up.
* **SolidCraft cross-check:** the X carriage and Beacon reached the XY joint plates' lower flange in the last few mm of X travel. The flange was cut back.
* **Z upgrade:**
  * 12 mm belts and 17HM19-2004S1 motors.
  * New printed Z carriage plates, belt clamp covers, tensioner blocks and seats, and optional motor end supports.
* **Purge and wipe stations:** two stations in front of the bed, two slide-out trays, and the slicer's front keep-out strip.
* **Y stop pads:** added on the rear corner mounts. The joint plates now land on them 0.5 mm past travel.
* **Firmware and docs:** wrote the Klipper config (BTT Kraken, mainline Klipper, INDX, Beacon contact homing) and the 24-page assembly guide.
* **Smooth idlers:** checked the Gates 12 mm smooth idlers on the reverse-idler axles. No part changes were needed. Spacer lengths are in `c3/C3_SMOOTH_IDLER_CHECK.json`.
* **Parts for the first build:** ordered.
