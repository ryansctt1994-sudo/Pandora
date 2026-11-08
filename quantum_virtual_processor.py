"""
QuantumVirtualProcessor
Simulates quantum registers/gates, integrates with classical and AI routines.
Philosophy: Accepts uncertainty, works in harmony with classical logic.

Now enhanced with Hamiltonian support through quantum profiles:
- Alternative: Explores alternative computational pathways via superposition
- Castle: Defensive stable quantum operations with energy barriers
- Hive: Collective behavior through distributed entanglement
- Empire: Hierarchical control with cascading interactions
- Omega: Optimized balanced configuration across all operators

Enhanced with neuromorphic sentinel and recursive weight integration:
- Neuromorphic sentinels for adaptive state monitoring
- Recursive weights with Ramanujan τ multipliers
- Integration with Ouroboros Virtual Processor functional manifold

Also keeps the simplified classical register from the core-improvements
version: per-qubit gates, entangle(), reset(), get_state_vector() and
quantum_random_number(). measure() with no argument samples the active
profile's Hamiltonian state; measure(i) reads qubit i of the register.
"""

# QuantumProfileManager is imported inside QuantumVirtualProcessor.__init__,
# not here: quantum_profiles imports this module (its processors subclass
# QuantumVirtualProcessor), so a module-level import would be circular.

# Modular integration for ouroboros components
try:
    from ouroboros_virtual_processor import (
        NeuromorphicSentinel,
        RecursiveWeight,
        RAMANUJAN_TAU_BASE
    )
    OUROBOROS_INTEGRATION_AVAILABLE = True
except ImportError:
    OUROBOROS_INTEGRATION_AVAILABLE = False


import random
import math


class QuantumVirtualProcessor:
    """
    Enhanced quantum virtual processor with Hamiltonian-aware profile support.
    
    Provides quantum simulation capabilities with multiple processor profiles,
    each with characteristic Hamiltonians for different computational paradigms.
    
    Enhanced with:
    - Neuromorphic sentinel monitoring for adaptive state tracking
    - Recursive weights with Ramanujan τ multipliers
    - Integration with Ouroboros Virtual Processor
    - A simplified classical register for per-qubit gates and measurement
    """
    
    def __init__(self, qubits=6, profile='alternative'):
        """
        Initialize the quantum virtual processor.
        
        Args:
            qubits: Number of qubits (default: 6)
            profile: Initial quantum profile ('alternative', 'castle', 'hive', 'empire', 'omega')
        """
        self.qubits = qubits
        
        # Simplified classical register (core-improvements version)
        self.state = [0] * qubits
        self.measurement_history = []
        
        from quantum_profiles import QuantumProfileManager
        
        # Initialize profile manager with Hamiltonian support
        self.profile_manager = QuantumProfileManager(
            default_profile=profile,
            n_qubits=qubits
        )
        
        # Neuromorphic sentinel integration
        self.sentinels = []
        self.recursive_weights = []
        
        if OUROBOROS_INTEGRATION_AVAILABLE:
            # Initialize neuromorphic sentinels
            num_sentinels = max(2, qubits // 3)
            self.sentinels = [
                NeuromorphicSentinel(
                    sentinel_id=i,
                    threshold=0.4 + 0.05 * i,
                    learning_rate=0.02
                )
                for i in range(num_sentinels)
            ]
            
            # Initialize recursive weights with Ramanujan τ multipliers
            self.recursive_weights = [
                RecursiveWeight(
                    index=i,
                    base_weight=1.0 / (i + 1),
                    tau_multiplier=1.0
                )
                for i in range(qubits)
            ]
    
    def _ensure_register_size(self):
        """Grow the classical register if self.qubits was raised (e.g. expand_qubits)."""
        if len(self.state) < self.qubits:
            self.state.extend([0] * (self.qubits - len(self.state)))
    
    def apply_gate(self, gate, reg):
        """
        Apply a single-qubit gate to the simplified classical register.
        
        Args:
            gate: Gate identifier: 'H', 'X', 'Y', 'Z' or 'T'
            reg: Qubit index to apply the gate to
        
        Returns:
            The qubit's classical value after the gate
        
        Raises:
            ValueError: If the qubit index is out of range or the gate is unknown
        """
        if reg >= self.qubits:
            raise ValueError(f"Qubit index {reg} out of range (max: {self.qubits-1})")
        self._ensure_register_size()
        
        gate = gate.upper()
        
        if gate == 'H':  # Hadamard: creates superposition
            # Simplified: randomly set to 0 or 1 (50/50 chance)
            self.state[reg] = random.randint(0, 1)
        elif gate == 'X':  # Pauli-X: bit flip
            self.state[reg] = 1 - self.state[reg]
        elif gate == 'Y':  # Pauli-Y: bit flip plus phase; phase is dropped in this model
            self.state[reg] = 1 - self.state[reg]
        elif gate == 'Z':  # Pauli-Z: phase flip (simplified)
            pass  # In this simple model, phase doesn't affect measurement
        elif gate == 'T':  # T gate: π/4 phase rotation (simplified)
            pass  # Phase operations simplified in this model
        else:
            raise ValueError(f"Unknown gate: {gate}")
        
        return self.state[reg]
    
    def entangle(self, qubit1, qubit2):
        """Create entanglement between two qubits (simplified)"""
        if qubit1 >= self.qubits or qubit2 >= self.qubits:
            raise ValueError("Qubit indices out of range")
        self._ensure_register_size()
        
        # Simplified entanglement: make qubit2 match qubit1
        self.state[qubit2] = self.state[qubit1]
    
    def measure(self, qubit_index=None):
        """
        Perform quantum measurement, projecting to classical state.
        
        Args:
            qubit_index: None to sample the active profile's Hamiltonian state;
                an index to read that qubit of the classical register
        
        Returns:
            Basis-state index sampled from the state probabilities (no argument),
            or the qubit's classical value (0 or 1)
        """
        if qubit_index is not None:
            # Measure specific qubit of the classical register
            if qubit_index >= self.qubits:
                raise ValueError(f"Qubit index {qubit_index} out of range")
            self._ensure_register_size()
            result = self.state[qubit_index]
            self.measurement_history.append((qubit_index, result))
            return result
        
        import numpy as np
        state = self.profile_manager.get_state()
        probabilities = np.abs(state) ** 2
        
        # Sample from probability distribution
        outcome = np.random.choice(len(probabilities), p=probabilities)
        self.measurement_history.append(('all', outcome))
        return outcome
    
    def reset(self):
        """Reset all qubits of the classical register to |0⟩"""
        self.state = [0] * self.qubits
    
    def get_state_vector(self):
        """Return current quantum state (simplified representation)"""
        return {
            'qubits': self.qubits,
            'state': self.state,
            'measurements': len(self.measurement_history)
        }
    
    def quantum_random_number(self, bits=8):
        """Generate truly random number using quantum uncertainty"""
        result = 0
        for i in range(min(bits, self.qubits)):
            self.apply_gate('H', i)  # Put in superposition
            bit = self.measure(i)     # Collapse to 0 or 1
            result = (result << 1) | bit
        return result
    
    # === Hamiltonian-aware operations ===
    
    def add_hamiltonian_term(self, coefficient, pauli_string):
        """
        Add a term to the current profile's Hamiltonian.
        
        Args:
            coefficient: Weight for this term
            pauli_string: Pauli operator string (e.g., "XYZ")
        """
        self.profile_manager.add_term(coefficient, pauli_string)
    
    def compute_energy(self, state=None):
        """
        Compute energy expectation value under current Hamiltonian.
        
        Args:
            state: Quantum state (None = current state)
        
        Returns:
            float: Energy expectation value
        """
        return self.profile_manager.compute_energy(state)
    
    def get_hamiltonian(self):
        """
        Get the current profile's Hamiltonian.
        
        Returns:
            Hamiltonian object
        """
        return self.profile_manager.get_hamiltonian()
    
    def time_evolve(self, time):
        """
        Evolve the quantum state under the Hamiltonian for given time.
        
        Args:
            time: Evolution time
        
        Returns:
            Evolved state vector
        """
        return self.profile_manager.time_evolution(time)
    
    def switch_profile(self, profile_name):
        """
        Switch to a different quantum processor profile.
        
        Args:
            profile_name: Name of profile ('alternative', 'castle', 'hive', 'empire', 'omega')
        """
        self.profile_manager.switch_profile(profile_name)
    
    def get_ml_addon(self):
        """
        Get the ML quantum addon for Hamiltonian learning.
        
        Returns:
            MLQuantumAddon instance
        """
        return self.profile_manager.get_ml_addon()
    
    def get_summary(self):
        """
        Get summary of processor state and configuration.
        
        Returns:
            Dictionary with summary information
        """
        summary = self.profile_manager.get_summary()
        
        # Add neuromorphic sentinel and recursive weight information
        if OUROBOROS_INTEGRATION_AVAILABLE:
            summary['neuromorphic_sentinels'] = {
                'count': len(self.sentinels),
                'sentinel_info': [
                    {
                        'id': s.sentinel_id,
                        'threshold': s.threshold,
                        'sensitivity': s.sensitivity,
                        'activations': len(s.activation_history)
                    }
                    for s in self.sentinels
                ]
            }
            
            summary['recursive_weights'] = {
                'count': len(self.recursive_weights),
                'weights': [
                    {
                        'index': rw.index,
                        'base_weight': rw.base_weight,
                        'tau_multiplier': rw.tau_multiplier,
                        'recursion_depth': rw.recursion_depth
                    }
                    for rw in self.recursive_weights
                ]
            }
        
        return summary
    
    def monitor_state_with_sentinels(self, state=None):
        """
        Monitor quantum state using neuromorphic sentinels.
        
        Args:
            state: Quantum state to monitor (None = current state)
            
        Returns:
            Dictionary with sentinel monitoring results
        """
        if not OUROBOROS_INTEGRATION_AVAILABLE or not self.sentinels:
            return {'sentinels_available': False}
        
        if state is None:
            state = self.profile_manager.get_state()
        
        results = {
            'sentinels_available': True,
            'triggers': [],
            'activations': []
        }
        
        for sentinel in self.sentinels:
            triggered = sentinel.monitor(state)
            results['triggers'].append({
                'sentinel_id': sentinel.sentinel_id,
                'triggered': triggered,
                'threshold': sentinel.threshold
            })
            if len(sentinel.activation_history) > 0:
                results['activations'].append({
                    'sentinel_id': sentinel.sentinel_id,
                    'last_activation': sentinel.activation_history[-1]
                })
        
        return results
    
    def evolve_recursive_weights(self, iteration):
        """
        Evolve recursive weights using Ramanujan τ multipliers.
        
        Args:
            iteration: Current iteration number
            
        Returns:
            List of evolved weight values
        """
        if not OUROBOROS_INTEGRATION_AVAILABLE or not self.recursive_weights:
            return []
        
        evolved_weights = []
        for rw in self.recursive_weights:
            weight = rw.evolve(iteration)
            evolved_weights.append({
                'index': rw.index,
                'weight': weight,
                'tau_multiplier': rw.tau_multiplier
            })
        
        return evolved_weights
