# Changelog

## 2026-11-05 (later): 1.4 mm umbilical wire, round clamp stalk, route check every 50 mm

* **Why:** the owner asked to fix the 11 full-height contacts the 5 x 5 check had found (the umbilical on belt B, the tubes through the roof clamp's stalk, a tube on a parked tool).
* **Umbilical:** the piano wire is 1.4 mm instead of 1.2 mm. The loop at full height can swing round in plan at the same energy (both its ends point down), so it was checked over every swung shape: 1.4 mm clears belt B by 4 mm and the top hat's walls by 5-10 mm; 1.2 mm sagged 4.6 mm into the belt and 1.3 mm cleared it by 0.4 mm. Same length (764 mm), same 1.6 mm bores in the clamp and the saddle.
* **Roof clamp:** its stalk is round (28 mm across, lower edge rounded 6 mm) and the plate's corners are rounded, so a tube arching past slides off. Still 66 mm long: a stalk short enough to clear the tubes (25 mm or less) makes the umbilical about 40 mm longer, and its swung loop then reaches 4-7 mm into the top hat's front and rear walls.
* **Route check:** `c3_routecheck.py` now checks the first layer and every 50 mm of print height to 500 mm (11 heights, each in its own process; about 25 minutes), and splits contacts into clashes (anything that moves against a line or has edges: head, bridge, belts, docks, gantry parts, stock frame, couplers) and rubs (a line resting on a smooth printed surface: the top hat's walls, the roof clamp, a parked tool's top). The three heights used until now missed a tube on the top hat's front corner at 350-400 mm.
* **Tubes:** unchanged. With about 500 mm of spare length at full height, the free tubes lean on something somewhere; every change tried (coupler tilt 32-36 deg, height, yaw, positions further back, 6.5-8 % length) removed one contact and added another, some on the head or belt B. So their rubs on smooth printed parts are reported like tube on tube.
* **Checks:** `c3_check.py`: 0 at the 7 poses, 0 belt contacts, 0 over the Z sweep and for the enclosure. `c3_routecheck.py`: 0 for the motor chains; 0 clashes; 11 rubs, each a tube on a smooth printed surface: past the round stalk 5 (500 mm), on the top hat's front-right corner 4 (T0 at 350 and 400 mm), on the parked T2's top 2 (500 mm); 0 above the cover (arch tops 5 mm under it); 0 not solved; tubes touch in 1959 of 21450 checked pairs (active on parked 784, on the umbilical 941, parked on parked 234, all T0 beside T1; 1354 crossing in all).
* **Print files:** only the umbilical roof clamp changes (60 g of PPS-CF, was 66). The PPS-CF project is rebuilt: 6 plates, 65 parts, 61.9 h, 1153 g, no slicer warnings, 21 parts with supports. Printed total: PPS-CF 1025 g, ASA 3207 g.

## 2026-11-05: all five PTFE couplers in the right wall, close together

* **Why:** the owner was worried that the free tubes could tangle. With three couplers on the right and two on the left, the parked tubes from the two walls met and crossed in the middle of the top hat.
* **Change:** all five PC4-M10 couplers are now in the top hat's right side wall, two to a bay around the wall's middle (bay centre +/- 15 mm). From the front: T0 to T4 at Y 352, 322, 289, 259, 225, in the order of the docks, so the parked tubes nest instead of crossing. Height and angle are unchanged (about 705 mm above the bed, 34 deg down). Free lengths: T0 906, T1 896, T2 902, T3 913, T4 926 mm. The filament box now feeds all five from the right.
* **Denser check:** `c3_routecheck.py` now puts the head at 25 bed positions (5 x 5) instead of 9, and splits tube contacts by kind and by crossing (more than 30 deg apart) or side by side.

| Layout (5 x 5 check) | Contacts with hardware | Tube pairs touching | Parked on parked (crossing) | Crossing pairs | Longest tube |
|---|---|---|---|---|---|
| Two walls (released 2026-11-01) | 11 | 880 | 468 (390) | 758 | 932 mm |
| Right wall, one per bay (Y 158-382) | 22 (10 on the walls, frame top, belt and X beam) | 360 | 0 | 310 | 956 mm |
| **Right wall, close together (released)** | **11** (0 on walls or frame) | **533** | **78 (0)** | **376** | **926 mm** |

  Spreading the couplers one per bay sent the rearmost tube into the wall and the frame top, so they sit close together around the wall's middle.
* **Open (in every layout, missed by the 3 x 3 grid):** 11 contacts, all at full height: the umbilical on belt B 4, a tube through the roof clamp's stalk 5, the tube on the head brushing the parked T2's nozzle 2; none with the walls or frame. They need their own fix: a round stalk with a chamfered end, and a look at the umbilical's loop.
* **Tried and dropped (2026-11-02):** a 1.0 or 0.8 mm piano wire along each tube. The stiffer tubes held bigger arches, which went up to 12 mm over the cover or into the roof clamp and the head saddle at full height, and touched each other as often.
* **Checks:** `c3_check.py`: 0 at the 7 poses, 0 belt contacts, 0 over the Z sweep and for the enclosure. `c3_routecheck.py`: 0 for the motor chains; 11 contacts, all at full height: the umbilical on belt B 4, a tube through the roof clamp's stalk 5, the tube on the head brushing the parked T2's nozzle 2; none with the walls or frame; 0 above the cover (arch tops 5 mm under it); tubes touch in 533 of 5850 checked pairs (active on parked 209, on the umbilical 246, parked on parked 78, T0 on T1 at 500 mm, side by side; 376 crossing in all).
* **Print files:** only the top hat's two side straights change (the right one carries all five coupler pads, the left one none). The PPS-CF parts and the 3MF are unchanged. The top hat is 3.2 kg of ASA.

## 2026-11-01 (evening): simpler routing: wall couplers, free tubes and a roof umbilical

* **Why:** the owner found the chains, masts and arcs far too complicated. Now the tubes come in through plain couplers in the wall and hang free, and the head cables come down from the centre of the top cover.
* **PTFE:** five PC4-M10 couplers in the top hat's side walls (three right, two left), 34 deg down and pointing inboard, about 705 mm above the bed. That is above the gantry's highest point: lower, a tube would hang under the gantry and into the print whenever the gantry is above its coupler. Each tube runs free from its coupler to its tool, as Sovol's own tube does. Free lengths: T0 901, T1 907, T2 932, T3 907, T4 901 mm.
* **Head wiring:** the INDX Link cable and Beacon USB come straight down from a clamp under the centre of the top cover, on a 1.2 mm piano wire in loom (764 mm), to the saddle on the INDX PCB cover. The Link Board and the USB hub sit on the cover.
* **Motor cables:** unchanged, one micro chain per gantry motor in the gaps beside the side beams (four chains instead of ten).
* **Removed:** the PTFE and USB chains, the side masts, the rear mast, the harness and its posts, and the 0.8 mm piano wires.
* **Friction:** a tube now bends through 91-332 deg in all inside the chamber, against 600-780 deg before: about 1.3-2.4 times the spool's drag at the extruder instead of 5-8 times.
* **Checks:** `c3_check.py`: 0 at the 7 poses, 0 belt contacts, 0 over the Z sweep and for the enclosure. `c3_routecheck.py` (rewritten): 0 for the motor chains at 13 heights; 0 contacts for the free tubes and umbilical with the gantry, parked tools, frame or top hat at the first layer, 250 mm and 500 mm, for each tool on the head at 9 bed positions and its own dock; the tube arches stay 6 mm under the cover at full height. The tubes cross and rub in 355 of 2250 checked pairs.
* **Print files:** new: the umbilical roof clamp. Gone: the side masts, rear mast, harness posts and the PTFE and USB chain fittings. The top hat's side pieces carry the coupler pads. The 3MF has 65 parts on 6 plates: 62.4 h and 1158 g. The top hat is 3.2 kg of ASA.

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
