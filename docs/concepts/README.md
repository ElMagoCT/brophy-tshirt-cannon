# Mark 5 concepts

20 stealth-tank concepts (5 single, 5 double stacked, 5 triple stacked, 5 one-barrel
revolvers) in a small Three.js editor. Each body is built around the real Tier A parts
and checked to fit:

- **Packaging first:** 4 enclosed 6" mecanum wheels on stash CIM + Toughbox Mini corners,
  12V SLA battery, ZHSYMX compressor, electronics tray, the Viair 2.5 gal tank mounted
  across the rear, an elevation actuator, and per barrel a 3/4" QEV, a transverse 4"
  Sch 40 chamber (~0.94 L), a dump valve and a check valve.
- **Body wraps the gun:** the hull's upper side panels carry straight up into two turret
  halves. The barrels (stacked on the centreline) elevate 0-90° in the centre slot, and
  each chamber runs sideways into a half (alternating sides). The revolver has one
  barrel, one chamber and an exposed drum loaded with shirts.
- **Basic to build:** every panel is flat (fixed side slopes; nose and tail are uniform
  scales of the full section), so each facet is a planar trapezoid or triangle that can
  be cut from sheet.
- **Fit check:** every internal part is tested against the hull, and every chamber and
  valve against the turret halves through the full elevation range. The trunnion height
  is solved so the gun clears the deck from 0° to 90°. Failures show in the readout and
  in orange in x-ray.

LEDs are flat emissive textures (belt band, skirt glow, slot glow, rings, underglow decal):
no lights, no bloom.

- Open: `python3 -m http.server 8791` in this folder, then http://127.0.0.1:8791
- X-ray: the eye button in the viewer, `x` on the keyboard, or "X-ray" above the grid
- Stills: `renders/01-spectre.jpg` … `renders/20-bulwark.jpg`, `renders/contact-sheet.jpg`,
  `renders/contact-sheet-xray.jpg`

Concepts only: part envelopes are real dimensions, but the structure isn't engineered yet.
