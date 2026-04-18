# Stinky Bones — joystick:bit Radio Controller

> **THE Hamilton Essentials Foundation** | STEAM Coding Curriculum

A micro:bit v2 + Elecfreaks joystick:bit controller that steers the XGO dog
over radio. Use the analog thumbstick to drive forward, back, left, and right.
Use the four action buttons to start/stop the bone hunt and trigger special moves.

This is the **controller** half of the Stinky Bones system. Flash this onto
the joystick:bit micro:bit. Flash `stinky-bones-xgo` onto the micro:bit
mounted on the XGO dog body.

---

## Hardware Required

| Qty | Part |
|---|---|
| 1 | micro:bit v2 |
| 1 | Elecfreaks joystick:bit |
| 1 | USB cable or battery pack |

The joystick:bit plugs directly into the micro:bit edge connector — no wiring needed.

---

## Loading in MakeCode

1. Go to [makecode.microbit.org](https://makecode.microbit.org)
2. Click **Import** → **Import URL**
3. Paste: `https://github.com/profhamilton3/stinky-bones-controller`
4. MakeCode installs the `joystickbit` extension automatically
5. Click the **Python** tab
6. Click **Download** and copy the `.hex` to your MICROBIT drive

---

## Controls

### Thumbstick (Analog)

| Direction | Threshold | Sends | Dog action |
|---|---|---|---|
| Push UP | Y ≥ 800 | cmd 5 | Move forward |
| Push DOWN | Y ≤ 200 | cmd 8 | Move backward |
| Push LEFT | X ≤ 200 | cmd 6 | Turn left |
| Push RIGHT | X ≥ 800 | cmd 7 | Turn right |
| Center / rest | 200 < X/Y < 800 | (nothing) | — |

### joystick:bit Action Buttons (P12–P15)

| Button | Sends | Dog action |
|---|---|---|
| P12 (top-left) | cmd 1 | Start searching |
| P13 (bottom-left) | cmd 2 | Stop and sit |
| P14 (top-right) | cmd 3 | Stand up |
| P15 (bottom-right) | cmd 4 | Victory dance (testing) |

### micro:bit Buttons (backup)

| Input | Sends | Dog action |
|---|---|---|
| Button A | cmd 1 | Start searching |
| Button B | cmd 2 | Stop and sit |
| Logo touch | cmd 4 | Victory dance |

---

## Haptic Feedback

| Event | Vibration pattern |
|---|---|
| Action button pressed | Single 60ms buzz |
| Telemetry received from dog | Double 40ms buzz |

---

## LED Display

| Display | Meaning |
|---|---|
| Arrow North | Joystick centered / idle |
| Arrow North | Dog moving forward |
| Arrow South | Dog moving backward |
| Arrow West | Dog turning left |
| Arrow East | Dog turning right |
| Happy face | Just sent "start search" |
| Sleeping face | Just sent "stop" |
| Checkmark | Just sent "stand" |
| Diamond | Just sent "dance" |
| Bottom-left dot blink | Telemetry received |

---

## Calibration

The joystick center position is captured at startup. If commands fire when
the stick is at rest, adjust the thresholds in `main.py`:

```python
JOY_LO = 200    # below this = pushed left or down
JOY_HI = 800    # above this = pushed right or up
SEND_INTERVAL_MS = 400   # ms between commands (raise to slow repeat rate)
```

---

## Radio Group

All three microbits (dog, controller, collector) must use the same
`RADIO_GROUP`. Default is **3**. Change it if running multiple teams
in the same room.

---

## Extension Credit

joystick:bit extension: `github:tinkertanker/pxt-joystickbit#v1.0.3`

Usage references in this project:
- `profhamilton3/joystickbit-rockervalues` — joystick axis reading pattern
- `profhamilton3/mecanumcontroller` — button events + deadzone pattern

---

*THE Hamilton Essentials Foundation, Inc.*
