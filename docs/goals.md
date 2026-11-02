# Brophy T-Shirt Cannon - Mark 5: Goals

Source: Google Doc "Brophy T-Shirt Cannon - Mark 5" in Micah's Drive (not public).
This copy is kept current; when the doc changes, update this file and note it in
`decisions.md`.

Team: Micah Tucker

## Construction
- Aluminum extrusion construction
  - T-slot or other for accessorizing?
  - Maybe welded steel so it literally can't fall apart for the chassis
- Frosted acrylic body
- Clear tube?
- Soft bumpers
  - White
  - Backlit?
- 1in thinner for doors

## Functionality
- Multi shot
  - Triple barrel
  - Magazine (ref: https://www.youtube.com/watch?v=Yn_wtP6Gjho)
  - Rotary (ref: https://www.youtube.com/watch?v=1Zqx96xyHDk)
  - Revolver
- Self-sufficient air system
  - 10 shots in permanently fixed tank
  - Fills 1 shot worth every 5 minutes
- 0-90 degree range
- Speaker horn (different tones, control volume, etc)
  - Music?
  - How custom do we want this...
- All terrain mecanum
  - like gravel, grass, and ramps
  - Good for gym floors
  - Custom?
  - (an AliExpress all-terrain mecanum set at ~$108 was noted as "expensive")
- Variable pressure
  - Rapid actuator to secondary tank
- Turret (might be doing too much but would be super cool)
- Cooling system
- 150psi

## Electronics
- Runs off ESP32 or other
- Control via WebSocket (any remote usable)
  - Any device
  - easier to code
  - No frc nonsense
- USB straight to robot
  - <3 sec boot
- Dashboard
  - Show pressure (of each tank)
  - Robot rendering (with lights)
  - Battery
- Video livefeed

## Aesthetics
- LEDs
  - Cannon
  - Underneath
  - Acrylic body glow
  - Under bumper foam
- Smoke machine
  - Out of cannon
  - Under bumper

## Context (Micah's words, cleaned up)

Mark 4 is literally falling apart, looks terrible, uses 15-year-old FRC parts,
and has a ton of setup and reliability issues. We want more shots and variable
shots. Maybe weld the chassis if it can still be easily serviced. I want it
controlled via an ESP32 and a WebSocket that lets you connect any HID or use
keyboard/trackpad, so anyone with a Mac could connect and we don't need specific
hardware or software. I think custom 3D printed mecanum wheels would be good.
We have a plasma cutter, CNC, and waterjet. The robotics club operates it for
student council.

## Known tensions with the settled design
- "10 shots stored, 1 shot per 5 minutes" is backwards from what a 12V pump does:
  realistic is ~4-5 full-power shots stored, then one shot every ~30-60 s
  indefinitely (see `decisions.md`).
- "1in thinner for doors" is unexplained. Ask Micah what door width it targets.
