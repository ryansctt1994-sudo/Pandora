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


@pytest.mark.parametrize(
    "module_name,class_name",
    [
        ("security.antiviral_firewall", "AntiviralFirewall"),
        ("security.fluid_firewall", "FluidFirewall"),
    ],
)
def test_legacy_firewall_constructors_fail_closed(module_name, class_name, monkeypatch):
    import importlib
    import os
    import subprocess

    module = importlib.import_module(module_name)
    assert module.SECURITY_STATUS == "DISABLED_UNVERIFIED"

    def forbidden(*args, **kwargs):
        raise AssertionError("A host command was invoked")
    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(os, "system", forbidden)
    with pytest.raises(RuntimeError, match="disabled"):
        getattr(module, class_name)()


@pytest.mark.parametrize(
    "module_name,class_name,method_name",
    [
        ("security.antiviral_firewall", "AntiviralFirewall", "enable_linux_firewall"),
        ("security.antiviral_firewall", "AntiviralFirewall", "activate_lockdown"),
        ("security.antiviral_firewall", "AntiviralFirewall", "quarantine_file"),
        ("security.fluid_firewall", "FluidFirewall", "_apply_port_rules"),
        ("security.fluid_firewall", "FluidFirewall", "randomize_ports"),
        ("security.fluid_firewall", "FluidFirewall", "randomize_rules"),
        ("security.fluid_firewall", "FluidFirewall", "freeze"),
        ("security.fluid_firewall", "FluidFirewall", "shutdown"),
    ],
)
def test_legacy_mutation_entrypoints_remain_disabled(module_name, class_name, method_name):
    import importlib
    module = importlib.import_module(module_name)
    obj = object.__new__(getattr(module, class_name))
    method = getattr(obj, method_name)
    args = ("example.txt",) if method_name == "quarantine_file" else ()
    with pytest.raises(RuntimeError, match="disabled"):
        method(*args)


def test_autostart_script_refuses_to_change_system_services():
    import subprocess
    from pathlib import Path
    script = Path(__file__).resolve().parents[1] / "security" / "launch_av_on_boot.sh"
    result = subprocess.run(
        ["bash", str(script)], capture_output=True, text=True, timeout=5
    )
    assert result.returncode != 0
    assert "disabled" in result.stderr.lower()


def test_scanner_launcher_does_not_sudo_start_daemon(monkeypatch):
    import os
    from security.antivirus_launcher import try_start_clamd

    def forbidden(*args, **kwargs):
        raise AssertionError("Privileged service management attempted")
    monkeypatch.setattr(os, "system", forbidden)
    assert try_start_clamd() is False
