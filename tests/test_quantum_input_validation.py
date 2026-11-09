"""Regression checks for bounded quantum inputs (not quantum correctness).

The processor still has separate classical-register and profile-state semantics;
these tests do not claim the quantum gate/measurement design is repaired.
"""

import numpy as np
import pytest

from quantum_virtual_processor import QuantumVirtualProcessor
from quantum_profiles.base_profile import BaseQuantumProfile


@pytest.mark.parametrize(
    ("operation", "indices"),
    [
        ("gate", (-1,)),
        ("measure", (-1,)),
        ("entangle", (-1, 0)),
        ("entangle", (0, -1)),
    ],
)
def test_negative_indices_are_rejected(operation, indices):
    processor = QuantumVirtualProcessor(qubits=2)
    before = list(processor.state)
    with pytest.raises(ValueError):
        if operation == "gate":
            processor.apply_gate("X", indices[0])
        elif operation == "measure":
            processor.measure(indices[0])
        else:
            processor.entangle(*indices)
    assert processor.state == before


@pytest.mark.parametrize(
    "bad_state",
    [
        [0, 0, 0, 0],
        [float("nan"), 0, 0, 0],
        [float("inf"), 0, 0, 0],
        [[1, 0], [0, 0]],
        [1, 0],
        1,
    ],
)
def test_invalid_profile_states_are_rejected_without_mutation(bad_state):
    profile = BaseQuantumProfile("test", n_qubits=2)
    before = profile.get_state()
    with pytest.raises(ValueError):
        profile.set_state(np.asarray(bad_state))
    assert np.array_equal(profile.get_state(), before)


def test_profile_state_is_normalized_and_detached():
    profile = BaseQuantumProfile("test", n_qubits=2)
    caller = np.array([3.0, 4.0, 0.0, 0.0])
    profile.set_state(caller)
    np.testing.assert_allclose(profile.get_state(), [0.6, 0.8, 0.0, 0.0])
    caller[0] = 99
    np.testing.assert_allclose(profile.get_state(), [0.6, 0.8, 0.0, 0.0])


def test_random_number_docstring_does_not_claim_physical_entropy():
    description = QuantumVirtualProcessor.quantum_random_number.__doc__.lower()
    assert "simulated" in description
    assert "not for cryptographic" in description
    assert "truly random" not in description
