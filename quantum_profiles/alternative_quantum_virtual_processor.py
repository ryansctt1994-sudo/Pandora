"""
Alternative Quantum Virtual Processor

An extensible quantum processor implementation with add-on support, diagnostics,
and fallback mechanisms. This processor accepts uncertainty and works in harmony
with classical logic, providing a flexible foundation for quantum operations.

ML integration: an MLQuantumAddon is installed by default (addons[0]) and logs
gates, measurements, expansion and diagnostics.

Components:
    - QuantumAddon: Base class for extensible add-ons
    - LoggerAddon: Logging functionality for quantum operations
    - QuantumQubitBuffer: Buffer for managing quantum state
    - AlternativeQuantumVirtualProcessor: Main processor with add-on support
"""

import logging
from typing import List, Optional, Any

from quantum_profiles.ml_quantum_addon import MLQuantumAddon


class QuantumAddon:
    """
    Base class for quantum processor add-ons.
    
    Add-ons can extend processor functionality by hooking into key operations
    such as gate application, measurement, and state management.
    """
    
    def __init__(self, name: str = "QuantumAddon"):
        """
        Initialize the add-on.
        
        Args:
            name (str): Descriptive name for this add-on
        """
        self.name = name
        self.enabled = True
    
    def on_gate_apply(self, gate: str, reg: Any) -> None:
        """
        Hook called when a gate is applied.
        
        Args:
            gate (str): Name of the gate being applied
            reg: Register or qubit identifier
        """
        pass
    
    def on_measure(self, result: Any) -> None:
        """
        Hook called when a measurement is performed.
        
        Args:
            result: Measurement result
        """
        pass
    
    def on_state_change(self, old_state: Any, new_state: Any) -> None:
        """
        Hook called when quantum state changes.
        
        Args:
            old_state: Previous state
            new_state: New state
        """
        pass


class LoggerAddon(QuantumAddon):
    """
    Add-on that provides logging functionality for quantum operations.
    """
    
    def __init__(self, log_level: int = logging.INFO):
        """
        Initialize the logger add-on.
        
        Args:
            log_level (int): Logging level (e.g., logging.INFO, logging.DEBUG)
        """
        super().__init__(name="LoggerAddon")
        self.logger = logging.getLogger("QuantumProcessor")
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)
    
    def on_gate_apply(self, gate: str, reg: Any) -> None:
        """Log gate application."""
        self.logger.debug(f"Applied gate '{gate}' to register {reg}")
    
    def on_measure(self, result: Any) -> None:
        """Log measurement."""
        self.logger.info(f"Measurement result: {result}")
    
    def on_state_change(self, old_state: Any, new_state: Any) -> None:
        """Log state change."""
        self.logger.debug(f"State transition: {old_state} -> {new_state}")


class QuantumQubitBuffer:
    """
    Buffer for managing quantum qubit state.
    
    Provides a virtual representation of quantum state with support for
    initialization, manipulation, and measurement.
    """
    
    def __init__(self, size: int = 6):
        """
        Initialize the qubit buffer.
        
        Args:
            size (int): Number of qubits in the buffer
        """
        self.size = size
        self.state = [0] * size  # Classical representation, |0⟩ state
        self.is_superposition = [False] * size
    
    def reset(self) -> None:
        """Reset all qubits to |0⟩ state."""
        self.state = [0] * self.size
        self.is_superposition = [False] * self.size
    
    def set_superposition(self, qubit: int, value: bool = True) -> None:
        """
        Mark a qubit as being in superposition.
        
        Args:
            qubit (int): Qubit index
            value (bool): True if in superposition, False otherwise
        """
        if 0 <= qubit < self.size:
            self.is_superposition[qubit] = value
    
    def get_state(self, qubit: int) -> int:
        """
        Get the classical state representation of a qubit.
        
        Args:
            qubit (int): Qubit index
            
        Returns:
            int: 0 or 1 representing the classical state
        """
        if 0 <= qubit < self.size:
            return self.state[qubit]
        return 0
    
    def set_state(self, qubit: int, value: int) -> None:
        """
        Set the classical state of a qubit.
        
        Args:
            qubit (int): Qubit index
            value (int): 0 or 1
        """
        if 0 <= qubit < self.size:
            self.state[qubit] = value & 1
    
    def expand(self, additional: int) -> None:
        """
        Add qubits to the buffer, each starting in the |0⟩ state.
        
        Args:
            additional (int): Number of qubits to add
        """
        self.state.extend([0] * additional)
        self.is_superposition.extend([False] * additional)
        self.size += additional


class AlternativeQuantumVirtualProcessor:
    """
    Alternative quantum virtual processor with extensible add-on support.
    
    This processor simulates quantum operations and integrates with classical
    and AI routines. It includes diagnostics, fallback mechanisms, and supports
    dynamic add-on registration for extended functionality.
    
    Two add-on interfaces are supported: QuantumAddon hooks (on_gate_apply,
    on_measure) and the MLQuantumAddon hooks (before_gate, after_gate,
    before_measurement, after_measurement).
    
    Usage:
        >>> processor = AlternativeQuantumVirtualProcessor(qubits=6)
        >>> processor.apply_gate("H", 0)
        >>> result = processor.measure()
        >>> stats = processor.get_addon_statistics()
    """
    
    # Define addons list with ML quantum addon enabled by default
    ADDONS = [
        MLQuantumAddon(train_on_fly=True)
    ]
    
    def __init__(self, qubits: int = 6, addons: Optional[List[QuantumAddon]] = None, **kwargs):
        """
        Initialize the alternative quantum processor.
        
        Args:
            qubits (int): Number of qubits to simulate
            addons (List[QuantumAddon], optional): List of add-ons to install,
                in addition to the default ML quantum addon
            **kwargs: Additional arguments
        """
        self.qubits = qubits
        self.buffer = QuantumQubitBuffer(qubits)
        self.addons = [addon for addon in self.ADDONS] + (list(addons) if addons is not None else [])
        self.operation_count = 0
        self.last_measurement = None
        self.diagnostics_enabled = True
        
        # Store processor context for addon hooks
        self._context = {
            'qubits': qubits,
            'profile': 'Alternative'
        }
    
    def add_addon(self, addon: QuantumAddon) -> None:
        """
        Add an add-on to the processor.
        
        Args:
            addon (QuantumAddon): Add-on instance to register
        """
        if addon not in self.addons:
            self.addons.append(addon)
    
    def remove_addon(self, addon: QuantumAddon) -> None:
        """
        Remove an add-on from the processor.
        
        Args:
            addon (QuantumAddon): Add-on instance to remove
        """
        if addon in self.addons:
            self.addons.remove(addon)
    
    def _before_gate_hooks(self, gate: str, register: int) -> None:
        """
        Call all addon before_gate hooks.
        
        Args:
            gate: Gate name
            register: Register/qubit index
        """
        for addon in self.addons:
            if hasattr(addon, 'before_gate'):
                addon.before_gate(gate, register, self._context)
    
    def _after_gate_hooks(self, gate: str, register: int) -> None:
        """
        Call all addon after_gate hooks.
        
        Args:
            gate: Gate name
            register: Register/qubit index
        """
        for addon in self.addons:
            if hasattr(addon, 'after_gate'):
                addon.after_gate(gate, register, self._context)
    
    def _before_measurement_hooks(self, register: int = None) -> None:
        """
        Call all addon before_measurement hooks.
        
        Args:
            register: Optional register/qubit index
        """
        for addon in self.addons:
            if hasattr(addon, 'before_measurement'):
                addon.before_measurement(register, self._context)
    
    def _after_measurement_hooks(self, register: int, result: int) -> None:
        """
        Call all addon after_measurement hooks.
        
        Args:
            register: Register/qubit index
            result: Measurement result
        """
        for addon in self.addons:
            if hasattr(addon, 'after_measurement'):
                addon.after_measurement(register, result, self._context)
    
    def apply_gate(self, gate: str, reg: int, **kwargs) -> None:
        """
        Apply a quantum gate to a register.
        
        Args:
            gate (str): Name of the gate (e.g., 'H', 'X', 'CNOT')
            reg (int): Register/qubit index
            **kwargs: Additional gate parameters
        """
        # Update context with any additional parameters
        context = self._context.copy()
        context.update(kwargs)
        self._context = context
        
        # Before hooks (ML quantum addon)
        self._before_gate_hooks(gate, reg)
        
        # Notify add-ons
        for addon in self.addons:
            if getattr(addon, 'enabled', True) and hasattr(addon, 'on_gate_apply'):
                addon.on_gate_apply(gate, reg)
        
        # Simulate gate operation
        if gate.upper() == 'X':
            # Pauli-X (NOT gate)
            current = self.buffer.get_state(reg)
            self.buffer.set_state(reg, 1 - current)
        elif gate.upper() == 'H':
            # Hadamard gate - creates superposition
            self.buffer.set_superposition(reg, True)
        elif gate.upper() == 'Z':
            # Pauli-Z gate (phase flip)
            pass  # Phase operations handled in full quantum simulator
        
        self.operation_count += 1
        
        # Fallback: If operations exceed threshold, perform diagnostics
        if self.diagnostics_enabled and self.operation_count % 100 == 0:
            self._run_diagnostics()
        
        # After hooks (ML quantum addon)
        self._after_gate_hooks(gate, reg)
    
    def measure(self, reg=None):
        """
        Measure quantum state and project to classical state.
        
        Args:
            reg: Specific register (int), list of registers, or None for all
            
        Returns:
            Measurement result (int or list)
        """
        import random
        
        # Before hooks (ML quantum addon)
        self._before_measurement_hooks(reg)
        
        
        if reg is not None:
            # Check if reg is a list of registers
            if isinstance(reg, (list, tuple)):
                # Measure multiple specific qubits
                result = []
                for r in reg:
                    if self.buffer.is_superposition[r]:
                        val = random.choice([0, 1])
                        self.buffer.set_state(r, val)
                        self.buffer.set_superposition(r, False)
                        result.append(val)
                    else:
                        result.append(self.buffer.get_state(r))
            else:
                # Measure single specific qubit
                if self.buffer.is_superposition[reg]:
                    # Collapse superposition randomly
                    result = random.choice([0, 1])
                    self.buffer.set_state(reg, result)
                    self.buffer.set_superposition(reg, False)
                else:
                    result = self.buffer.get_state(reg)
        else:
            # Measure all qubits
            result = []
            for i in range(self.qubits):
                if self.buffer.is_superposition[i]:
                    val = random.choice([0, 1])
                    self.buffer.set_state(i, val)
                    self.buffer.set_superposition(i, False)
                    result.append(val)
                else:
                    result.append(self.buffer.get_state(i))
        
        self.last_measurement = result
        
        # Notify add-ons
        for addon in self.addons:
            if getattr(addon, 'enabled', True) and hasattr(addon, 'on_measure'):
                addon.on_measure(result)
        
        # After hooks (ML quantum addon)
        self._after_measurement_hooks(reg if reg is not None else 0, result)
        
        return result
    
    def reset(self) -> None:
        """Reset the processor to initial state."""
        self.buffer.reset()
        self.operation_count = 0
        self.last_measurement = None
    
    def _run_diagnostics(self) -> None:
        """
        Run internal diagnostics on the processor.
        
        This is a fallback mechanism to ensure processor stability during
        long-running operations.
        """
        # Check buffer integrity
        if self.buffer.size != self.qubits:
            # Fallback: Recreate buffer
            self.buffer = QuantumQubitBuffer(self.qubits)
        
        # Log diagnostic information if logger addon is present
        for addon in self.addons:
            if isinstance(addon, LoggerAddon) and addon.enabled:
                addon.logger.info(
                    f"Diagnostics: {self.operation_count} operations performed, "
                    f"buffer integrity OK"
                )
    
    def get_state_info(self) -> dict:
        """
        Get information about the current processor state.
        
        Returns:
            dict: State information including qubit count, operations, etc.
        """
        return {
            'qubits': self.qubits,
            'operations': self.operation_count,
            'last_measurement': self.last_measurement,
            'addons': [getattr(addon, 'name', type(addon).__name__) for addon in self.addons
                       if getattr(addon, 'enabled', True)],
            'buffer_size': self.buffer.size
        }
    
    def expand_qubits(self, additional_qubits: int) -> None:
        """
        Expand the quantum system with additional qubits.
        
        Args:
            additional_qubits: Number of qubits to add
        """
        old_qubits = self.qubits
        self.qubits += additional_qubits
        self.buffer.expand(additional_qubits)
        self._context['qubits'] = self.qubits
        
        # Log expansion to addons
        for addon in self.addons:
            if hasattr(addon, 'log_expansion'):
                addon.log_expansion(
                    f"Expanded from {old_qubits} to {self.qubits} qubits",
                    self._context
                )
    
    def get_diagnostic_info(self) -> dict:
        """
        Get diagnostic information about processor state.
        
        Returns:
            Dictionary with diagnostic information
        """
        diagnostic = {
            'qubits': self.qubits,
            'profile': 'Alternative',
            'addons': len(self.addons)
        }
        
        # Log diagnostic to addons
        for addon in self.addons:
            if hasattr(addon, 'log_diagnostic'):
                addon.log_diagnostic('processor_state', diagnostic, self._context)
        
        return diagnostic
    
    def get_addon_statistics(self) -> dict:
        """
        Get statistics from all addons.
        
        Returns:
            Dictionary mapping addon index to statistics
        """
        stats = {}
        for i, addon in enumerate(self.addons):
            if hasattr(addon, 'get_statistics'):
                stats[f'addon_{i}'] = addon.get_statistics()
        return stats
    
    def get_ml_addon(self) -> MLQuantumAddon:
        """
        Get the ML quantum addon instance.
        
        Returns:
            MLQuantumAddon instance or None if not found
        """
        for addon in self.addons:
            if isinstance(addon, MLQuantumAddon):
                return addon
        return None


def get_profile():
    """
    Factory function to create a fully configured AlternativeQuantumVirtualProcessor.
    
    Returns:
        AlternativeQuantumVirtualProcessor: Processor instance with standard add-ons
    """
    # Create processor with default configuration
    processor = AlternativeQuantumVirtualProcessor(qubits=6)
    
    # Add standard add-ons
    logger_addon = LoggerAddon(log_level=logging.INFO)
    processor.add_addon(logger_addon)
    
    return processor
