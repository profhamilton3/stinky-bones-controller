//  ============================================================
//  Stinky Bones — joystick:bit Radio Controller
//  ============================================================
//  Hardware: micro:bit v2 + Elecfreaks joystick:bit
// 
//  The joystick:bit plugs into the micro:bit edge connector.
//  It provides an analog thumbstick (X/Y axes, 0-1023) and
//  four action buttons on pins P12, P13, P14, and P15.
//  It also has a small vibration motor for haptic feedback.
// 
//  ── JOYSTICK CONTROLS ─────────────────────────────────────
//  Push UP    (Y >= 800)  → dog moves forward       (cmd 5)
//  Push LEFT  (X <= 200)  → dog turns left          (cmd 6)
//  Push RIGHT (X >= 800)  → dog turns right         (cmd 7)
//  Push DOWN  (Y <= 200)  → dog moves backward      (cmd 8)
// 
//  ── BUTTON CONTROLS ───────────────────────────────────────
//  P12 button  → start searching                    (cmd 1)
//  P13 button  → stop / sit down                    (cmd 2)
//  P14 button  → stand up                           (cmd 3)
//  P15 button  → force victory dance (test)         (cmd 4)
// 
//  ── MICRO:BIT BUTTONS (backup controls) ───────────────────
//  Button A    → start searching                    (cmd 1)
//  Button B    → stop / sit down                    (cmd 2)
//  Logo touch  → force victory dance (test)         (cmd 4)
// 
//  ── RADIO PROTOCOL ────────────────────────────────────────
//  Group 3. Sends numbers 1-8. Receives 16-byte buffer from
//  the XGO dog (see stinky-bones-xgo/main.py for layout).
// 
//  ── VIBRATION FEEDBACK ────────────────────────────────────
//  Short buzz when a joystick:bit button is pressed.
//  Quick double-buzz when telemetry arrives from the dog.
//  ============================================================
//  ────────────────────────────────────────────────────────────
//  CONSTANTS
//  ────────────────────────────────────────────────────────────
let RADIO_GROUP = 3
//  Joystick threshold — readings outside the center zone
//  (512 ± ~300) are treated as intentional pushes.
//  Lower = more sensitive; raise if commands fire accidentally.
//  Based on pattern from profhamilton3/joystickbit-rockervalues:
//    pushed left/down: <= 200
//    pushed right/up:  >= 800
let JOY_LO = 200
//  below this = pushed left or down
let JOY_HI = 800
//  above this = pushed right or up
//  Minimum time between joystick move commands.
//  Prevents flooding the dog while the stick is held.
let SEND_INTERVAL_MS = 400
//  ────────────────────────────────────────────────────────────
//  STATE VARIABLES
//  ────────────────────────────────────────────────────────────
let last_send_time = 0
//  time of last joystick command sent
//  Latest telemetry received from the dog
let last_mag_x = 0
let last_mag_y = 0
let last_mag_z = 0
let last_sonar = 0
let last_dog_state = 0
//  Track previous joystick positions to detect movement
//  (pattern from profhamilton3/mecanumcontroller)
let joy_x_center = 512
let joy_y_center = 512
//  ────────────────────────────────────────────────────────────
//  HARDWARE INITIALISATION
//  ────────────────────────────────────────────────────────────
radio.setGroup(RADIO_GROUP)
//  joystick:bit must be initialised before use
joystickbit.initJoystickBit()
//  Capture the true center/neutral position of this specific stick
//  (each unit may sit slightly off 512 at rest)
joy_x_center = joystickbit.getRockerValue(joystickbit.rockerType.X)
joy_y_center = joystickbit.getRockerValue(joystickbit.rockerType.Y)
//  Startup haptic + display
joystickbit.Vibration_Motor(200)
basic.showArrow(ArrowNames.North)
//  ────────────────────────────────────────────────────────────
//  HELPER: send a command with haptic + LED feedback
//  ────────────────────────────────────────────────────────────
function send_cmd(cmd: number, icon: number) {
    /** Send a radio command, show an icon, buzz the motor. */
    radio.sendNumber(cmd)
    basic.showIcon(icon)
    joystickbit.Vibration_Motor(60)
}

//  ────────────────────────────────────────────────────────────
//  joystick:bit BUTTON EVENT HANDLERS (P12–P15)
//  ────────────────────────────────────────────────────────────
//  P12 — start searching
joystickbit.onButtonEvent(joystickbit.JoystickBitPin.P12, joystickbit.ButtonType.down, function on_p12() {
    send_cmd(1, IconNames.Happy)
    basic.pause(200)
    basic.showArrow(ArrowNames.North)
})
//  P13 — stop and sit
joystickbit.onButtonEvent(joystickbit.JoystickBitPin.P13, joystickbit.ButtonType.down, function on_p13() {
    send_cmd(2, IconNames.Asleep)
    basic.pause(200)
    basic.showArrow(ArrowNames.North)
})
//  P14 — stand up
joystickbit.onButtonEvent(joystickbit.JoystickBitPin.P14, joystickbit.ButtonType.down, function on_p14() {
    send_cmd(3, IconNames.Yes)
    basic.pause(200)
    basic.showArrow(ArrowNames.North)
})
//  P15 — force victory dance (testing / demo)
joystickbit.onButtonEvent(joystickbit.JoystickBitPin.P15, joystickbit.ButtonType.down, function on_p15() {
    send_cmd(4, IconNames.Diamond)
    basic.pause(200)
    basic.showArrow(ArrowNames.North)
})
//  ────────────────────────────────────────────────────────────
//  MICRO:BIT BUTTON BACKUPS (A / B / Logo)
//  ────────────────────────────────────────────────────────────
input.onButtonPressed(Button.A, function on_button_a() {
    send_cmd(1, IconNames.Happy)
    basic.pause(200)
    basic.showArrow(ArrowNames.North)
})
input.onButtonPressed(Button.B, function on_button_b() {
    send_cmd(2, IconNames.Asleep)
    basic.pause(200)
    basic.showArrow(ArrowNames.North)
})
input.onLogoEvent(TouchButtonEvent.Pressed, function on_logo_pressed() {
    send_cmd(4, IconNames.Diamond)
    basic.pause(200)
    basic.showArrow(ArrowNames.North)
})
//  ────────────────────────────────────────────────────────────
//  INCOMING TELEMETRY FROM XGO DOG
//  ────────────────────────────────────────────────────────────
radio.onReceivedBuffer(function on_radio_buffer(buf: Buffer) {
    /** Receive 16-byte sensor snapshot from the XGO dog.

    Buffer layout (INT16_LE, 2 bytes each):
      offset 0  mag_x    offset 6  accel_x   offset 12 sonar_cm
      offset 2  mag_y    offset 8  accel_y   offset 14 dog_state
      offset 4  mag_z    offset 10 accel_z
    
 */
    
    
    if (buf.length >= 16) {
        last_mag_x = buf.getNumber(NumberFormat.Int16LE, 0)
        last_mag_y = buf.getNumber(NumberFormat.Int16LE, 2)
        last_mag_z = buf.getNumber(NumberFormat.Int16LE, 4)
        last_sonar = buf.getNumber(NumberFormat.Int16LE, 12)
        last_dog_state = buf.getNumber(NumberFormat.Int16LE, 14)
        //  Double-buzz to confirm telemetry arrived
        joystickbit.Vibration_Motor(40)
        basic.pause(80)
        joystickbit.Vibration_Motor(40)
        //  Flash bottom-left LED
        led.plot(0, 4)
        basic.pause(60)
        led.unplot(0, 4)
    }
    
})
//  ────────────────────────────────────────────────────────────
//  MAIN LOOP — joystick-to-steer
//  ────────────────────────────────────────────────────────────
basic.forever(function on_forever() {
    /** Read the joystick and send directional commands.

    Joystick values range from 0 to 1023. Center is ~512.
    We use threshold constants (JOY_LO / JOY_HI) to define
    the "pushed" zone on each axis:

       Y >= JOY_HI  →  push UP   →  dog moves forward  (cmd 5)
       X <= JOY_LO  →  push LEFT →  dog turns left      (cmd 6)
       X >= JOY_HI  →  push RIGHT→  dog turns right     (cmd 7)
       Y <= JOY_LO  →  push DOWN →  dog moves backward  (cmd 8)

    Rate limiting (SEND_INTERVAL_MS) prevents command flooding
    while the stick is held in position.
    
 */
    
    let now = input.runningTime()
    //  Enforce rate limit before reading the joystick
    if (now - last_send_time < SEND_INTERVAL_MS) {
        basic.pause(50)
        return
    }
    
    let jx = joystickbit.getRockerValue(joystickbit.rockerType.X)
    let jy = joystickbit.getRockerValue(joystickbit.rockerType.Y)
    if (jy >= JOY_HI) {
        //  Joystick pushed up → move forward
        radio.sendNumber(5)
        basic.showArrow(ArrowNames.North)
        last_send_time = now
    } else if (jy <= JOY_LO) {
        //  Joystick pushed down → move backward
        radio.sendNumber(8)
        basic.showArrow(ArrowNames.South)
        last_send_time = now
    } else if (jx <= JOY_LO) {
        //  Joystick pushed left → turn left
        radio.sendNumber(6)
        basic.showArrow(ArrowNames.West)
        last_send_time = now
    } else if (jx >= JOY_HI) {
        //  Joystick pushed right → turn right
        radio.sendNumber(7)
        basic.showArrow(ArrowNames.East)
        last_send_time = now
    } else {
        //  Stick at rest / center zone — show neutral arrow
        basic.showArrow(ArrowNames.North)
    }
    
    basic.pause(50)
})
