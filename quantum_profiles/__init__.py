"""
Quantum Profiles Package

Quantum processor profiles that Pandora can dynamically discover, retrieve,
instantiate and switch between.

Hamiltonian support (used by quantum_virtual_processor.QuantumVirtualProcessor):
- Hamiltonian, QuantumProfileManager
- AlternativeProfile, CastleProfile, HiveProfile, EmpireProfile, OmegaProfile

Processor profiles, each with an MLQuantumAddon for on-the-fly ML-based
process logging and training:
- AlternativeQuantumVirtualProcessor: Alternative approaches to quantum computation
- CastleQuantumVirtualProcessor: Defensive and secure quantum computation
- HiveQuantumVirtualProcessor: Collaborative and distributed quantum computation
- EmpireQuantumVirtualProcessor: Central control lattice with an expandable
  grid of Kaleidoscopic Hives
- FourOverlayQuantumVirtualProcessor (registered as 'four_overlay')

Registry and factory functions:
    list_profiles() -> list: Returns a list of available profile names
    get_profile(name: str, **kwargs) -> object: Returns an instantiated processor
    get_addons(name: str) -> list: Returns the available addons for a given profile
    register_profile(name, module_name, get_profile_func): Adds a profile factory
"""

# Hamiltonian support. Imported before the processors: they subclass
# quantum_virtual_processor.QuantumVirtualProcessor, which uses
# QuantumProfileManager.
from .hamiltonian import Hamiltonian
from .alternative import AlternativeProfile
from .castle import CastleProfile
from .hive import HiveProfile
from .empire import EmpireProfile
from .omega import OmegaProfile
from .ml_quantum_addon import MLQuantumAddon
from .profile_manager import QuantumProfileManager

# Processor profiles
from quantum_profiles.alternative_quantum_virtual_processor import AlternativeQuantumVirtualProcessor
from quantum_profiles.castle_quantum_virtual_processor import CastleQuantumVirtualProcessor
from quantum_profiles.hive_quantum_virtual_processor import HiveQuantumVirtualProcessor
from quantum_profiles.empire_quantum_virtual_processor import EmpireQuantumVirtualProcessor


# Registry of quantum processor profiles that take configuration parameters
QUANTUM_PROFILES = {
    'empire': EmpireQuantumVirtualProcessor
}

# Registry of quantum processor profiles created by a factory function
_PROFILE_REGISTRY = {}


def register_profile(name, module_name, get_profile_func):
    """
    Register a quantum processor profile in the registry.

    Args:
        name (str): Unique name for the profile
        module_name (str): Module path containing the profile
        get_profile_func (callable): Function that returns an instantiated processor
    """
    _PROFILE_REGISTRY[name] = {
        'module': module_name,
        'factory': get_profile_func
    }


def list_profiles():
    """
    List all available quantum processor profiles.

    Returns:
        list: Names of all available profiles
    """
    names = list(_PROFILE_REGISTRY.keys())
    names += [name for name in QUANTUM_PROFILES if name not in _PROFILE_REGISTRY]
    return names


def get_profile(profile_name, **kwargs):
    """
    Get an instantiated quantum processor profile by name.

    Args:
        profile_name (str): Name of the profile to retrieve (e.g., 'empire')
        **kwargs: Configuration parameters for the profile

    Returns:
        Instance of the requested quantum processor profile

    Raises:
        KeyError: If the profile name is not registered

    Example:
        >>> processor = get_profile('empire', control_qubits=6, grid_size=(3, 3))
        >>> processor = get_profile('alternative')
    """
    if profile_name in QUANTUM_PROFILES:
        return QUANTUM_PROFILES[profile_name](**kwargs)
    if profile_name in _PROFILE_REGISTRY:
        return _PROFILE_REGISTRY[profile_name]['factory'](**kwargs)
    available = ', '.join(list_profiles())
    raise KeyError(
        f"Profile '{profile_name}' not found. "
        f"Available profiles: {available}"
    )


def get_addons(name):
    """
    Get the list of add-ons available for a specific profile.

    Args:
        name (str): Name of the profile

    Returns:
        list: List of addon names or descriptions

    Raises:
        KeyError: If the profile name is not found in the registry
    """
    # Get the profile instance and check for addons attribute
    processor = get_profile(name)
    if hasattr(processor, 'addons'):
        return [type(addon).__name__ for addon in processor.addons]
    return []


# Import and register profiles
try:
    from . import alternative_quantum_virtual_processor
    register_profile(
        'alternative',
        'quantum_profiles.alternative_quantum_virtual_processor',
        alternative_quantum_virtual_processor.get_profile
    )
except ImportError as e:
    print(f"Warning: Could not register 'alternative' profile: {e}")

try:
    from . import four_overlay_quantum_virtual_processor
    register_profile(
        'four_overlay',
        'quantum_profiles.four_overlay_quantum_virtual_processor',
        four_overlay_quantum_virtual_processor.get_profile
    )
except ImportError as e:
    print(f"Warning: Could not register 'four_overlay' profile: {e}")


__all__ = [
    # Hamiltonian support
    'Hamiltonian',
    'AlternativeProfile',
    'CastleProfile',
    'HiveProfile',
    'EmpireProfile',
    'OmegaProfile',
    'MLQuantumAddon',
    'QuantumProfileManager',
    # Processor profiles
    'AlternativeQuantumVirtualProcessor',
    'CastleQuantumVirtualProcessor',
    'HiveQuantumVirtualProcessor',
    'EmpireQuantumVirtualProcessor',
    # Registry
    'QUANTUM_PROFILES',
    'register_profile',
    'list_profiles',
    'get_profile',
    'get_addons',
]

__version__ = '1.0.0'
