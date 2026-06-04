"""Evaluation utilities for drone design optimization."""

from __future__ import annotations

from darpalyft.core import DroneDesign, PhysicsConstraints, structural_safety_factor, total_mass


def payload_to_weight_ratio(design: DroneDesign, payload_kg: float) -> float:
    """Compute payload-to-weight ratio for a design carrying a given payload.

    Ratio = payload_kg / total_structural_mass(design).
    Returns 0.0 if structural mass is zero.

    Args:
        design: DroneDesign instance.
        payload_kg: Payload mass in kg.

    Returns:
        Dimensionless payload-to-weight ratio.
    """
    mass = total_mass(design)
    if mass == 0.0:
        return 0.0
    return payload_kg / mass


def is_feasible(design: DroneDesign, constraints: PhysicsConstraints) -> bool:
    """Check whether a design satisfies all physics constraints.

    Args:
        design: DroneDesign to evaluate.
        constraints: PhysicsConstraints thresholds.

    Returns:
        True if all constraints are satisfied.
    """
    mass = total_mass(design)
    if mass > constraints.max_total_mass_kg:
        return False
    ssf = structural_safety_factor(design)
    if ssf < constraints.min_structural_factor:
        return False
    # Wing loading check: mass * g / total_area
    total_area = sum(c.area_m2 for c in design.components)
    if total_area > 0:
        wing_loading = (mass * 9.81) / total_area
        if wing_loading > constraints.max_wing_loading:
            return False
    return True


def design_score(
    design: DroneDesign,
    payload_kg: float,
    constraints: PhysicsConstraints,
) -> float:
    """Compute composite design score.

    Returns 0.0 for infeasible designs, payload_to_weight_ratio otherwise.

    Args:
        design: DroneDesign to score.
        payload_kg: Payload mass in kg.
        constraints: PhysicsConstraints thresholds.

    Returns:
        Score scalar (higher is better).
    """
    if not is_feasible(design, constraints):
        return 0.0
    return payload_to_weight_ratio(design, payload_kg)


def pareto_designs(
    designs: list[DroneDesign],
    payloads: list[float],
) -> list[DroneDesign]:
    """Return Pareto-optimal designs: non-dominated by (high payload, low mass).

    A design d1 dominates d2 if payload[d1] >= payload[d2] AND mass[d1] <= mass[d2],
    with at least one strict inequality.

    Args:
        designs: List of DroneDesign instances.
        payloads: Corresponding payload capacities (same length as designs).

    Returns:
        Subset of designs on the Pareto front.
    """
    if len(designs) != len(payloads):
        raise ValueError("designs and payloads must have the same length.")

    pareto: list[DroneDesign] = []
    masses = [total_mass(d) for d in designs]

    for i, (d, p, m) in enumerate(zip(designs, payloads, masses)):
        dominated = False
        for j, (p2, m2) in enumerate(zip(payloads, masses)):
            if i == j:
                continue
            # d is dominated by j if j has >= payload AND <= mass with one strict
            if p2 >= p and m2 <= m and (p2 > p or m2 < m):
                dominated = True
                break
        if not dominated:
            pareto.append(d)
    return pareto
