# Bazzite tweaks

Custom changes for a Bazzite PC, kept in one place so they can be reinstalled
on a new machine, updated, or undone.

## Install / update / uninstall

    sudo ./install.sh      # install everything
    sudo ./uninstall.sh    # remove everything

Both are safe to run as many times as you like. To **update** after editing
anything in this folder (or pulling new changes), just run `sudo ./install.sh`
again: it overwrites the installed copies and restarts what needs restarting.

Run them from your normal user with `sudo` (not from a root shell), so the
scripts know which user's session to start/stop the hotkey service in.

### Where things get installed

The repo itself can live anywhere; install copies files out of it. Bazzite
updates don't touch `/etc` or `/usr/local`, so these survive OS updates.

| Tweak | Installed to |
|---|---|
| controller-wakeup | `/etc/udev/rules.d/99-controller-wakeup.rules` |
| desktop-hotkey | `/usr/local/bin/desktop-hotkey`, `/etc/systemd/user/desktop-hotkey.service` |

## controller-wakeup

Lets the Xbox 360 wireless receiver and the Pico 2 W dongles (DS5Dongle /
DS4Dongle) wake the PC from sleep.

Linux keeps a per-device "allowed to wake the PC" switch at
`/sys/bus/usb/devices/<device>/power/wakeup`. It's off for these devices by
default and resets on every boot. `99-controller-wakeup.rules` is a udev rule:
whenever one of these devices is plugged in (including at boot), udev turns that
switch on. It's the same approach Bazzite uses for Steam Controllers
(`/usr/lib/udev/rules.d/99-steamcontroller-wakeup.rules`).

Devices covered (by USB ID): Xbox 360 receiver `045e:0719`, DS5Dongle
`054c:0ce6` / `054c:0df2` (Edge mode), DS4Dongle `054c:09cc`. To add another
device, find its ID with `lsusb`, add a line to the rule, re-run install.

The Pico dongles also need wake turned on in their own firmware settings
(off by default):
- DS5Dongle: https://ds5.awalol.eu.org -> "Wake PC from sleep on PS button" -> Reconnect USB
- DS4Dongle: `tools/config_tool.py fields` to find the wake-on-PS setting, then `set <name>=1`

Check it worked: `grep . /sys/bus/usb/devices/*/power/wakeup` and look for
`enabled` next to the device (`lsusb -t` shows which port is which).

If nothing wakes the PC, check the BIOS: USB ports must stay powered in sleep
(on ASRock, ErP should be disabled).

Tested results:
- Xbox 360 receiver: the controller's Guide button does **not** wake the PC.
  The receiver's radio appears to shut off while USB is suspended. Pressing the
  **sync button on the receiver itself** does wake it.

## desktop-hotkey

Ctrl+Alt+Shift+Delete in Gaming Mode switches to Desktop Mode, so you don't need
the TV on. A small script listens to the keyboards directly and runs
`steamosctl switch-to-desktop-mode`. It does nothing in Desktop Mode, and only
checks for the combo; it doesn't record keystrokes.

Logs: `journalctl --user -u desktop-hotkey -f`
