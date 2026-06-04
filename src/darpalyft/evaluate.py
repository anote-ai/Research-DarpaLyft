"""Evaluation metrics for darpalyft."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .core import (
    DroneDesign,
    PhysicsConstraints,
    TaskRecord,
    TaskSequence,
    motor_thrust_n,
    payload_capacity,
    structural_safety_factor,
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
            if (
                payloads[j] >= payloads[i]
                and designs[j].total_mass() <= designs[i].total_mass()
                and (
                    payloads[j] > payloads[i]
                    or designs[j].total_mass() < designs[i].total_mass()
                )
            ):
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


# ---------------------------------------------------------------------------
# Continual learning metrics
# ---------------------------------------------------------------------------


def backward_transfer(sequence: TaskSequence) -> float:
    """Backward Transfer (BWT): mean change in accuracy on previously-learned tasks.

    BWT = (1 / (T-1)) * sum_{i=1}^{T-1} (R_{T,i} - R_{i,i})

    where R_{T,i} is the accuracy on task i measured after training on all T tasks,
    and R_{i,i} is the accuracy right after training on task i.

    Negative BWT indicates catastrophic forgetting.
    Records with accuracy_after_later=None are skipped.
    Returns 0.0 if no valid pairs exist.
    """
    valid = [
        r for r in sequence.records
        if r.accuracy_after_later is not None
    ]
    if not valid:
        return 0.0
    deltas = [r.accuracy_after_later - r.accuracy_after_training for r in valid]  # type: ignore[operator]
    return sum(deltas) / len(deltas)


def forward_transfer(sequence: TaskSequence) -> float:
    """Forward Transfer (FWT): mean accuracy gain on tasks before they are trained.

    FWT = (1 / (T-1)) * sum_{i=2}^{T} (R_{i-1,i} - b_i)

    where R_{i-1,i} is accuracy_before_training for task i (zero-shot from previous
    tasks), and b_i is a random-baseline accuracy (approximated as 0 here).

    Positive FWT indicates that prior tasks helped learn future tasks.
    Records with accuracy_before_training=None are skipped.
    Returns 0.0 if no valid records exist.
    """
    valid = [
        r for r in sequence.records
        if r.accuracy_before_training is not None
    ]
    if not valid:
        return 0.0
    return sum(r.accuracy_before_training for r in valid) / len(valid)  # type: ignore[misc]


def continual_learning_score(
    sequence: TaskSequence,
    bwt_weight: float = 0.5,
    fwt_weight: float = 0.5,
) -> float:
    """Composite continual learning score combining BWT and FWT.

    Score = bwt_weight * clip(BWT, -1, 1) * 0.5 + 0.5
          + fwt_weight * clip(FWT, 0, 1)
    Normalised to approximately [0, 1].
    """
    bwt = backward_transfer(sequence)
    fwt = forward_transfer(sequence)
    # Map BWT from [-1, 1] -> [0, 1]
    bwt_norm = max(0.0, min(1.0, (bwt + 1.0) / 2.0))
    fwt_norm = max(0.0, min(1.0, fwt))
    total_weight = bwt_weight + fwt_weight
    if total_weight == 0.0:
        return 0.0
    return (bwt_weight * bwt_norm + fwt_weight * fwt_norm) / total_weight


def plasticity_score(sequence: TaskSequence) -> float:
    """Mean accuracy immediately after training on each task.

    High plasticity = model quickly adapts to new tasks.
    """
    if not sequence.records:
        return 0.0
    return sum(r.accuracy_after_training for r in sequence.records) / len(sequence.records)


def stability_score(sequence: TaskSequence) -> float:
    """Fraction of tasks with non-negative backward transfer (no forgetting)."""
    valid = [
        r for r in sequence.records
        if r.accuracy_after_later is not None
    ]
    if not valid:
        return 1.0
    no_forgetting = sum(
        1 for r in valid
        if r.accuracy_after_later >= r.accuracy_after_training  # type: ignore[operator]
    )
    return no_forgetting / len(valid)


def domain_drift_penalty(sequence: TaskSequence) -> float:
    """Normalised domain drift count; higher means more distribution shift."""
    n = len(sequence.records)
    if n <= 1:
        return 0.0
    return sequence.domain_drift_count() / (n - 1)
