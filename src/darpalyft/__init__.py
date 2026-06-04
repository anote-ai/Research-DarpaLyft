"""DarpaLyft: Payload-per-Weight Optimization for the DARPA LIFT Challenge."""

from darpalyft.core import (
    MaterialType,
    DroneComponent,
    DroneDesign,
    PhysicsConstraints,
    total_mass,
    payload_capacity,
    structural_safety_factor,
    DesignOptimizer,
)
from darpalyft.evaluate import (
    payload_to_weight_ratio,
    is_feasible,
    design_score,
    pareto_designs,
)

__all__ = [
    "MaterialType",
    "DroneComponent",
    "DroneDesign",
    "PhysicsConstraints",
    "total_mass",
    "payload_capacity",
    "structural_safety_factor",
    "DesignOptimizer",
    "payload_to_weight_ratio",
    "is_feasible",
    "design_score",
    "pareto_designs",
]

__version__ = "0.1.0"
