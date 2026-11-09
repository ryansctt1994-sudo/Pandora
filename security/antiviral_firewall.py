"""AntiviralFirewall quarantine: host/network mutation is disabled.

The historical prototype could enable UFW, change default policies and
quarantine files from an unvalidated scan. It is not an antivirus product.
The earlier source remains in repository history for design review.
"""

SECURITY_STATUS = "DISABLED_UNVERIFIED"


class AntiviralFirewall:
    """Fail closed until scanning, quarantine and firewall policies are reviewed."""

    def __init__(self, log_path="pandora_security.log"):
        self.log_path = log_path
        self._disabled()

    @staticmethod
    def _disabled():
        raise RuntimeError(
            "Pandora AntiviralFirewall is disabled: no validated scanner "
            "or approved host firewall policy is installed."
        )

    def enable_linux_firewall(self):
        self._disabled()

    def check_clamav_loaded(self):
        self._disabled()

    def scan_file(self, path):
        self._disabled()

    def quarantine_file(self, path):
        self._disabled()

    def audit_suspicious_behavior(self, event, severity="medium"):
        self._disabled()

    def activate_lockdown(self):
        self._disabled()


if __name__ == "__main__":
    raise SystemExit("Pandora AntiviralFirewall is disabled pending security review.")
