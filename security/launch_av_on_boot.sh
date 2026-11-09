#!/usr/bin/env bash
# DISABLED: do not install, enable or start privileged Pandora services.
# The historical implementation changed systemd configuration under sudo
# without an independently reviewed deployment / rollback procedure.
set -euo pipefail
echo "Pandora antivirus autostart is disabled pending administrator review." >&2
exit 1
