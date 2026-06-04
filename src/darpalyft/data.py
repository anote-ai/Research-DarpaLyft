"""Synthetic data generation for darpalyft."""
from __future__ import annotations

import random
from typing import List

from .core import MaterialType, DroneComponent, DroneDesign

STANDARD_COMPONENTS: List[dict] = [
    {"name": "frame", "material": MaterialType.CARBON_FIBER, "mass_kg": 1.2, "volume_m3": 0.02, "load_bearing": True},
    {"name": "arms", "material": MaterialType.ALUMINUM_ALLOY, "mass_kg": 0.6, "volume_m3": 0.005, "load_bearing": True},
    {"name": "motors", "material": MaterialType.ALUMINUM_ALLOY, "mass_kg": 0.4, "volume_m3": 0.002, "load_bearing": False},
    {"name": "battery", "material": MaterialType.ABS_PLASTIC, "mass_kg": 1.5, "volume_m3": 0.008, "load_bearing": False},
    {"name": "payload_bay", "material": MaterialType.CARBON_FIBER, "mass_kg": 0.3, "volume_m3": 0.01, "load_bearing": False},
    {"name": "landing_gear", "material": MaterialType.FIBERGLASS, "mass_kg": 0.2, "volume_m3": 0.003, "load_bearing": False},
]


def make_component(
    name: str = "frame",
    material: MaterialType = MaterialType.CARBON_FIBER,
    mass_kg: float = 0.5,
) -> DroneComponent:
    return DroneComponent(
        component_id=f"comp_{name}",
        name=name,
        material=material,
        mass_kg=mass_kg,
        volume_m3=mass_kg / 1600.0,
        load_bearing=(name in {"frame", "arms"}),
    )


def make_baseline_design(seed: int = 42) -> DroneDesign:
    """Realistic baseline quadcopter design."""
    components = [
        DroneComponent("C0", "frame", MaterialType.CARBON_FIBER, 3.0, 0.02, True),
        DroneComponent("C1", "arms", MaterialType.CARBON_FIBER, 0.8, 0.005, True),
        DroneComponent("C2", "motors", MaterialType.ALUMINUM_ALLOY, 0.6, 0.002, False),
        DroneComponent("C3", "battery", MaterialType.ABS_PLASTIC, 2.0, 0.01, False),
        DroneComponent("C4", "payload_bay", MaterialType.CARBON_FIBER, 0.5, 0.008, False),
        DroneComponent("C5", "landing_gear", MaterialType.FIBERGLASS, 0.3, 0.003, False),
    ]
    return DroneDesign(
        design_id="baseline",
        components=components,
        motor_count=4,
        propeller_diameter_m=0.3,
        battery_capacity_wh=800.0,
    )


def make_design_variants(n: int = 5, seed: int = 42) -> List[DroneDesign]:
    """Generate varied design configurations."""
    rng = random.Random(seed)
    materials = list(MaterialType)
    motor_options = [4, 6, 8]
    variants = []
    for i in range(n):
        components = [
            DroneComponent(f"V{i}C{j}", c["name"], rng.choice(materials),
                           round(c["mass_kg"] * rng.uniform(0.7, 1.3), 3),
                           c["volume_m3"], c["load_bearing"])
            for j, c in enumerate(STANDARD_COMPONENTS[:4])
        ]
        variants.append(DroneDesign(
            components=components,
            motor_count=rng.choice(motor_options),
            propeller_diameter_m=round(rng.uniform(0.25, 0.5), 3),
            battery_capacity_wh=round(rng.uniform(500, 1200), 1),
        ))
    return variants
