# electrical/

**Rev D.2 proposal (2026-11-06), waiting on Micah's green light.** It changes the control side; the sections below are
rev C.3/D and still describe the power tree and sensors, except where this box says otherwise.
- **One controller:** an ESP32-P4 + ESP32-C5 board (Wireless Tag WTDKP4C5-S1) replaces the STM32F411, the ESP32-C5
  bridge and their UART. WiFi 6 on 2.4 + 5 GHz from the C5 on the same board; MIPI camera port; 16 parallel LED lanes.
  An ADS1115 reads the three transducers + the 5 V reference; the P4's ADC reads the pot, battery and PDH volts.
- **No PWM gate.** The contactor is the cut-off. Its coil: logic tap -> rear E-stop contact 1 -> safety node switch ->
  main controller MOSFET (all in series). The safety node holds it only while the remote's and the controller's
  heartbeats are alive; it no longer drives a separate safety relay or gate.
- **Valve arm relay** (was the safety relay): coil fed from the PDH through rear E-stop contact 2, armed by the
  controller, so the valve rail dies with the contactor and a stuck MOSFET can't fire a disarmed gun.
- **Audio:** the P4 mixes horn, effects and phone music to the PCM5102A. Phone music comes from a classic ESP32
  (Bluetooth A2DP sink) over I2S; volume/pause go back over a UART.
- MOSFET modules trigger from 3.3 V (no buffer); 74AHCT125s only level-shift LED data. One contactor, a diymore
  3.6-32 V buck-boost for the logic rail.
- Details and alternatives: `docs/glacis/JUDGMENTS.md`, "Rev D.2 proposal"; the "Glacis air & wiring" artifact has a
  power sim of all of this.

Glacis electrical design as of rev C.3 (2026-11-03). The drawing is the "Glacis air & wiring" artifact
(source `docs/glacis/air_wiring_artifact.html`); parts are in `bom/glacis_bom.py`. Pin map: firmware phase.

## Power: two sides

```
FRC battery x2 (parallel, SB50) + charge port
        |
   120 A main breaker  (master off: everything, logic included)
        |
        +--- 5 A ATO fuse --- PM02 5 V 5 A buck-boost --- LOGIC RAIL (always on)
        |                                                         STM32, WiFi bridge, safety node,
        |                                                         all sensors
        |
   200 A contactor  (coil: 12 V tap -> rear E-stop contact 2 -> STM32 MOSFET channel; flyback diode)
        |
     REV PDH (switched side: dead in standby)
        +--- Falcon 500 x4 (40 A), Spark MAX (goBILDA)
        +--- 20 A buck -> WS2812 LEDs only
        +--- (40 A channel) 48 V 1500 W boost -> TPA3255 amp -> two 200 W siren speakers
        +--- fog core relay(s) -> MOSFETs -> heater, pump, blower
        +--- 10 A channel -> STM32 MOSFET (PWM) -> front light bar (Zmoon 12 in, 72 W, ~6 A)
        +--- safety relay (coil: safety node + rear E-stop contact 1) -> 12 V valve rail -> firing + in valves
```

- **Standby** = main breaker on, contactor open. The PDH and everything on it is dead. The logic rail
  stays up, so the STM32 reads every sensor, the web UI shows pressures, fog fluid, temperatures and
  battery, and the remote stays linked. Arm from the UI and the STM32 closes the contactor (~20 ms).
- **The light bar is the STM32's**: on, off and dimming from the web UI, through one MOSFET channel's PWM
  (a few hundred Hz; if its driver flickers on PWM, run it on/off only).
- **The logic rail is a buck-boost** (3-20 V in), so a drive sag can't reset the controllers.
- **Frame strips run sealed in PETG tunnels:** cap the 100/m frame strips at about 20% white in firmware (heat in
  the sun), and the front and rear bottom members have no tunnel, so a jumper wire runs round each (rev D.1.4).
- **Siren speakers:** two Xprite 200 W, 8 ohm on a TPA3255 board fed by a 1500 W boost set to 48 V, on a 40 A PDH
  channel: about 100 W a speaker, 20-25 A from the battery at full siren (rev D.1.4).
- **Rear E-stop:** a 2NC mushroom. Contact 1 is in the safety relay coil (valves dead), contact 2 is in
  the contactor coil (whole PDH dead). Both in hardware; the STM32 can't override either.
- **Remote E-stop, lost link, dead STM32 heartbeat, tank over 210 psi:** the safety node drops the
  safety relay and disables the PWM gate, as before. The STM32 also opens the contactor on any of these.
- **No precharge** on the contactor. At 12 V with FRC loads it's the same event as closing a main breaker.
- **Never switch the negative.** Grounds are common; only +12 V goes through the contactor.
- **Storage:** flip the main breaker off. Standby draws about 2 W.

## Sensors (all on the logic rail)

| Sensor | Part | To the STM32 | Notes |
|---|---|---|---|
| Tank, chamber A, chamber B | 3 x FUSCH 0-300 psi, 0.5-4.5 V | ADC, 10k/15k divider | One part number. 100k pull-down: a cut wire reads < 0.4 V = fault, never "empty" |
| 5 V logic rail | divider | ADC | Transducers are ratiometric: scale by the measured 5 V |
| Battery volts (unswitched) | 39k/10k divider | ADC | Dashboard battery; low-battery standby |
| PDH volts (switched) | 39k/10k divider | ADC | Confirms the contactor closed; catches an E-stop and a welded contactor |
| Gun angle | 10k pot | ADC | Power it from 3.3 V, not 5 V, so it can't overdrive the ADC |
| Fog core temperature | MAX6675 + K probe | SPI | Open-thermocouple bit = heater off |
| Fog fluid level | XKC-Y25-NPN capacitive switch | GPIO (pull-up to 3.3 V) | Taped to the outside of the printed tank at ~20%. No hole in the tank |
| Fogger box, electronics shelf, battery bay | 3 x DS18B20 | 1-Wire, one pin | Heater off at 70 C in the fogger box (PETG softens near 80 C) |

**Fog fluid gauge for free:** the peristaltic pump is volumetric (70 mL/min, calibrate once), so
pump-seconds since the last refill = mL used. The UI shows a % gauge; the level switch re-syncs it and
stops the pump about a minute after it reads dry.

## Main valve is manual (rev C.3)

A 1/4 NPT brass ball valve (600 WOG; the old cannon's if it's rated) replaces the Aignep main valve.
- Open for a session, closed for transport and before working on the gun. Handle at the rear panel.
- The in valves now hold tank pressure all session. They're rated 507 psi and normally closed, and they
  sit on the valve rail, so a trip still isolates both chambers from the tanks.
- If an in valve leaks or sticks open, the chamber's 125 psi relief (120 SCFM) easily outflows a 2 mm orifice.
- Firmware: fill = pulse the in valve to setpoint. No main-valve step. One fewer relay channel.

## Controller check: is the STM32 enough?

**Yes, for its job.** STM32F411 (Black Pill): Cortex-M4F with FPU, 100 MHz, 512 KB flash, 128 KB RAM.

| Need | Has |
|---|---|
| 7 ADC inputs (3 transducers, pot, battery, PDH, 5 V ref) | 10 external channels on the Black Pill |
| 5 servo PWM (4 Falcons, Spark MAX) + 2-3 LED data lines with DMA | 8 timers |
| MAX6675 | 5 SPI |
| UART to the bridge | 3 USART (one shares the USB pins, so 2 free) |
| USB to the rear panel | USB FS on the USB-C |
| Trajectory solve (drag model like `cad/glacis/range_model.py`) | Tens of ms on the FPU |

What it is not, and shouldn't be: the Wi-Fi, web or video computer. It has no radio and 128 KB RAM.
That's why the design already splits it:
- **STM32:** everything time-critical (valves, metering, drive, elevation loop, fog, contactor).
- **ESP32-C5 WiFi bridge (rev D; was an ESP32-S3):** serves the gzipped web UI from flash and runs the
  WebSocket at 20-50 Hz on 5 GHz. The browser does the heavy work (robot rendering, trajectory). Fine for
  a rich UI; the limit is about 4-8 clients.
- **Trajectory math goes in the browser.** The dashboard already has the angle and chamber pressure, and
  it's where the aim arc gets drawn. The robot only receives angle and pressure setpoints.

### WiFi on 5 GHz (rev D)

2.4 GHz in a packed gym is crowded (phones, earbuds), so the web UI's access point moves to 5 GHz on an
**ESP32-C5** (Waveshare WiFi 6 kit, $13.99). Espressif documents a 5 GHz SoftAP on the non-DFS channels
36-48. It replaces ESP32-S3 #1 as the bridge, same UART to the STM32, same code base. The safety node and
remote stay on 2.4 GHz ESP-NOW, so the two links don't share a band.
- Use long-range mode for ESP-NOW and send heartbeats every 20 ms, so a 200 ms trip needs about 10 lost
  packets in a row.

### "An STM32 with WiFi?"

ST doesn't make one with WiFi built in. What exists:

| Board | Price | WiFi | Verdict |
|---|---|---|---|
| Arduino GIGA R1 WiFi (STM32H747 + Murata 1DX) | $72.82 | 2.4 GHz only (802.11b/g/n) | The closest thing. 10x the Black Pill, back on 2.4 GHz, and its Arduino core sits on Mbed OS, which Arm retired in July 2026 (Arduino is moving it to Zephyr) |
| STM32 + EMW3080 discovery kits | ~$60 | 2.4 GHz | Dev kits, not robot boards |
| **STM32F411 + ESP32-C5 bridge** | $7 + $14 | 5 GHz | **Picked**: the STM32 keeps the clean ADC and the real-time work; the C5 only does WiFi |
| ESP32-C5 alone | $14 + ~$15 of helpers | 5 GHz | One board, but it needs an ADS1115 for the pressure sensors and a PCA9685 for the 15 switched outputs (about 22 free pins), and its single core runs control and the WiFi stack together |

Two boards with one job each is the more reliable setup. The one-board C5 is fewer parts, not fewer
failure modes.

### Camera (deferred, rev D)

No camera for now. For later:
- **USB webcam:** it needs a board with USB host on the 5 GHz network. A spare ESP32-S3 can stream a USB
  webcam (Espressif's UVC host driver, MJPEG), but it's 2.4 GHz only, so it can't join a 5 GHz access
  point. A dual-band Linux board (a Raspberry Pi 4, or similar) can. Prices unchecked until it's needed.
- **GoPro:** a HERO12 or HERO13 can join an existing WiFi network ("Camera on the Home Network" in Open
  GoPro). Neither the STM32 nor the C5 can relay video, though: the laptop would have to pull the stream
  from the GoPro itself, and browsers can't play its preview format without a helper app.
- Mount any camera on the gun mantlet so an aim overlay moves with the barrels.

## Power budget (estimates)

| Load | Average | Peak | Side |
|---|---|---|---|
| Logic rail (STM32, 2 x ESP32-S3, sensors) | 0.2 A | 0.5 A | always on |
| Contactor coil | 0.7 A | 0.7 A | coil on logic tap |
| LEDs, 1,680 at the 20% cap | 4-5 A | 6 A | switched |
| Fog core (holding temp, puffs) | 9 A | 17.5 A | switched |
| Audio | 1 A | 5.5 A | switched |
| Drive + elevation (parade vs gym) | 5-15 A | 160 A | switched |
| Valves (only while firing/filling) | ~0 | 3 A | switched |

About 25 A on average at an event. Two 18 Ah FRC batteries give roughly an hour at that rate (lead-acid
loses capacity at high draw), so swap one battery every ~30 minutes at long events. LEDs and fog are
the big steady draws; dim the LEDs first if a game runs long.

Live swap: pull the low battery first, then plug in the fresh one. Expect a short 20-40 A rush between
them and a small spark at the SB50.

## Wiring notes

- WS2812 power: inject 5 V at every frame node and both ends of each panel loop (14 AWG trunk); a
  300-470 ohm resistor at each strip's data input and 1,000 uF at each injection point.
- Hold every output to the switched side low while the PDH is off (LED data, PWM, MOSFET gates), so
  the logic side never back-powers an LED strip or motor controller through a signal pin.
- Pull-downs on the contactor, heater-relay and valve gates: an STM32 reset turns all of them off.
- Firing valves: plain flyback diodes are fine. In valves: diode + 18 V zener so they close faster and
  meter more exactly.
- Firmware latches: no auto-restart after an E-stop (PDH volts dropped without a command = stay off
  until re-armed from the UI); contactor commanded off but PDH still live = welded-contact fault;
  battery under 11.0 V for 5 s under load = back to standby; in valve open longer than a fill should
  take = fault for that cannon.
