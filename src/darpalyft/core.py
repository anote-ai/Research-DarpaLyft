"""Core data structures and physics for darpalyft."""
from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple


class MaterialType(str, Enum):
    CARBON_FIBER = "CARBON_FIBER"
    ALUMINUM_ALLOY = "ALUMINUM_ALLOY"
    TITANIUM = "TITANIUM"
    FIBERGLASS = "FIBERGLASS"
    ABS_PLASTIC = "ABS_PLASTIC"


MATERIAL_DENSITY: dict = {
    MaterialType.CARBON_FIBER: 1600.0,   # kg/m³
    MaterialType.ALUMINUM_ALLOY: 2700.0,
    MaterialType.TITANIUM: 4500.0,
    MaterialType.FIBERGLASS: 1900.0,
    MaterialType.ABS_PLASTIC: 1050.0,
}

MATERIAL_STRENGTH: dict = {
    MaterialType.CARBON_FIBER: 3500.0,   # MPa (UTS)
    MaterialType.ALUMINUM_ALLOY: 310.0,
    MaterialType.TITANIUM: 900.0,
    MaterialType.FIBERGLASS: 350.0,
    MaterialType.ABS_PLASTIC: 40.0,
}


@dataclass
class DroneComponent:
    component_id: str
    name: str
    material: MaterialType
    mass_kg: float
    volume_m3: float
    load_bearing: bool = False

    def __post_init__(self) -> None:
        if self.mass_kg < 0:
            raise ValueError(f"mass_kg must be >= 0, got {self.mass_kg}")
        if self.volume_m3 < 0:
            raise ValueError(f"volume_m3 must be >= 0, got {self.volume_m3}")


@dataclass
class DroneDesign:
    design_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    components: List[DroneComponent] = field(default_factory=list)
    motor_count: int = 4
    propeller_diameter_m: float = 0.3
    battery_capacity_wh: float = 800.0

    def __post_init__(self) -> None:
        if self.motor_count < 1:
            raise ValueError("motor_count must be >= 1")
        if self.propeller_diameter_m <= 0:
            raise ValueError("propeller_diameter_m must be > 0")
        if self.battery_capacity_wh <= 0:
            raise ValueError("battery_capacity_wh must be > 0")

    def total_mass(self) -> float:
        return sum(c.mass_kg for c in self.components)

    def component_count(self) -> int:
        return len(self.components)


@dataclass
class PhysicsConstraints:
    max_total_mass_kg: float = 25.0
    min_structural_factor: float = 1.5
    max_wing_loading_kg_m2: float = 50.0
    min_thrust_to_weight: float = 1.5


def motor_thrust_n(
    motor_count: int, propeller_diameter_m: float, throttle: float = 0.8
) -> float:
    """Simplified motor thrust in Newtons."""
    return 10.0 * motor_count * (propeller_diameter_m ** 2) * throttle


def structural_safety_factor(design: DroneDesign) -> float:
    """Simplified safety factor based on load-bearing component strengths."""
    lb_components = [c for c in design.components if c.load_bearing]
    if not lb_components:
        lb_components = design.components
    if not lb_components:
        return 1.0
    mean_strength = sum(MATERIAL_STRENGTH[c.material] for c in lb_components) / len(lb_components)
    return mean_strength / 100.0


def payload_capacity(design: DroneDesign, max_thrust_n: float) -> float:
    """Payload capacity in kg."""
    return max_thrust_n / 9.81 - design.total_mass()


class DesignOptimizer:
    """Random-search design optimizer."""

    def __init__(self, constraints: PhysicsConstraints, seed: int = 42) -> None:
        self.constraints = constraints
        self.seed = seed
        self._rng = random.Random(seed)

    def random_design(self) -> DroneDesign:
        """Generate a random feasible-ish drone design."""
        materials = list(MaterialType)
        components = [
            DroneComponent(
                component_id=f"C{i}",
                name=["frame", "arm", "motor_mount", "battery_tray", "payload_bay"][i % 5],
                material=self._rng.choice(materials),
                mass_kg=round(self._rng.uniform(0.1, 2.0), 3),
                volume_m3=round(self._rng.uniform(0.001, 0.05), 4),
                load_bearing=(i < 2),
            )
            for i in range(self._rng.randint(3, 6))
        ]
        return DroneDesign(
            components=components,
            motor_count=self._rng.choice([4, 6, 8]),
            propeller_diameter_m=round(self._rng.uniform(0.2, 0.5), 3),
            battery_capacity_wh=round(self._rng.uniform(400, 1200), 1),
        )

    def optimize(self, n_iterations: int = 50) -> Tuple[DroneDesign, float]:
        """Random search returning best (design, payload_capacity)."""
        from .evaluate import is_feasible, design_score  # lazy import

        best_design = None
        best_payload = -1e9
        for _ in range(n_iterations):
            d = self.random_design()
            thrust = motor_thrust_n(d.motor_count, d.propeller_diameter_m)
            cap = payload_capacity(d, thrust)
            if is_feasible(d, self.constraints) and cap > best_payload:
                best_payload = cap
                best_design = d
        if best_design is None:
            best_design = self.random_design()
            thrust = motor_thrust_n(best_design.motor_count, best_design.propeller_diameter_m)
            best_payload = payload_capacity(best_design, thrust)
        return best_design, best_payload
