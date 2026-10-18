#!/usr/bin/python3
"""Switch from Gaming Mode to Desktop Mode when Ctrl+Alt+Shift+Delete is pressed.

Watches every keyboard directly (works even when the TV is off), so it
doesn't depend on gamescope or Steam handling the shortcut. Only the
combo is checked; no keystrokes are recorded.
"""
import selectors
import subprocess
import time

import evdev
from evdev import ecodes as e

# Each entry is a set of interchangeable keys (left or right modifier).
COMBO = [
    {e.KEY_LEFTCTRL, e.KEY_RIGHTCTRL},
    {e.KEY_LEFTALT, e.KEY_RIGHTALT},
    {e.KEY_LEFTSHIFT, e.KEY_RIGHTSHIFT},
    {e.KEY_DELETE},
]
RESCAN_SECONDS = 5


def in_gaming_mode():
    # Gaming Mode runs as this user service; checking it is more reliable than
    # looking for a gamescope process (gamescope renames its threads).
    result = subprocess.run(
        ["systemctl", "--user", "list-units", "--state=active", "--plain",
         "--no-legend", "gamescope-session-plus@*"],
        capture_output=True, text=True,
    )
    return bool(result.stdout.strip())


def switch_to_desktop():
    print("Combo pressed, switching to Desktop Mode", flush=True)
    subprocess.run(["steamosctl", "switch-to-desktop-mode"])


def is_keyboard(dev):
    keys = dev.capabilities().get(e.EV_KEY, [])
    return e.KEY_DELETE in keys and e.KEY_LEFTCTRL in keys


def main():
    sel = selectors.DefaultSelector()
    watched = {}  # path -> device
    pressed = set()
    next_scan = 0

    while True:
        # Pick up keyboards that were plugged in or woke up since the last scan.
        if time.monotonic() >= next_scan:
            for path in evdev.list_devices():
                if path in watched:
                    continue
                try:
                    dev = evdev.InputDevice(path)
                except OSError:
                    continue
                if is_keyboard(dev):
                    sel.register(dev, selectors.EVENT_READ)
                    watched[path] = dev
                    print(f"Watching {dev.name} ({path})", flush=True)
                else:
                    dev.close()
            next_scan = time.monotonic() + RESCAN_SECONDS

        for key, _ in sel.select(timeout=RESCAN_SECONDS):
            dev = key.fileobj
            try:
                events = list(dev.read())
            except OSError:
                # Device unplugged.
                sel.unregister(dev)
                watched.pop(dev.path, None)
                pressed.clear()
                continue
            for ev in events:
                if ev.type != e.EV_KEY:
                    continue
                if ev.value == 1:
                    pressed.add(ev.code)
                    if all(pressed & group for group in COMBO):
                        if in_gaming_mode():
                            switch_to_desktop()
                        else:
                            print("Combo pressed, but not in Gaming Mode; ignoring", flush=True)
                elif ev.value == 0:
                    pressed.discard(ev.code)


if __name__ == "__main__":
    main()
