<!-- AI-assisted: Claude Code (claude-opus-5-5), reviewed by PabloBernal-CPU -->
# Test conditions of ISS combustion investigations, from two NASA resources

One row per investigation: fuel and geometry, oxygen, flow, pressure, suppressant or diluent, and
diagnostics. Every filled cell cites its source and page. An empty cell means that neither source
gives that fact; nothing was filled in from memory. Facts and figures only, no copied paragraphs.

## Sources

- **G**: *A Researcher's Guide to: Combustion Science*, NASA ISS Program Science Office, 2015
  (NP-2015-10-034-JSC), 56 pages. Linked from
  https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/ as
  https://www.nasa.gov/wp-content/uploads/2016/05/np-2015-10-034-jsc_combustion_in_reduced_gravity-iss-mini-book-011116-508.pdf
  In this PDF the printed page number equals the PDF page number, so "G p. 19" is page 19 in any
  viewer.
- **NASA Combustion Science**,
  https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/
  Its "Archived Combustion Experiments" are not web pages but one PDF sheet per investigation,
  cited here by short name and PDF page:
  - **ACME sheet**: https://www.nasa.gov/wp-content/uploads/2025/07/advanced-combustion-via-microgravity-experiments-acme.pdf (19 pages; covers BRE, CLD Flame, E-FIELD Flames, Flame Design, s-Flame and CFI-G)
  - **BASS sheet**: https://www.nasa.gov/wp-content/uploads/2025/07/burning-and-suppression-of-solids-bass.pdf (10 pages; covers BASS, BASS-II and BASS-M)
  - **DAFT sheet**: https://www.nasa.gov/wp-content/uploads/2025/07/dust-and-aerosol-measurement-feasibility-test-daft.pdf (2 pages)
  - **FLEX sheet**: https://www.nasa.gov/wp-content/uploads/2025/07/flame-extinguishment-experiment-flex.pdf (5 pages; covers FLEX, FLEX-2, FLEX-2J and FLEX-ICE-GA)
  - **Saffire sheet**: https://www.nasa.gov/wp-content/uploads/2025/07/spacecraft-fire-safety-demonstration-saffire.pdf (2 pages; covers Saffire I to VI)
  - **SAME sheet**: https://www.nasa.gov/wp-content/uploads/2025/07/smoke-aerosol-measurement-experiment-same.pdf (5 pages; covers SAME and SAME-R)
  - **SLICE sheet**: https://www.nasa.gov/wp-content/uploads/2025/07/structure-liftoff-in-combustion-experiment-slice.pdf (2 pages)
  - **SPICE sheet**: https://www.nasa.gov/wp-content/uploads/2025/07/smoke-point-in-co-flow-experiment-spice.pdf (2 pages)

  The hub has no sheet or page for CFI (the droplet Cool Flames Investigation). All URLs above
  answered HTTP 200 on 2026-11-14. The PDFs are not versioned.

## Table

"Guide 2015" says whether G describes the investigation; "not covered" means it does not.

| Investigation | Guide 2015 | Facility | Fuel and geometry | Oxygen | Flow | Pressure | Suppressant or diluent | Diagnostics |
|---|---|---|---|---|---|---|---|---|
| BASS | covered (G p. 18-22) | MSG, SPICE flow duct (G p. 19; BASS sheet p. 1) | 41 samples: thin flat 12 cm x 1 and 2 cm (SIBAL cotton-fiberglass, Nomex, Ultem); thick flat 5 cm x 1 cm x 1 and 2 mm (PMMA, wax-saturated fiberglass); PMMA spheres 1 and 2 cm diameter; candles in ceramic tube 6 mm x 25 mm, paraffin and "Japan wax" (BASS sheet p. 1) | ISS air, nominally 21 % by volume; tests with nitrogen as low as 17 % (G p. 19); 2-cm acrylic sphere at 17 % (G p. 20, Fig. 11) | airflow 5 to 50 cm/s (BASS sheet p. 3); 12 cm/s (G p. 20, Fig. 11); fabric test stepped from 10 cm/s to less than 1 cm/s (G p. 20, Fig. 12) | one atmosphere (G p. 19) | nitrogen through a nozzle, 0 to 500 cc/min by mass flow controller, raised until extinction (BASS sheet p. 2-3) | anemometer, radiometer (BASS sheet p. 3); video and still cameras (BASS sheet p. 2); MSG: digital still camera, video camera, air flow, fuel flow, radiometer (G p. 52) |
| BASS-II | not covered by name (see note 1) | MSG, modified SPICE hardware (BASS sheet p. 5) | 100 samples: thin flat 10 cm x 1 and 2 cm (acrylic films and sheets of different thicknesses, SIBAL); black or clear acrylic rods; section of a large acrylic sphere (BASS sheet p. 5) | varied by nitrogen vitiation of the work volume; no figure given (BASS sheet p. 7) | airflow 5 to 50 cm/s (BASS sheet p. 7) | | station nitrogen for vitiation, up to 500 cc/min; nitrogen suppressant through a nozzle (BASS sheet p. 7) | anemometer, radiometer, video, digital photos (BASS sheet p. 7) |
| Saffire I | not covered | Cygnus cargo vehicle after leaving the ISS; enclosure about 0.5 m x 1 m x 1.3 m with flow duct (Saffire sheet p. 1) | cotton-fiberglass blend, 0.4 m x 1 m, hot-wire ignition (Saffire sheet p. 1) | | | | | |
| Saffire II | not covered | Cygnus, after leaving the ISS (Saffire sheet p. 1) | nine samples, including cotton-fiberglass blend, Nomex and spacecraft-window acrylic (Saffire sheet p. 1) | | | | | |
| Saffire III | not covered | Cygnus, after leaving the ISS (Saffire sheet p. 2) | same cotton-fiberglass blend as Saffire I (Saffire sheet p. 2) | | "higher flow velocity" than Saffire I; no figure (Saffire sheet p. 2) | | | |
| SAME | mentioned only (G p. 26, p. 45) | MSG, Expedition 15 (SAME sheet p. 2); flown 2007 (G p. 45) | 30 samples, six each of Teflon, Kapton, silicone rubber, cellulose, and dibutyl phthalate on a porous wick, tested at different heating temperatures and smoke aging times (SAME sheet p. 2) | | different airflow rates; no figure (SAME sheet p. 2) | | | ionization (Shuttle) and photoelectric (ISS) smoke detectors (SAME sheet p. 1) |
| SAME-R | mentioned only as SAME in 2010 (G p. 45) | Expedition 24, July-September 2010 (SAME sheet p. 4) | Teflon, Kapton, cotton, silicone rubber and Pyrell (SAME sheet p. 4) | | | | | thermal precipitator for TEM, several aerosol instruments, a commercial smoke detector, ISS and Shuttle smoke detectors (SAME sheet p. 4) |
| FLEX | covered (G p. 12-13, p. 33-36) | CIR with MDCA insert (G p. 12, p. 36) | heptane and methanol droplets (G p. 12; FLEX sheet p. 2); initial diameter 2 to 5 mm (FLEX sheet p. 2) | mole fraction 0.10 to 0.50 (FLEX sheet p. 1); a test at 21 % (G p. 12, Fig. 2) | quiescent ambient (G p. 33); a droplet translated at 3 cm/s (G p. 12, Fig. 2) | 0.5 to 1.0 atm (FLEX sheet p. 2) | diluent mainly nitrogen, some helium; suppressants carbon dioxide and helium, from 0.00 mole fraction to about 0.70 (FLEX sheet p. 1-2); second inert gas nitrogen, carbon dioxide, helium or xenon (G p. 12); a test at 70 % carbon dioxide (G p. 12, Fig. 2) | MDCA: analog color camera, radiometer, low light level UV camera, two HiBMs cameras (G p. 52) |
| FLEX-2 | covered (G p. 13, p. 36) | CIR with MDCA (G p. 36, p. 52) | droplets 2 to 4 mm, single or pairs on a fiber; pure fuels, mixtures, surrogates (FLEX sheet p. 3-4; G p. 13); ethanol in one figure (G p. 12, Fig. 3) | 30 % in one test (G p. 12, Fig. 3) | quiescent, plus sub-buoyant flow made by moving the tethered droplet; no figure (FLEX sheet p. 4) | 2.4 atm in one test (G p. 12, Fig. 3) | | MDCA: analog color camera, radiometer, low light level UV camera, two HiBMs cameras (G p. 52) |
| CFI | not covered (proposed as "Cool Flames" initiative, G p. 41-42) | to use FLEX-2 CIR/MDCA hardware (G p. 42) | | | | | | |
| SPICE | covered (G p. 13-14) | MSG, fan-driven flow duct, 2009 (G p. 13) | gas-jet coflow flames of propylene, propane and ethylene (SPICE sheet p. 2); three nozzles (SLICE sheet p. 2) | | coflowing air; nozzle diameter and coflow velocity varied, no figure (SPICE sheet p. 1-2) | | | MSG: digital still camera, video camera, air flow, fuel flow, radiometer (G p. 52) |
| SLICE | covered (G p. 14-15) | MSG with SPICE hardware, 2012 (G p. 14) | gas-jet flames of methane, ethylene and nitrogen dilutions of each, in air coflow (SLICE sheet p. 1) | | fuel flow fixed, air velocity raised until liftoff; no figure (SLICE sheet p. 2) | | nitrogen as fuel diluent (SLICE sheet p. 1) | still and video imaging (SLICE sheet p. 2); MSG list as SPICE (G p. 52) |
| DAFT | mentioned only (G p. 26) | anywhere in the ISS cabin, no external power (DAFT sheet p. 2) | none: measures background aerosol in the ISS air (DAFT sheet p. 1; G p. 26) | | | | | P-Trak ultrafine particle counter; SAME needs counts from 0.2 to 1 micron (DAFT sheet p. 1) |
| ACME BRE | covered (G p. 15) | CIR, ACME insert, about 90 L free volume, constant volume (ACME sheet p. 18) | flat porous burner fed with gaseous fuel, flow set from measured heat flux and surface temperature (G p. 15; ACME sheet p. 2) | | | | | surface thermocouple and two heat flux transducers per burner (ACME sheet p. 11); ACME suite, note 2 |
| ACME CLD Flame | covered (G p. 16) | CIR, ACME insert (ACME sheet p. 18) | coflow gas-jet flames of methane and ethylene diluted with nitrogen, in air coflow (G p. 16; ACME sheet p. 3) | | air coflow; injection velocity varied, no figure (G p. 16) | | nitrogen as fuel diluent (ACME sheet p. 3) | ACME suite, note 2 (ACME sheet p. 12-18) |
| ACME E-FIELD Flames | covered (G p. 16) | CIR, ACME insert (ACME sheet p. 18) | coflow flame or gas-jet flame without coflow (G p. 16); mesh electrode about 35 or 50 mm downstream of the burner (ACME sheet p. 18) | | | | | field up to 10 kV (G p. 16), +10 to -10 kV (ACME sheet p. 18); ion current through the flame (ACME sheet p. 18) |
| ACME s-Flame | covered (G p. 17-18) | CIR, ACME insert (ACME sheet p. 18) | porous spherical burner; hydrogen, methane, ethylene with inert diluents (G p. 17-18; ACME sheet p. 6) | | | | inert diluents in fuel and chamber atmosphere (ACME sheet p. 6) | ACME suite, note 2; far-field thermocouples for spherical flames (ACME sheet p. 15) |
| ACME Flame Design | covered (G p. 16-17) | CIR, ACME insert (ACME sheet p. 18) | spherical porous burner, ethylene or methane; inverse or coflow flames considered (G p. 17; ACME sheet p. 5-6) | oxygen-enriched atmosphere, concentrations varied, no figure (G p. 17) | | | | ACME suite, note 2 (ACME sheet p. 12-18) |
| ACME CFI-G | not covered | CIR, ACME hardware (ACME sheet p. 6) | gaseous fuel on a porous spherical burner, cool diffusion flames (ACME sheet p. 6) | | | | | |

## Notes

1. **BASS and BASS-II in G.** G describes "BASS" as running since March 2012 (G p. 18-19) and
   mentions tests at 17 % oxygen made with nitrogen (G p. 19). BASS-II varied oxygen by nitrogen
   vitiation (BASS sheet p. 7), so those tests may belong to BASS-II, but G does not say so. They
   are left in the BASS row as G gives them.
2. **ACME diagnostic suite** (ACME sheet p. 12-18; G p. 52): HD color camera, 1360x1024 at 30 fps
   with color, BG7 and CH* (430 nm) filters; analog camera; low light level UV camera for OH*
   (310 nm); HiBMs camera with tunable filter for pyrometry; second HiBMs camera with laser
   diodes for soot volume fraction; thin filament pyrometry with 5 SiC fibers; thermocouples;
   radiometers, 0.2-11 micron; three photomultiplier tubes (OH*, CH*); chamber pressure; gas
   chromatograph for oxygen, nitrogen, carbon dioxide, carbon monoxide and fuel gases before and
   after each test; SAMS-II accelerometers. Tests last 0.5-2 minutes (ACME sheet p. 18). Gas
   delivery: fuel up to 2 slpm, oxidizer and nitrogen up to about 10 slpm, nitrogen basis
   (ACME sheet p. 11).
3. **Ground tests, not ISS.** G gives drop tower figures for two ACME experiments, kept out of the
   table: Flame Design, 1.51 mg/s of 100 % ethylene into air at atmospheric pressure (G p. 17,
   Fig. 6); s-Flame, burner gas 25 % propane, 2 % oxygen, 49 % argon, 24 % nitrogen (G p. 17,
   Fig. 7). Also a drop tower PMMA sphere at 17 % oxygen, 1 atm, 2 cm/s (BASS sheet p. 2), and one
   at 30 cm/s airflow (BASS sheet p. 2).
4. **Facility limits, not test conditions.** MDCA: droplets 1 to 5 mm, 0-3 atm, up to 40 %
   oxygen by volume (G p. 12); note that FLEX lists oxygen up to 0.50 (FLEX sheet p. 1). SoFIE
   (planned for 2019): oxygen 10 % to 40 %, 0.2 to 1.5 atm (G p. 19), airflow 0 to 30 cm/s
   (G p. 21). The CIR chamber is 100 L with eight windows (G p. 44).
5. **Contradiction in the BASS sheet.** BASS-II is "100 fuel samples" (BASS sheet p. 5), but its
   protocol repeats BASS's "Forty-one test samples ... 89 test points" (BASS sheet p. 7).
6. **Saffire IV to VI** are also on the Saffire sheet, without figures: different pressures and
   oxygen (IV), exploration-spacecraft pressures and oxygen (V), oxygen levels plus detection,
   combustion product monitoring and post-fire cleanup (VI) (Saffire sheet p. 2).
