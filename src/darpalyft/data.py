"""Synthetic data generation for darpalyft."""
from __future__ import annotations

import random
from typing import List

from .core import (
    DroneComponent,
    DroneDesign,
    MaterialType,
    TaskDomain,
    TaskRecord,
    TaskSequence,
)

STANDARD_COMPONENTS: List[dict] = [
    {"name": "frame", "material": MaterialType.CARBON_FIBER, "mass_kg": 1.2, "volume_m3": 0.02, "load_bearing": True},
    {"name": "arms", "material": MaterialType.ALUMINUM_ALLOY, "mass_kg": 0.6, "volume_m3": 0.005, "load_bearing": True},
    {"name": "motors", "material": MaterialType.ALUMINUM_ALLOY, "mass_kg": 0.4, "volume_m3": 0.002, "load_bearing": False},
    {"name": "battery", "material": MaterialType.ABS_PLASTIC, "mass_kg": 1.5, "volume_m3": 0.008, "load_bearing": False},
    {"name": "payload_bay", "material": MaterialType.CARBON_FIBER, "mass_kg": 0.3, "volume_m3": 0.01, "load_bearing": False},
    {"name": "landing_gear", "material": MaterialType.FIBERGLASS, "mass_kg": 0.2, "volume_m3": 0.003, "load_bearing": False},
]

# Domain-specific accuracy degradation profiles (how much accuracy drops per domain shift)
_DOMAIN_DRIFT_DIFFICULTY: dict = {
    TaskDomain.URBAN: 0.05,
    TaskDomain.MARITIME: 0.10,
    TaskDomain.MOUNTAIN: 0.12,
    TaskDomain.DESERT: 0.08,
    TaskDomain.ARCTIC: 0.15,
}


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


# ---------------------------------------------------------------------------
# Task sequence generation for continual learning benchmarks
# ---------------------------------------------------------------------------


def make_task_record(
    task_id: str,
    domain: TaskDomain,
    base_accuracy: float = 0.80,
    forgetting: float = 0.05,
    forward_gain: float = 0.0,
    seed: int = 42,
) -> TaskRecord:
    """Create a realistic TaskRecord with optional forgetting and forward transfer."""
    rng = random.Random(seed)
    noise = rng.uniform(-0.02, 0.02)
    acc_after = max(0.0, min(1.0, base_accuracy + noise))
    acc_later: float | None = max(0.0, min(1.0, acc_after - forgetting + rng.uniform(-0.01, 0.01)))
    acc_before: float | None = max(0.0, min(1.0, forward_gain + rng.uniform(0.0, 0.05)))
    return TaskRecord(
        task_id=task_id,
        domain=domain,
        accuracy_after_training=acc_after,
        accuracy_after_later=acc_later,
        accuracy_before_training=acc_before,
    )


def make_task_sequence(
    n_tasks: int = 6,
    seed: int = 42,
    domain_drift: bool = True,
) -> TaskSequence:
    """Generate a synthetic task sequence with realistic domain drift.

    When domain_drift=True, domains are shuffled to maximise distribution shift.
    When domain_drift=False, the same domain is repeated (iid continuum).
    """
    rng = random.Random(seed)
    domains = list(TaskDomain)
    if domain_drift:
        # Cycle through domains to guarantee drift at every step
        selected = [domains[i % len(domains)] for i in range(n_tasks)]
        rng.shuffle(selected)
    else:
        selected = [domains[0]] * n_tasks

    records: List[TaskRecord] = []
    prev_accuracy = 0.75
    for i, domain in enumerate(selected):
        drift_penalty = _DOMAIN_DRIFT_DIFFICULTY.get(domain, 0.05)
        base = max(0.5, prev_accuracy - drift_penalty + rng.uniform(0.0, 0.1))
        record = make_task_record(
            task_id=f"T{i:03d}",
            domain=domain,
            base_accuracy=base,
            forgetting=rng.uniform(0.02, 0.10),
            forward_gain=rng.uniform(0.0, 0.10),
            seed=rng.randint(0, 99999),
        )
        records.append(record)
        prev_accuracy = record.accuracy_after_training

    return TaskSequence(records=records)


def make_iid_sequence(n_tasks: int = 6, seed: int = 42) -> TaskSequence:
    """Generate a sequence with no domain drift (iid baseline)."""
    return make_task_sequence(n_tasks=n_tasks, seed=seed, domain_drift=False)


def make_catastrophic_forgetting_sequence(n_tasks: int = 5, seed: int = 0) -> TaskSequence:
    """Sequence where each later task almost completely overwrites earlier ones."""
    rng = random.Random(seed)
    domains = list(TaskDomain)
    records = []
    for i in range(n_tasks):
        domain = domains[i % len(domains)]
        record = TaskRecord(
            task_id=f"CF{i:03d}",
            domain=domain,
            accuracy_after_training=round(rng.uniform(0.7, 0.95), 3),
            accuracy_after_later=round(rng.uniform(0.10, 0.30), 3),  # severe forgetting
            accuracy_before_training=round(rng.uniform(0.0, 0.05), 3),
        )
        records.append(record)
    return TaskSequence(records=records)
