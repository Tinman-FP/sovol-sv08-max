# Changelog

## 2026-11-01: cable chains, masts and piano-wire arcs replace the PTFE loops

* **Why:** the weighted loops could not work. A 4 mm PTFE tube with filament in it is stiff: a 30 g sled pulls 0.15 N per leg, so the tube's natural loop is about 160 mm in radius, and it would need about 1.2 kg to follow the 25 mm sleds and guides.
* **What fits:** over its 500 mm of Z the gantry sweeps the whole inside of the frame except a 14-16 mm gap beside each side beam (Y 97-450). Nothing fits behind the bed or in front of the docks.
* **Chains:** ten micro chains (7 x 7 mm inside, one tube or cable each) hang in those gaps. Their fixed ends bolt through the side panels at about 290 mm print height; their moving ends hang from brackets on the side beams.
* **PTFE (as the Snapmaker U1, in from the sides):** each tube enters through a PC4-M10 coupler on the side panel, runs through its chain, rises in a side mast on the side beam and leaves on a 0.8 mm piano wire to its tool. Parked tools' tubes come down into them from above.
* **Head wiring (as the Rat Rig V-Core 4, from the back middle):** the Link Board sits on a mast on the rear beam; the INDX Link cable and Beacon USB go to the head as a piano-wire umbilical. Motor cables come up outside the side panels into their own chains.
* **Top hat:** 195 mm tall (was 136) for the arcs at full height. The spine, drop ring, loop heads, weight towers, sleds, dock guides and the cable loop are gone.
* **Friction:** about 600-780 deg of total bend per tube, so about 5-8 times the spool's drag at the extruder (capstan rule, mu 0.15). Taking the tubes to one mast at the back as well would have been 8-12 times.
* **Checks:** `c3_check.py` gives 0 clashes at its 7 poses, 0 belt contacts and 0 over the Z sweep. `c3_routecheck.py` (new) gives 0 for the chains at 13 heights, 0 for the harness against the head, and 0 for the arcs against the gantry, parked tools and top hat for every tool on the head at 13 positions; the highest arc is 36 mm under the top hat's top at full height. Three pairs of parked tubes rest lightly against each other, and the moving arcs brush another arc in about 10 % of cases.
* **Print files:** 20 new part files (masts, chain brackets, anchors and entry plates, posts, the umbilical saddle on the INDX PCB cover); the loop heads, towers, sleds, dock guides, hanger, drop ring and tray are gone. The 3MF has 88 parts on eight plates: 120.4 h and 2236 g. The top hat is 3.2 kg of ASA. The camera mount's print files had floated 3.5 mm above the bed; fixed.

## 2026-10-31: PTFE tubes and head cables on weighted loops

* **Why:** each INDX tool keeps its own PTFE tube, and with the gantry's 500 mm of Z travel a tube's length changes by up to about 840 mm. The old spring take-up had about 360 mm and treated all five tubes as one bundle, though they go to five different docks.
* **Outside:** a loop head at each front corner of the top hat holds a PC4-M10 coupler per tube; the tube passes through and the collet anchors it. Each tube hangs in a loop round a weighted sled (an M8 nut, about 30 g) in a tower on Sovol's front Z profile, then comes up through a curved guide into the top hat. The INDX Link and Beacon USB cables share a bigger loop on the right.
* **Inside:** each tube runs taut to a guide right above its own dock, so a parked tool's tube hangs straight down into it. The guides hang on a 620 mm 1515 bar under the spine. The cables drop to the head through the drop ring, now at Y 420.
* **Removed:** the take-up sled, roller and spring, the five PTFE ports in the rear wall (the PG9 gland stays), and Sovol's spool holder. The Link Board and USB hub tray moves outside the right wall.
* **Checks:** `c3_check.py` gives 0 clashes with the new parts and tube spans. `c3_ptfecheck.py` (new) checks the moving tubes at 40 poses with each tool on the head: no contact with the gantry or the top hat parts except a 0.26 mm3 graze of a guide at one corner. A tool's tube does touch the parked tools' tubes when the head is at the very front of the corners (nozzle Y above about 520); excluding Y > 520 across the full width in the slicer avoids that.
* **Print files:** 16 new parts (loop heads, dock guides, sleds, guide bar hanger, and the weight towers in six ASA sections); the take-up sled and roller are gone. The 3MF has 68 parts on eight plates: 92.6 h and 1814 g.
* **Open:** the owner's 2 m Link cable plus any USB cable is over Bondtech's 2 m limit for the two together.

## 2026-10-31: a wiper station and purge tray for every tool

* **Docks:** 78 mm apart (they were 42 mm), at X -203/-125/-47/31/109.
* **Wiper stations:** five, one 42 mm beside each tool's dock, instead of two shared ones. Each tool wipes, purges and loads filament only at its own station. Wipe strokes step 8 mm toward the tool's own dock, which is empty while that tool wipes, and never toward the next dock.
* **Purge tray:** one 360 mm tray under all five stations, the old trays' height and depth (its rim stays 0.5 mm under the station brackets at the first layer). It sits loose on the chamber floor and slides out through the door with no fasteners. It is longer than the Qidi bed, so it prints diagonally on its own plate.
* **Print files:** one file each for the wiper bracket and the slider, printed five times, and one for the tray. The 3MF has 55 parts on six plates: 66.9 h and 1249 g.
* **Front keep-out:** still 37 mm deep (nozzle Y above 535.2), now from X -238 to +186: 424 mm wide instead of 380.
* **Klipper:** new dock X for T0-T4 and a station per tool. INDX `clearance_y` moves to 33 (from 31), the same margin as the station approach line. The Orca excluded area runs to X 485.5.
* **Checks:** FreeCAD: 0 clashes at the 7 clearance poses, over the Z sweep and for the enclosure; 0 at all 27 station, wipe and dock poses with the sliders lifted; the lift still fits (9.6 of 10.8 mm); the tray and its feet clear the stock printer. SolidCraft at station 1 and at dock 1 beside lifted sliders: no overlap involving a purge part. The hard-stop sweep is unchanged and the Klipper config check passes.
* **Docs:** BOM, sourcing list, design notes, assembly guide, full printer model and renders updated.

## 2026-10-31: Qidi Plus 4 wiper pads

* **Wiper pads:** the stations now take Qidi's Plus 4 / Q2 silicone nozzle wiper, 27 x 15 x 4.7 mm high, instead of 30 x 12.7 x 3.2 mm pads cut from silicone strip. It lies 27 mm across, so each stroke crosses its 15 mm. Its top still stands 1.2 mm above the nozzle tip.
* **Wiper sliders:** the pad pocket is 2.3 mm longer toward the bed and 1.5 mm deeper. New STEP and STL files; the sliders are now 59 x 31 x 15.1 mm.
* **Print project:** plate 4 re-laid out and the project re-sliced: 62.4 h and 1168 g in all.
* **Klipper:** the wipe stroke ends at machine Y 17.3 instead of 15, 3.5 mm past the pad. The offline config check passes.
* **Checks:** all clearance checks still give 0, in FreeCAD and in SolidCraft. Only the nozzle touches the pad, 4.15 mm3 mid-wipe.
* **Front keep-out:** the lifted slider now reaches 2.3 mm further back, so the slicer's front strip is 37 mm deep instead of 35 (nozzle Y above 535.2 instead of 537.5, X -194..+186). In machine coordinates the Orca excluded area runs to Y 30.8, the station approach line moves to Y 33 and the Beacon mesh starts at Y 72.
* **Docs:** BOM, sourcing list, design notes, assembly guide and the full printer model updated.
* **Removed:** ten review renders from the morning of 30 Oct (`c3/C3_ISO.png`, `C3_DOCKS`, `C3_FRONT_CORNER_*`, `C3_REAR_CORNER_XN`, `C3_TOPHAT*`, `C3_CAMERA`, `C3_DISPLAY`). They showed the design before the wiper stations and the Y stop pads. The assembly guide and the full printer model show the current design.

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
