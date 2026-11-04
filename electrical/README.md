# electrical/

Glacis electrical design as of rev C.3 (2026-11-03). The drawing is the "Glacis air & wiring" artifact
(source `docs/glacis/air_wiring_artifact.html`); parts are in `bom/glacis_bom.py`. Pin map: firmware phase.

## Power: two sides

```
FRC battery x2 (parallel, SB50) + charge port
        |
   120 A main breaker  (master off: everything, logic included)
        |
        +--- 5 A ATO fuse --- Pololu S13V30F5 5 V buck-boost --- LOGIC RAIL (always on)
        |                                                         STM32, WiFi bridge, safety node,
        |                                                         all sensors, camera (if added)
        |
   200 A contactor  (coil: 12 V tap -> rear E-stop contact 2 -> STM32 MOSFET channel; flyback diode)
        |
     REV PDH (switched side: dead in standby)
        +--- Falcon 500 x4 (40 A), Spark MAX (goBILDA)
        +--- 20 A buck -> WS2812 LEDs only
        +--- 24 V boost -> TPA3116 amp -> siren speakers
        +--- fog core relay(s) -> MOSFETs -> heater, pump, blower
        +--- safety relay (coil: safety node + rear E-stop contact 1) -> 12 V valve rail -> firing + in valves
```

- **Standby** = main breaker on, contactor open. The PDH and everything on it is dead. The logic rail
  stays up, so the STM32 reads every sensor, the web UI shows pressures, fog fluid, temperatures and
  battery, and the remote stays linked. Arm from the UI and the STM32 closes the contactor (~20 ms).
- **The logic rail is a buck-boost** (2.8-22 V in), so a drive sag can't reset the controllers.
- **Rear E-stop:** a 2NC mushroom. Contact 1 is in the safety relay coil (valves dead), contact 2 is in
  the contactor coil (whole PDH dead). Both in hardware; the STM32 can't override either.
- **Remote E-stop, lost link, dead STM32 heartbeat, tank over 210 psi:** the safety node drops the
  safety relay and disables the PWM gate, as before. The STM32 also opens the contactor on any of these.
- **No precharge** on the contactor. At 12 V with FRC loads it's the same event as closing a main breaker.
- **Never switch the negative.** Grounds are common; only +12 V goes through the contactor.
- **Storage:** flip the main breaker off. Standby draws about 2 W (4-5 W with a Pi camera).

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
- **ESP32-S3 WiFi bridge:** serves the gzipped web UI from flash and runs the WebSocket at 20-50 Hz.
  The browser does the heavy work (robot rendering, trajectory). Fine for a rich UI; limit is about
  4-8 clients and 2.4 GHz only.
- **Trajectory math goes in the browser.** The dashboard already has the angle and chamber pressure, and
  it's where the aim arc gets drawn. The robot only receives angle and pressure setpoints.

### Camera live feed

Neither the STM32 nor the bridge should carry video. It needs its own board on the logic rail.

| Option | Cost | Video | Verdict |
|---|---|---|---|
| **Pi Zero 2 W + Camera Module 3 Wide** | about $50 | H.264 over WebRTC (MediaMTX), ~720p30, ~0.2 s lag, 120 deg | **Recommended** |
| XIAO ESP32S3 Sense | $14-20 | MJPEG, ~VGA, 10-20 fps, weak in gym light, one viewer | Cheapest; fine as a peek camera |
| ESP32-C5 bridge + dual-band camera Pi | +$40 or so | Same as the Pi, on 5 GHz | Only if 2.4 GHz chokes at games |

- The Pi joins the bridge's network; the dashboard embeds its stream. Video can never delay a fire command.
- On the logic rail it boots once (~25 s) when the main breaker goes on, so it's ready before you arm.
  Control is still up in under 3 s.
- Mount it on the gun mantlet so the aim overlay moves with the barrels.
- **Test 2.4 GHz before buying anything:** take one of your ESP32-S3s to a game, run an AP with a
  WebSocket ping page, and check the round trip stays under ~50 ms. If it doesn't, the ESP32-C5
  (Waveshare boards, $8-14) runs a 5 GHz access point on channels 36-48 with the same code.
- ESP-NOW (safety node) stays on 2.4 GHz. Use long-range mode and send heartbeats every 20 ms so a
  200 ms trip needs about 10 lost packets in a row.

## Power budget (estimates)

| Load | Average | Peak | Side |
|---|---|---|---|
| Logic rail (STM32, 2 x ESP32-S3, sensors) | 0.2 A | 0.5 A | always on |
| + Pi Zero 2 W camera | +0.25 A | +0.5 A | always on |
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
