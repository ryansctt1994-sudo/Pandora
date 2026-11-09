"""Quarantine tests: firewall code must not mutate host networking.

This experimental module is not malware protection. No tests run UFW or
start a live watcher; all dangerous side effects are replaced by sentinels.
"""

import pytest

from security import quantum_mirror_firewall as firewall


def test_firewall_is_explicitly_disabled():
    assert firewall.SECURITY_STATUS == "DISABLED_UNVERIFIED"


def test_direct_cycle_cannot_call_ufw(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Host command execution attempted")
    monkeypatch.setattr(firewall.subprocess, "run", forbidden)
    observer = firewall.QuantumMirrorFirewallObserver()
    with pytest.raises(RuntimeError, match="disabled"):
        observer.quantum_firewall_cycle()


def test_start_cannot_spawn_watchers_or_execute_shell(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Host side effect attempted")
    monkeypatch.setattr(firewall.subprocess, "run", forbidden)
    monkeypatch.setattr(firewall.threading.Thread, "start", forbidden)
    observer = firewall.QuantumMirrorFirewallObserver()
    with pytest.raises(RuntimeError, match="disabled"):
        observer.start()


def test_quantum_port_is_not_a_security_random_source(monkeypatch):
    source = firewall.QuantumRandomizer(bits=2)
    def forbidden(*args, **kwargs):
        raise AssertionError("Unverified random source used")
    monkeypatch.setattr(source.processor, "apply_gate", forbidden)
    monkeypatch.setattr(source.processor, "measure", forbidden)
    with pytest.raises(RuntimeError, match="disabled"):
        source.quantum_port()


def test_scanner_absence_is_not_presented_as_protection():
    # A future scanner implementation must not silently activate the
    # quarantined firewall. Activation requires a separate reviewed PR.
    assert firewall.SECURITY_STATUS != "ACTIVE"
    if firewall.scan_with_all is None:
        assert firewall.any_infected is None
