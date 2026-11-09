"""FluidFirewall quarantine: destructive iptables paths are disabled.

Historical behavior flushed INPUT/OUTPUT chains, set DROP/ACCEPT policies,
and randomized ports. These operations can disconnect a host and do not
constitute a validated security boundary. Historical source remains in git.
"""

SECURITY_STATUS = "DISABLED_UNVERIFIED"


class FluidFirewall:
    """Retain a recognizable API while refusing unsafe host mutation."""

    def __init__(self, monitored_pid=None, update_interval=90):
        self.running = False
        self.monitor_pid = monitored_pid
        self.update_interval = update_interval
        self._disabled()

    @staticmethod
    def _disabled():
        raise RuntimeError(
            "Pandora FluidFirewall is disabled: unreviewed host rule changes "
            "must not run on a user's network."
        )

    def start(self):
        self._disabled()

    def _randomize_loop(self):
        self._disabled()

    def randomize_ports(self):
        self._disabled()

    def _apply_port_rules(self):
        self._disabled()

    def randomize_rules(self):
        self._disabled()

    def _monitor_process(self):
        self._disabled()

    def freeze(self):
        self._disabled()

    def shutdown(self):
        self._disabled()


if __name__ == "__main__":
    raise SystemExit("Pandora FluidFirewall is disabled pending security review.")
