"""Cross-component integration gates for both reviewed repair branches.

These tests establish coexistence of validated quantum inputs and the
quarantined firewall surfaces, not physical quantum correctness or security.
"""

import os
import subprocess
import threading

import numpy as np
import pytest

from quantum_profiles.base_profile import BaseQuantumProfile
from quantum_virtual_processor import QuantumVirtualProcessor
from security.antiviral_firewall import AntiviralFirewall
from security.fluid_firewall import FluidFirewall
from security.quantum_mirror_firewall import QuantumMirrorFirewallObserver


def test_quantum_input_guards_coexist_with_disabled_firewalls(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Unexpected privileged command or thread startup")

    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(os, "system", forbidden)
    monkeypatch.setattr(threading.Thread, "start", forbidden)

    processor = QuantumVirtualProcessor(qubits=2)
    with pytest.raises(ValueError):
        processor.apply_gate("X", -1)
    with pytest.raises(ValueError):
        processor.measure(-1)

    profile = BaseQuantumProfile("integration", n_qubits=2)
    with pytest.raises(ValueError):
        profile.set_state(np.zeros(4))
    profile.set_state(np.array([3.0, 4.0, 0.0, 0.0]))
    np.testing.assert_allclose(profile.get_state(), [0.6, 0.8, 0, 0])

    for disabled in (AntiviralFirewall, FluidFirewall):
        with pytest.raises(RuntimeError, match="disabled"):
            disabled()

    observer = QuantumMirrorFirewallObserver()
    with pytest.raises(RuntimeError, match="disabled"):
        observer.start()
    with pytest.raises(RuntimeError, match="disabled"):
        observer.quantum_firewall_cycle()


def test_unverified_security_port_source_stays_disabled():
    from security.quantum_mirror_firewall import QuantumRandomizer
    with pytest.raises(RuntimeError, match="disabled"):
        QuantumRandomizer(bits=2).quantum_port()
