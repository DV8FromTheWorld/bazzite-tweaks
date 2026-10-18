#!/usr/bin/bash
# Install (or update) every tweak in this repo. Safe to re-run.
# Usage: sudo ./install.sh
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
    echo "Run with sudo: sudo $0" >&2
    exit 1
fi

REPO="$(cd "$(dirname "$0")" && pwd)"

echo "== controller-wakeup"
install -m 644 "$REPO/controller-wakeup/99-controller-wakeup.rules" /etc/udev/rules.d/
udevadm control --reload
udevadm trigger --subsystem-match=usb --action=add

echo "== desktop-hotkey"
install -m 755 "$REPO/desktop-hotkey/desktop-hotkey.py" /usr/local/bin/desktop-hotkey
install -m 644 "$REPO/desktop-hotkey/desktop-hotkey.service" /etc/systemd/user/
# Enable for every user, starting at their next login
systemctl --global enable desktop-hotkey.service
# Start (or restart, to pick up updates) for the user who ran sudo, if logged in
if [[ -n "${SUDO_USER:-}" ]]; then
    systemctl --user -M "$SUDO_USER@" daemon-reload &&
        systemctl --user -M "$SUDO_USER@" restart desktop-hotkey.service ||
        echo "   (not started now; it will start at next login)"
fi

echo "Done."
