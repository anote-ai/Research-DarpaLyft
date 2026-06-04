"""Core data structures and physics models for DARPA LIFT drone optimization."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum


class MaterialType(str, Enum):
    """Structural materials available for drone component fabrication."""

    CARBON_FIBER = "CARBON_FIBER"
    ALUMINUM_ALLOY = "ALUMINUM_ALLOY"
    TITANIUM = "TITANIUM"
    FIBERGLASS = "FIBERGLASS"
    ABS_PLASTIC = "ABS_PLASTIC"


# Material density (kg/m^3) — simplified representative values
_MATERIAL_DENSITY: dict[MaterialType, float] = {
    MaterialType.CARBON_FIBER: 1600.0,
    MaterialType.ALUMINUM_ALLOY: 2700.0,
    MaterialType.TITANIUM: 4500.0,
    MaterialType.FIBERGLASS: 1900.0,
    MaterialType.ABS_PLASTIC: 1050.0,
}

# Material tensile strength factor (relative, higher = stronger)
_MATERIAL_STRENGTH: dict[MaterialType, float] = {
    MaterialType.CARBON_FIBER: 3.5,
    MaterialType.ALUMINUM_ALLOY: 1.5,
    MaterialType.TITANIUM: 2.5,
    MaterialType.FIBERGLASS: 1.2,
    MaterialType.ABS_PLASTIC: 0.6,
}


@dataclass
class DroneComponent:
    """A single structural or functional component of the drone."""

    component_id: str
    name: str
    material: MaterialType
    mass_kg: float
    area_m2: float = 0.0
    load_bearing: bool = False

    def __post_init__(self) -> None:
        if self.mass_kg < 0:
            raise ValueError(f"mass_kg must be non-negative, got {self.mass_kg}")
        if self.area_m2 < 0:
            raise ValueError(f"area_m2 must be non-negative, got {self.area_m2}")


@dataclass
class DroneDesign:
    """Full drone design specification."""

    design_id: str
    components: list[DroneComponent] = field(default_factory=list)
    motor_count: int = 4
    propeller_diameter_m: float = 0.3
    battery_capacity_wh: float = 100.0

    def __post_init__(self) -> None:
        if self.motor_count < 1:
            raise ValueError(f"motor_count must be >= 1, got {self.motor_count}")
        if self.propeller_diameter_m <= 0:
            raise ValueError(f"propeller_diameter_m must be > 0")


@dataclass
class PhysicsConstraints:
    """Physical and regulatory constraints for drone designs."""

    max_total_mass_kg: float = 25.0
    min_structural_factor: float = 1.5
    max_wing_loading: float = 50.0  # N/m^2


def total_mass(design: DroneDesign) -> float:
    """Compute total structural mass of a drone design.

    Args:
        design: DroneDesign instance.

    Returns:
        Sum of component masses in kg.
    """
    return sum(c.mass_kg for c in design.components)


def payload_capacity(design: DroneDesign, max_thrust_n: float) -> float:
    """Compute maximum payload the drone can carry.

    payload = (max_thrust / g) - structural_mass

    Args:
        design: DroneDesign instance.
        max_thrust_n: Maximum thrust in Newtons.

    Returns:
        Payload capacity in kg (may be negative if thrust insufficient).
    """
    g = 9.81  # m/s^2
    return (max_thrust_n / g) - total_mass(design)


def structural_safety_factor(design: DroneDesign) -> float:
    """Estimate structural safety factor based on load-bearing components.

    Heuristic: weighted average material strength of load-bearing components,
    normalized by a reference factor. Returns 1.0 if no components.

    Args:
        design: DroneDesign instance.

    Returns:
        Estimated safety factor (dimensionless).
    """
    lb_components = [c for c in design.components if c.load_bearing]
    if not lb_components:
        return 1.0
    avg_strength = sum(_MATERIAL_STRENGTH[c.material] for c in lb_components) / len(lb_components)
    # Scale so CARBON_FIBER-only designs yield ~3.5, ABS_PLASTIC ~0.6
    return avg_strength


class DesignOptimizer:
    """Random search optimizer for drone designs under physics constraints.

    In production this would integrate surrogate model (GP or NN) + Bayesian
    optimization. This stub performs random sampling for demonstration.
    """

    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)

    def optimize(
        self,
        constraints: PhysicsConstraints,
        n_iterations: int = 100,
    ) -> DroneDesign:
        """Run random search to find a feasible drone design.

        Args:
            constraints: PhysicsConstraints to satisfy.
            n_iterations: Number of random designs to sample.

        Returns:
            Best DroneDesign found (highest payload capacity within constraints).
        """
        best_design: DroneDesign | None = None
        best_payload = float("-inf")
        materials = list(MaterialType)

        for i in range(n_iterations):
            components = [
                DroneComponent(
                    component_id=f"C{i}_frame",
                    name="Frame",
                    material=self._rng.choice(materials),
                    mass_kg=self._rng.uniform(0.5, 3.0),
                    area_m2=self._rng.uniform(0.1, 1.0),
                    load_bearing=True,
                ),
                DroneComponent(
                    component_id=f"C{i}_shell",
                    name="Shell",
                    material=self._rng.choice(materials),
                    mass_kg=self._rng.uniform(0.2, 1.5),
                    area_m2=self._rng.uniform(0.05, 0.5),
                    load_bearing=False,
                ),
            ]
            design = DroneDesign(
                design_id=f"D{i:04d}",
                components=components,
                motor_count=self._rng.choice([4, 6, 8]),
                propeller_diameter_m=self._rng.uniform(0.2, 0.6),
                battery_capacity_wh=self._rng.uniform(50.0, 500.0),
            )
            mass = total_mass(design)
            thrust = design.motor_count * 30.0  # 30N per motor (stub)
            pcap = payload_capacity(design, thrust)
            ssf = structural_safety_factor(design)

            if (
                mass <= constraints.max_total_mass_kg
                and ssf >= constraints.min_structural_factor
                and pcap > best_payload
            ):
                best_payload = pcap
                best_design = design

        if best_design is None:
            # Fallback: return first design
            best_design = DroneDesign(design_id="D_fallback", components=[])
        return best_design
