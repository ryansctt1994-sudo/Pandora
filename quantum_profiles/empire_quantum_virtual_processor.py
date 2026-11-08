"""
Empire Quantum Virtual Processor
==================================

Features a central control lattice (supervised by Pandora) and an expandable
grid of Kaleidoscopic Hives. Each component is a quantum virtual processor
with configurable qubit sizes.

Architecture:
- Central Control Lattice: A QuantumVirtualProcessor (default 4 qubits)
- Kaleidoscopic Hives Grid: A 2D grid of HiveQuantumVirtualProcessors (default 2x2 grid, 8 qubits each)
- Supports dynamic expansion of both control lattice and hive grid
- Routes gates/measurements to entire empire, control lattice, or specific hives
- Full addon support

ML integration:
- An MLQuantumAddon is registered by default (addons[0]) and logs the
  Empire's gates, measurements, expansions and diagnostics
- qubits is the control lattice's qubit count; apply_gate/measure act on the
  control lattice, so the Empire works like every other ML-instrumented profile
- Each hive is itself an ML-instrumented HiveQuantumVirtualProcessor
"""

from functools import partial

from quantum_virtual_processor import QuantumVirtualProcessor
from quantum_profiles.ml_quantum_addon import MLQuantumAddon
from quantum_profiles.hive_quantum_virtual_processor import HiveQuantumVirtualProcessor


class EmpireQuantumVirtualProcessor:
    """
    Empire Quantum Virtual Processor Profile
    
    A hierarchical quantum computing architecture with:
    - A central control lattice for coordination
    - An expandable grid of Kaleidoscopic Hives for distributed quantum operations
    
    The Empire profile allows Pandora/API to:
    - Dynamically expand the number of hives (grid size)
    - Adjust control lattice size
    - Direct operations to the entire empire, control lattice only, or specific hives
    - Support addons for enhanced functionality
    - Log and learn from its operations through the ML quantum addon
    
    Usage:
        >>> empire = EmpireQuantumVirtualProcessor(control_qubits=4, grid_size=(2, 2))
        >>> empire.apply_gate_to_hive((0, 0), "H", 0)
        >>> results = empire.measure_empire()
        >>> processor = EmpireQuantumVirtualProcessor(qubits=6)
        >>> processor.apply_gate("H", 0)
        >>> stats = processor.get_addon_statistics()
    """

    # Define addons list with ML quantum addon enabled by default.
    # Each entry is called once per processor, so every processor gets its
    # own addon (its own event log, training buffers and model).
    ADDONS = [
        partial(MLQuantumAddon, train_on_fly=True)
    ]
    
    def __init__(self, control_qubits=None, grid_size=(2, 2), hive_qubits=8, qubits=None, **kwargs):
        """
        Initialize the Empire quantum processor.
        
        Args:
            control_qubits (int): Number of qubits in the central control lattice (default: 4)
            grid_size (tuple): Grid dimensions (rows, cols) for hives (default: (2, 2))
            hive_qubits (int): Number of qubits per hive (default: 8)
            qubits (int): Alias for control_qubits, as accepted by the other profiles
            **kwargs: Additional arguments
        
        Raises:
            ValueError: If qubits and control_qubits are both given and differ
        """
        if qubits is not None and control_qubits is not None and qubits != control_qubits:
            raise ValueError(
                f"qubits ({qubits}) and control_qubits ({control_qubits}) both set the "
                "control lattice size; pass one of them."
            )
        if control_qubits is None:
            control_qubits = qubits if qubits is not None else 4
        
        self.control_lattice = QuantumVirtualProcessor(qubits=control_qubits)
        self.control_qubits = control_qubits
        self.grid_size = grid_size
        self.hive_qubits = hive_qubits
        self.hive_grid = {}
        
        # Initialize addons, ML quantum addon first
        self.addons = [make_addon() for make_addon in self.ADDONS]
        
        # Store processor context for addon hooks
        self._context = {
            'qubits': control_qubits,
            'profile': 'Empire'
        }
        
        # Initialize the hive grid
        self._initialize_hive_grid()
    
    @property
    def qubits(self):
        """Number of qubits in the control lattice (same as control_qubits)."""
        return self.control_qubits
    
    def _log_expansion(self, description):
        """Log an expansion to all addons that support it."""
        for addon in self.addons:
            if hasattr(addon, 'log_expansion'):
                addon.log_expansion(description, self._context)
    
    def _initialize_hive_grid(self):
        """Initialize the grid of Kaleidoscopic Hives."""
        rows, cols = self.grid_size
        self.hive_grid = {}
        for row in range(rows):
            for col in range(cols):
                hive_id = (row, col)
                self.hive_grid[hive_id] = HiveQuantumVirtualProcessor(
                    qubits=self.hive_qubits,
                    hive_id=hive_id
                )
    
    def expand_grid(self, new_grid_size):
        """
        Dynamically expand the hive grid to a new size.
        
        Args:
            new_grid_size (tuple): New grid dimensions (rows, cols)
            
        Returns:
            bool: True if expansion was successful
        """
        new_rows, new_cols = new_grid_size
        old_rows, old_cols = self.grid_size
        
        if new_rows < old_rows or new_cols < old_cols:
            raise ValueError("Cannot shrink grid size. New size must be >= current size.")
        
        # Add new hives for expanded grid
        for row in range(new_rows):
            for col in range(new_cols):
                hive_id = (row, col)
                if hive_id not in self.hive_grid:
                    self.hive_grid[hive_id] = HiveQuantumVirtualProcessor(
                        qubits=self.hive_qubits,
                        hive_id=hive_id
                    )
        
        self.grid_size = new_grid_size
        self._log_expansion(f"Expanded hive grid from {(old_rows, old_cols)} to {new_grid_size}")
        return True
    
    def expand_control_lattice(self, new_qubit_count):
        """
        Expand the control lattice to support more qubits.
        
        Args:
            new_qubit_count (int): New number of qubits for the control lattice
            
        Returns:
            bool: True if expansion was successful
        """
        if new_qubit_count < self.control_qubits:
            raise ValueError("Cannot reduce control lattice size. New size must be >= current size.")
        
        old_qubits = self.control_qubits

        # Create new control lattice with expanded qubit count
        self.control_lattice = QuantumVirtualProcessor(qubits=new_qubit_count)
        self.control_qubits = new_qubit_count
        self._context['qubits'] = new_qubit_count
        self._log_expansion(f"Expanded control lattice from {old_qubits} to {new_qubit_count} qubits")
        return True
    
    def apply_gate_to_empire(self, gate, reg):
        """
        Apply a quantum gate to the entire Empire (control lattice + all hives).
        
        Args:
            gate (str): Gate type to apply
            reg (int): Register/qubit index
        """
        # Apply to control lattice
        self.apply_gate(gate, reg)
        
        # Apply to all hives
        for hive in self.hive_grid.values():
            hive.apply_gate(gate, reg)
    
    def apply_gate_to_control_lattice(self, gate, reg):
        """
        Apply a quantum gate only to the central control lattice.
        
        Args:
            gate (str): Gate type to apply
            reg (int): Register/qubit index
        """
        self.apply_gate(gate, reg)
    
    def apply_gate_to_hive(self, hive_id, gate, reg):
        """
        Apply a quantum gate to a specific hive block.
        
        Args:
            hive_id (tuple): Hive identifier (row, col)
            gate (str): Gate type to apply
            reg (int): Register/qubit index
            
        Raises:
            KeyError: If hive_id does not exist in the grid
        """
        if hive_id not in self.hive_grid:
            raise KeyError(f"Hive {hive_id} does not exist in the grid.")
        
        self.hive_grid[hive_id].apply_gate(gate, reg)
    
    def measure_empire(self):
        """
        Measure the entire Empire (control lattice + all hives).
        
        Returns:
            dict: Measurement results with 'control' and 'hives' keys
        """
        results = {
            'control': self.measure(),
            'hives': {}
        }
        
        for hive_id, hive in self.hive_grid.items():
            results['hives'][hive_id] = hive.measure()
        
        return results
    
    def measure_control_lattice(self):
        """
        Measure only the central control lattice.
        
        Returns:
            Measurement result from the control lattice
        """
        return self.measure()
    
    def measure_hive(self, hive_id):
        """
        Measure a specific hive block.
        
        Args:
            hive_id (tuple): Hive identifier (row, col)
            
        Returns:
            Measurement result from the specified hive
            
        Raises:
            KeyError: If hive_id does not exist in the grid
        """
        if hive_id not in self.hive_grid:
            raise KeyError(f"Hive {hive_id} does not exist in the grid.")
        
        return self.hive_grid[hive_id].measure()
    
    def get_hive(self, hive_id):
        """
        Get a reference to a specific hive processor.
        
        Args:
            hive_id (tuple): Hive identifier (row, col)
            
        Returns:
            HiveQuantumVirtualProcessor: The hive processor
            
        Raises:
            KeyError: If hive_id does not exist in the grid
        """
        if hive_id not in self.hive_grid:
            raise KeyError(f"Hive {hive_id} does not exist in the grid.")
        
        return self.hive_grid[hive_id]
    
    def list_hives(self):
        """
        List all hive identifiers in the grid.
        
        Returns:
            list: List of hive IDs (row, col) tuples
        """
        return sorted(self.hive_grid.keys())
    
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
    
    def apply_gate(self, gate: str, register: int, **kwargs) -> None:
        """
        Apply a quantum gate to the control lattice with ML monitoring.
        
        Args:
            gate: Gate name (e.g., 'H', 'X', 'CNOT')
            register: Register/qubit to apply gate to
            **kwargs: Additional gate parameters
        """
        # Update context with any additional parameters
        context = self._context.copy()
        context.update(kwargs)
        self._context = context
        
        # Before hooks
        self._before_gate_hooks(gate, register)
        
        # Apply the gate to the control lattice
        self.control_lattice.apply_gate(gate, register)
        
        # After hooks
        self._after_gate_hooks(gate, register)
    
    def measure(self, register: int = None) -> int:
        """
        Measure the control lattice with ML monitoring.
        
        Args:
            register: Optional register to measure (None = measure all)
            
        Returns:
            Measurement result
        """
        # Before hooks
        self._before_measurement_hooks(register)
        
        # Measure the control lattice
        result = self.control_lattice.measure()
        
        # After hooks
        self._after_measurement_hooks(register if register is not None else 0, result)
        
        return result
    
    def expand_qubits(self, additional_qubits: int) -> None:
        """
        Expand the control lattice with additional qubits.
        
        Args:
            additional_qubits: Number of qubits to add
        """
        self.expand_control_lattice(self.control_qubits + additional_qubits)
    
    def get_diagnostic_info(self) -> dict:
        """
        Get diagnostic information about processor state.
        
        Returns:
            Dictionary with diagnostic information
        """
        diagnostic = {
            'qubits': self.qubits,
            'profile': 'Empire',
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
    
    def register_addon(self, addon):
        """
        Register an addon for the Empire profile.
        
        Addons can extend the functionality of the Empire processor.
        
        Args:
            addon: Addon object to register
        """
        self.addons.append(addon)
    
    def execute_addon(self, addon_name, *args, **kwargs):
        """
        Execute a registered addon by name.
        
        Args:
            addon_name (str): Name of the addon to execute
            *args: Positional arguments for the addon
            **kwargs: Keyword arguments for the addon
            
        Returns:
            Result from the addon execution
            
        Raises:
            ValueError: If addon is not found
        """
        for addon in self.addons:
            if hasattr(addon, 'name') and addon.name == addon_name:
                if hasattr(addon, 'execute'):
                    return addon.execute(self, *args, **kwargs)
        
        raise ValueError(f"Addon '{addon_name}' not found or does not have execute method.")
    
    def get_empire_stats(self):
        """
        Get statistics about the Empire configuration.
        
        Returns:
            dict: Dictionary with Empire statistics
        """
        return {
            'control_lattice_qubits': self.control_qubits,
            'grid_size': self.grid_size,
            'total_hives': len(self.hive_grid),
            'hive_qubits': self.hive_qubits,
            'total_qubits': self.control_qubits + (len(self.hive_grid) * self.hive_qubits),
            'registered_addons': len(self.addons)
        }
    
    def __repr__(self):
        """String representation of the Empire."""
        stats = self.get_empire_stats()
        return (f"<EmpireQuantumVirtualProcessor: "
                f"{stats['control_lattice_qubits']} control qubits, "
                f"{stats['total_hives']} hives ({self.grid_size[0]}x{self.grid_size[1]}), "
                f"{stats['total_qubits']} total qubits>")
