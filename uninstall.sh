#!/usr/bin/bash
# Remove every tweak in this repo. Safe to re-run.
# Usage: sudo ./uninstall.sh
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
    echo "Run with sudo: sudo $0" >&2
    exit 1
fi

echo "== desktop-hotkey"
if [[ -n "${SUDO_USER:-}" ]]; then
    systemctl --user -M "$SUDO_USER@" stop desktop-hotkey.service 2>/dev/null || true
fi
systemctl --global disable desktop-hotkey.service 2>/dev/null || true
rm -f /etc/systemd/user/desktop-hotkey.service /usr/local/bin/desktop-hotkey
if [[ -n "${SUDO_USER:-}" ]]; then
    systemctl --user -M "$SUDO_USER@" daemon-reload 2>/dev/null || true
fi

echo "== controller-wakeup"
rm -f /etc/udev/rules.d/99-controller-wakeup.rules
udevadm control --reload
echo "   (devices keep wake enabled until the next reboot)"

echo "Done."
