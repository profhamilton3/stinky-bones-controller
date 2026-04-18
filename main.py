# ============================================================
# Stinky Bones — joystick:bit Radio Controller
# ============================================================
# Hardware: micro:bit v2 + Elecfreaks joystick:bit
#
# The joystick:bit plugs into the micro:bit edge connector.
# It provides an analog thumbstick (X/Y axes, 0-1023) and
# four action buttons on pins P12, P13, P14, and P15.
# It also has a small vibration motor for haptic feedback.
#
# ── JOYSTICK CONTROLS ─────────────────────────────────────
# Push UP    (Y >= 800)  → dog moves forward       (cmd 5)
# Push LEFT  (X <= 200)  → dog turns left          (cmd 6)
# Push RIGHT (X >= 800)  → dog turns right         (cmd 7)
# Push DOWN  (Y <= 200)  → dog moves backward      (cmd 8)
#
# ── BUTTON CONTROLS ───────────────────────────────────────
# P12 button  → start searching                    (cmd 1)
# P13 button  → stop / sit down                    (cmd 2)
# P14 button  → stand up                           (cmd 3)
# P15 button  → force victory dance (test)         (cmd 4)
#
# ── MICRO:BIT BUTTONS (backup controls) ───────────────────
# Button A    → start searching                    (cmd 1)
# Button B    → stop / sit down                    (cmd 2)
# Logo touch  → force victory dance (test)         (cmd 4)
#
# ── RADIO PROTOCOL ────────────────────────────────────────
# Group 3. Sends numbers 1-8. Receives 16-byte buffer from
# the XGO dog (see stinky-bones-xgo/main.py for layout).
#
# ── VIBRATION FEEDBACK ────────────────────────────────────
# Short buzz when a joystick:bit button is pressed.
# Quick double-buzz when telemetry arrives from the dog.
# ============================================================


# ────────────────────────────────────────────────────────────
# CONSTANTS
# ────────────────────────────────────────────────────────────
RADIO_GROUP = 3

# Joystick threshold — readings outside the center zone
# (512 ± ~300) are treated as intentional pushes.
# Lower = more sensitive; raise if commands fire accidentally.
# Based on pattern from profhamilton3/joystickbit-rockervalues:
#   pushed left/down: <= 200
#   pushed right/up:  >= 800
JOY_LO = 200    # below this = pushed left or down
JOY_HI = 800    # above this = pushed right or up

# Minimum time between joystick move commands.
# Prevents flooding the dog while the stick is held.
SEND_INTERVAL_MS = 400


# ────────────────────────────────────────────────────────────
# STATE VARIABLES
# ────────────────────────────────────────────────────────────
last_send_time = 0     # time of last joystick command sent

# Latest telemetry received from the dog
last_mag_x = 0
last_mag_y = 0
last_mag_z = 0
last_sonar = 0
last_dog_state = 0

# Track previous joystick positions to detect movement
# (pattern from profhamilton3/mecanumcontroller)
joy_x_center = 512
joy_y_center = 512


# ────────────────────────────────────────────────────────────
# HARDWARE INITIALISATION
# ────────────────────────────────────────────────────────────
radio.set_group(RADIO_GROUP)

# joystick:bit must be initialised before use
joystickbit.init_joystick_bit()

# Capture the true center/neutral position of this specific stick
# (each unit may sit slightly off 512 at rest)
joy_x_center = joystickbit.get_rocker_value(joystickbit.rockerType.X)
joy_y_center = joystickbit.get_rocker_value(joystickbit.rockerType.Y)

# Startup haptic + display
joystickbit.Vibration_Motor(200)
basic.show_icon(IconNames.ARROW_NORTH)


# ────────────────────────────────────────────────────────────
# HELPER: send a command with haptic + LED feedback
# ────────────────────────────────────────────────────────────

def send_cmd(cmd: number, icon):
    """Send a radio command, show an icon, buzz the motor."""
    radio.send_number(cmd)
    basic.show_icon(icon)
    joystickbit.Vibration_Motor(60)


# ────────────────────────────────────────────────────────────
# joystick:bit BUTTON EVENT HANDLERS (P12–P15)
# ────────────────────────────────────────────────────────────

# P12 — start searching
def on_p12():
    send_cmd(1, IconNames.HAPPY)
    basic.pause(200)
    basic.show_icon(IconNames.ARROW_NORTH)
joystickbit.on_button_event(
    joystickbit.JoystickBitPin.P12,
    joystickbit.ButtonType.DOWN,
    on_p12
)

# P13 — stop and sit
def on_p13():
    send_cmd(2, IconNames.ASLEEP)
    basic.pause(200)
    basic.show_icon(IconNames.ARROW_NORTH)
joystickbit.on_button_event(
    joystickbit.JoystickBitPin.P13,
    joystickbit.ButtonType.DOWN,
    on_p13
)

# P14 — stand up
def on_p14():
    send_cmd(3, IconNames.YES)
    basic.pause(200)
    basic.show_icon(IconNames.ARROW_NORTH)
joystickbit.on_button_event(
    joystickbit.JoystickBitPin.P14,
    joystickbit.ButtonType.DOWN,
    on_p14
)

# P15 — force victory dance (testing / demo)
def on_p15():
    send_cmd(4, IconNames.DIAMOND)
    basic.pause(200)
    basic.show_icon(IconNames.ARROW_NORTH)
joystickbit.on_button_event(
    joystickbit.JoystickBitPin.P15,
    joystickbit.ButtonType.DOWN,
    on_p15
)


# ────────────────────────────────────────────────────────────
# MICRO:BIT BUTTON BACKUPS (A / B / Logo)
# ────────────────────────────────────────────────────────────

def on_button_a():
    send_cmd(1, IconNames.HAPPY)
    basic.pause(200)
    basic.show_icon(IconNames.ARROW_NORTH)
input.on_button_pressed(Button.A, on_button_a)

def on_button_b():
    send_cmd(2, IconNames.ASLEEP)
    basic.pause(200)
    basic.show_icon(IconNames.ARROW_NORTH)
input.on_button_pressed(Button.B, on_button_b)

def on_logo_pressed():
    send_cmd(4, IconNames.DIAMOND)
    basic.pause(200)
    basic.show_icon(IconNames.ARROW_NORTH)
input.on_logo_event(TouchButtonEvent.PRESSED, on_logo_pressed)


# ────────────────────────────────────────────────────────────
# INCOMING TELEMETRY FROM XGO DOG
# ────────────────────────────────────────────────────────────

def on_radio_buffer(buf: Buffer):
    """Receive 16-byte sensor snapshot from the XGO dog.

    Buffer layout (INT16_LE, 2 bytes each):
      offset 0  mag_x    offset 6  accel_x   offset 12 sonar_cm
      offset 2  mag_y    offset 8  accel_y   offset 14 dog_state
      offset 4  mag_z    offset 10 accel_z
    """
    global last_mag_x, last_mag_y, last_mag_z
    global last_sonar, last_dog_state
    if len(buf) >= 16:
        last_mag_x   = buf.get_number(NumberFormat.INT16_LE, 0)
        last_mag_y   = buf.get_number(NumberFormat.INT16_LE, 2)
        last_mag_z   = buf.get_number(NumberFormat.INT16_LE, 4)
        last_sonar   = buf.get_number(NumberFormat.INT16_LE, 12)
        last_dog_state = buf.get_number(NumberFormat.INT16_LE, 14)
        # Double-buzz to confirm telemetry arrived
        joystickbit.Vibration_Motor(40)
        basic.pause(80)
        joystickbit.Vibration_Motor(40)
        # Flash bottom-left LED
        led.plot(0, 4)
        basic.pause(60)
        led.unplot(0, 4)
radio.on_received_buffer(on_radio_buffer)


# ────────────────────────────────────────────────────────────
# MAIN LOOP — joystick-to-steer
# ────────────────────────────────────────────────────────────

def on_forever():
    """Read the joystick and send directional commands.

    Joystick values range from 0 to 1023. Center is ~512.
    We use threshold constants (JOY_LO / JOY_HI) to define
    the "pushed" zone on each axis:

       Y >= JOY_HI  →  push UP   →  dog moves forward  (cmd 5)
       X <= JOY_LO  →  push LEFT →  dog turns left      (cmd 6)
       X >= JOY_HI  →  push RIGHT→  dog turns right     (cmd 7)
       Y <= JOY_LO  →  push DOWN →  dog moves backward  (cmd 8)

    Rate limiting (SEND_INTERVAL_MS) prevents command flooding
    while the stick is held in position.
    """
    global last_send_time
    now = input.running_time()

    # Enforce rate limit before reading the joystick
    if now - last_send_time < SEND_INTERVAL_MS:
        basic.pause(50)
        return

    jx = joystickbit.get_rocker_value(joystickbit.rockerType.X)
    jy = joystickbit.get_rocker_value(joystickbit.rockerType.Y)

    if jy >= JOY_HI:
        # Joystick pushed up → move forward
        radio.send_number(5)
        basic.show_icon(IconNames.ARROW_NORTH)
        last_send_time = now
    elif jy <= JOY_LO:
        # Joystick pushed down → move backward
        radio.send_number(8)
        basic.show_icon(IconNames.ARROW_SOUTH)
        last_send_time = now
    elif jx <= JOY_LO:
        # Joystick pushed left → turn left
        radio.send_number(6)
        basic.show_icon(IconNames.ARROW_WEST)
        last_send_time = now
    elif jx >= JOY_HI:
        # Joystick pushed right → turn right
        radio.send_number(7)
        basic.show_icon(IconNames.ARROW_EAST)
        last_send_time = now
    else:
        # Stick at rest / center zone — show neutral arrow
        basic.show_icon(IconNames.ARROW_NORTH)

    basic.pause(50)

basic.forever(on_forever)
