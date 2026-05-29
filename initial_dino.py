# Got 24781 with this code:
import pyautogui
import time
from PIL import Image
import mss

# ==============================
# CONFIG
# ==============================
BASE_X = 260
BASE_Y = 760
SCAN_HEIGHT = 80
MAX_OFFSET = 270  # original 250
SENSITIVITY_THRESHOLD = 70

FOOT_PIXEL_X = 88
FOOT_PIXEL_Y = 830

sct = mss.mss()
start_time = time.perf_counter()


class State:
    GROUND = 0
    JUMP = 1
    AIR = 2


# ==============================
# INPUT LAYER (Single Source of Truth)
# ==============================
is_down_pressed = False


def set_down(active):
    global is_down_pressed
    if active and not is_down_pressed:
        pyautogui.keyDown("down")
        is_down_pressed = True
    elif not active and is_down_pressed:
        pyautogui.keyUp("down")
        is_down_pressed = False


def jump(hold):
    pyautogui.keyDown("space")
    time.sleep(hold)
    pyautogui.keyUp("space")


# ==============================
# DETECTION
# ==============================
def check_grounded(bg):
    px = sct.grab({"top": FOOT_PIXEL_Y, "left": FOOT_PIXEL_X, "width": 1, "height": 1})
    r, g, b = px.pixel(0, 0)
    gray = (r + g + b) // 3
    return abs(gray - bg) > 50


# Version 1 Strategic Simplification Scanner
def scan(img):
    w, h = img.size
    g = img.convert("L")
    px = g.load()

    bg = px[0, 0]
    threats = []
    last_x = -99

    for x in range(0, w, 5):
        if x < last_x + 20:
            continue

        hit_y = -1
        for y in range(0, h, 5):
            if abs(px[x, y] - bg) > SENSITIVITY_THRESHOLD:
                # Basic noise filter: must be at least 5px wide to be a threat
                if x + 5 < w and abs(px[x + 5, y] - bg) > SENSITIVITY_THRESHOLD:
                    hit_y = y
                    break

        if hit_y == -1:
            continue

        # 1. THE "ROOT" CHECK
        # We look for a connection to the ground.
        is_grounded = False
        for check_x in range(x - 5, x + 15, 5):
            if 0 <= check_x < w:
                for gy in range(h - 1, h - 21, -5):
                    if abs(px[check_x, gy] - bg) > SENSITIVITY_THRESHOLD:
                        is_grounded = True
                        break
            if is_grounded: break

        # 2. THE "WING" CHECK (Only if not grounded)
        # If it's not touching the ground, is it wide enough to be a bird?
        # Cacti arms are usually < 15px wide. Bird wings are > 25px.
        is_bird = False
        if not is_grounded:
            # Check 25 pixels ahead. If we still see "meat", it's a wing.
            wing_sample_x = x + 25
            if wing_sample_x < w:
                # Check a small vertical slice where the wing should be
                for wy in range(max(0, hit_y - 10), min(h, hit_y + 15), 5):
                    if abs(px[wing_sample_x, wy] - bg) > SENSITIVITY_THRESHOLD:
                        is_bird = True
                        break
        # 3. CLASSIFICATION (JUMP OVER EVERYTHING VERSION)
        if hit_y < 15:
            # OVERRIDE: A 4-cactus group is very wide and tricks the "wing check"
            # into returning True. But if it's this high in the scan box,
            # it is the top of a tall cactus arm. Force it to be a cactus.
            threats.append(("cactus", x, hit_y))
        elif is_grounded:
            threats.append(("cactus", x, hit_y))
        elif is_bird:
            threats.append(("cactus", x, hit_y))  # bird
        else:
            # Fallback: If it's somewhat high but NOT wide enough to be a bird,
            # it's a single tall cactus arm.
            if hit_y < 25:
                threats.append(("cactus", x, hit_y))
            else:
                threats.append(("cactus", x, hit_y))  # bird

        last_x = x

    return threats, bg


# ==============================
# MAIN LOOP
# ==============================
def main():
    pyautogui.PAUSE = 0
    print("🚀 FINAL HYBRID ENGINE ONLINE")
    time.sleep(3)

    state = State.GROUND
    state_start = 0

    # 1. SETUP DECISION MEMORY (Outside the loop!)
    decision = None
    decision_until = 0

    duck_until = 0
    duck_lock_until = 0
    jump_lock = 0
    last_jump = 0
    next_jump_queued = False

    while True:
        now = time.perf_counter()
        elapsed = now - start_time
        speed = min(1.0, elapsed / 45)

        # ==============================
        # GAME MODES
        # ==============================
        if elapsed < 58:
            mode = "early_a"
            SCAN_WIDTH = 260
            JUMPER = 0.015
        elif elapsed < 99:  # ORIGINAL 90
            mode = "early_b"
            SCAN_WIDTH = 290  # original 260
            JUMPER = 0.012
        else:
            mode = "mid"
            SCAN_WIDTH = 400  # original 300, 370
            JUMPER = 0.008  # Increased from 0.001 to ensure registration

        # ==============================
        # VISION OFFSET CALCULATION
        # ==============================
        if mode == "early_a":
            # 0 offset: Scan starts exactly at BASE_X
            # forward = 105
            # This handles the slight acceleration before the 60s mark.
            forward = 105 + int(speed * 20)
        elif mode == "early_b":
            # Transitional offset
            forward = int(MAX_OFFSET * (0.6 * speed + 0.4 * (speed ** 2)))
        else:
            # Mid-game aggressive offset
            forward = int(MAX_OFFSET * (0.9 * speed + 0.9 * (speed ** 2)))

        # ==============================
        # VISION
        # ==============================
        region = {
            "top": BASE_Y,
            "left": BASE_X + forward,
            "width": SCAN_WIDTH,
            "height": SCAN_HEIGHT
        }

        raw = sct.grab(region)
        img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
        threats, bg = scan(img)

        # ==============================
        # GROUND CHECK
        # ==============================
        is_grounded = check_grounded(bg) if (now - last_jump > 0.18) else False

        # ==============================
        # EARLY A (PURE REFLEX)
        # ==============================
        if mode == "early_a":
            if not is_grounded:
                state = State.AIR
                continue
            else:
                state = State.GROUND

            if threats:
                # We no longer care if it's 't == cactus' or 't == bird'
                _, d, _ = threats[0]

                # If ANYTHING enters the kill-zone, we jump.
                if d < 175:
                    duck_until = 0
                    set_down(False)
                    jump(JUMPER)
                    last_jump = now
                    state = State.JUMP

        # ==============================
        # EARLY B (TRANSITION)
        # ==============================
        elif mode == "early_b":
            # state = State.GROUND
            # next_jump_queued = False
            if not is_grounded:
                state = State.AIR

            else:
                state = State.GROUND

            # 2. THE GATEKEEPER: If locked, enforce decision and skip scanning
            if now < decision_until:
                if decision == "duck":
                    set_down(True)
                elif decision == "jump":
                    set_down(False)  # Ensure we aren't ducking mid-jump
                continue  # SKIPS TO THE NEXT FRAME IMMEDIATELY!

            if threats:

                bird = None
                cactus = None

                for t, x, y in threats:
                    if t == "bird" and bird is None:
                        bird = (t, x, y)
                    elif t == "cactus" and cactus is None:
                        cactus = (t, x, y)

                threat = bird if bird else cactus

                # t, d, _ = threats[0]
                t, d, y = threat

                if t == "cactus" and now > jump_lock and is_grounded:
                    if d < 270:  # original was 180
                        # IGNORE fake cactus during active bird duck
                        if decision == "duck" and now < decision_until:
                            continue

                        else:
                            # 1. PURIFY THE STATE
                            duck_until = 0
                            set_down(False)

                            # 2. THEN JUMP
                            if is_grounded:
                                jump(JUMPER)
                                last_jump = now
                                jump_lock = now + 0.12

                                # chain awareness (light)
                                if len(threats) > 1:
                                    gap = threats[1][1] - d
                                    if 60 < gap < 200:
                                        next_jump_queued = True


                elif t == "bird" and is_grounded:

                    # 1. SET THE DECISION LOCK
                    decision = "duck"
                    decision_until = now + 0.35  # Lock the brain for 350ms
                    set_down(True)

        # ==============================
        # MID GAME (CHAIN-AWARE FSM)
        # ==============================
        else:
            # ==============================
            # HARD STATE SYNC
            # ==============================
            # NEW: Landing Lock. If we are within the jump lock window,
            # it is physically impossible to be grounded. Ignore the sensor.
            landing_lock = now < jump_lock

            if is_grounded and not landing_lock:
                if state != State.GROUND:
                    state = State.GROUND
                    state_start = now  # CRITICAL: Reset state_start so we can track ground time

            elif state != State.JUMP:
                state = State.AIR

            # ==============================
            # MID GAME FSM
            # ==============================
            if state == State.AIR:

                # 🔥 IMPROVED RHYTHM SYSTEM
                if threats:
                    # Look at the VERY FIRST incoming threat
                    d = threats[0][1]

                    # If any obstacle is within 'rebound' range while we are mid-air,
                    # queue the jump. This covers the 3rd obstacle in a 3-chain.

                    if elapsed < 120:
                        rebound_range = 340
                        if 120 < d < rebound_range:
                            next_jump_queued = True
                            # FAST FALL (Non-blocking)
                            # We push down here to snap to the ground faster for the next jump
                            duck_until = now + min(0.12, 0.05 + speed * 0.02)

                    elif elapsed < 240:
                        rebound_range = 380
                        if 120 < d < rebound_range:
                            next_jump_queued = True
                            # FAST FALL (Non-blocking)
                            # We push down here to snap to the ground faster for the next jump
                            duck_until = now + min(0.12, 0.05 + speed * 0.02)

                    else:
                        rebound_range = 430
                        if 120 < d < rebound_range:
                            next_jump_queued = True
                            # FAST FALL (Non-blocking)
                            # We push down here to snap to the ground faster for the next jump
                            duck_until = now + min(0.12, 0.05 + speed * 0.02)

                    # Optional: Still check for tight gaps between multiple future threats
                    if len(threats) > 1:
                        gap = threats[1][1] - d
                        # if gap < (120 + int(speed * 90)):
                        if 40 < gap < (120 + int(speed * 90)):
                            next_jump_queued = True
                            # FAST FALL (Non-blocking)
                            duck_until = now + min(0.12, 0.05 + speed * 0.02)

            elif state == State.GROUND:
                # The millisecond we land, release the fast-fall
                if is_down_pressed and now > duck_until:
                    set_down(False)

                # 1. FORCED REBOUND: If a jump was queued while airborne, take it now.
                if next_jump_queued:
                    # NEW: Critical release buffer
                    if is_down_pressed:
                        set_down(False)
                        time.sleep(0.01)  # Gives the game 10ms to register "Not Ducking"

                    duck_until = 0
                    set_down(False)  # Ensure we aren't ducking before the rebound jump
                    jump(JUMPER)
                    last_jump = now
                    next_jump_queued = False
                    state = State.JUMP
                    state_start = now
                    # Keep lock minimal for chains
                    jump_lock = now + 0.15  # Slightly increased from 0.12


                elif threats:

                    bird = None
                    cactus = None

                    for t, x, y in threats:
                        if t == "bird" and bird is None:
                            bird = (t, x, y)
                        elif t == "cactus" and cactus is None:
                            cactus = (t, x, y)

                    # threat = bird if bird else cactus

                    # PICK THE CLOSEST THREAT, PERIOD. (JUMP OVER EVERYTHING STRATEGY)
                    threat = min(threats, key=lambda t: t[1])

                    # t, d, _ = threats[0]
                    t, d, y = threat

                    if t == "cactus" and now > jump_lock:

                        if elapsed < 120:
                            trigger = 265

                        elif elapsed < 240:
                            trigger = 320

                        else:
                            trigger = 350  # 350
                        # 1. PURIFY THE STATE
                        duck_until = 0
                        set_down(False)

                        # 2. THEN JUMP
                        if d < trigger:
                            jump(JUMPER)
                            last_jump = now
                            state = State.JUMP
                            state_start = now
                            jump_lock = now + 0.18

                    elif t == "bird":
                        duck_until = now + 0.3



            elif state == State.JUMP:
                if now - state_start > 0.18:  # 0.18
                    state = State.AIR

        # ==============================
        # OUTPUT LAYER (CLEAN VERSION)
        # ==============================

        # 1. Decision system has priority
        if now < decision_until:
            if decision == "duck":
                set_down(True)
            elif decision == "jump":
                set_down(False)

        # 2. Only when NO decision is active, allow mid-game duck logic
        else:
            if mode == "mid":
                set_down(now < duck_until)
            else:
                # early game: default safe state
                set_down(False)


if __name__ == "__main__":
    main()
 