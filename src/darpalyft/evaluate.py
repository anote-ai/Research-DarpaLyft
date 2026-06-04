"""Evaluation metrics for darpalyft."""
from __future__ import annotations

from typing import List, Dict, Tuple

from .core import (
    DroneDesign, PhysicsConstraints,
    motor_thrust_n, structural_safety_factor, payload_capacity,
)


def total_thrust_n(design: DroneDesign) -> float:
    """Total thrust for a design at default throttle."""
    return motor_thrust_n(design.motor_count, design.propeller_diameter_m)


def payload_to_weight_ratio(design: DroneDesign, payload_kg: float) -> float:
    """Payload mass divided by total design mass."""
    return payload_kg / max(design.total_mass(), 1e-9)


def is_feasible(design: DroneDesign, constraints: PhysicsConstraints) -> bool:
    """Check all physics constraints."""
    if design.total_mass() > constraints.max_total_mass_kg:
        return False
    if structural_safety_factor(design) < constraints.min_structural_factor:
        return False
    thrust = total_thrust_n(design)
    if thrust < constraints.min_thrust_to_weight * design.total_mass() * 9.81:
        return False
    return True


def design_score(
    design: DroneDesign, payload_kg: float, constraints: PhysicsConstraints
) -> float:
    """0 if infeasible, else payload-to-weight ratio."""
    if not is_feasible(design, constraints):
        return 0.0
    return payload_to_weight_ratio(design, payload_kg)


def pareto_designs(
    designs: List[DroneDesign], payloads: List[float]
) -> List[DroneDesign]:
    """Return non-dominated designs by (payload, -total_mass)."""
    dominated = set()
    n = len(designs)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            # j dominates i if j is better on both objectives
            if (payloads[j] >= payloads[i] and
                    designs[j].total_mass() <= designs[i].total_mass() and
                    (payloads[j] > payloads[i] or designs[j].total_mass() < designs[i].total_mass())):
                dominated.add(i)
    return [d for idx, d in enumerate(designs) if idx not in dominated]


def optimization_report(
    history: List[Tuple[DroneDesign, float]]
) -> Dict:
    """Summarize optimization run."""
    if not history:
        return {"best_payload": 0.0, "best_design_id": "", "n_feasible": 0, "convergence_iter": 0}
    best_idx = max(range(len(history)), key=lambda i: history[i][1])
    best_design, best_payload = history[best_idx]
    n_feasible = sum(1 for _, p in history if p > 0)
    return {
        "best_payload": best_payload,
        "best_design_id": best_design.design_id,
        "n_feasible": n_feasible,
        "convergence_iter": best_idx,
    }
