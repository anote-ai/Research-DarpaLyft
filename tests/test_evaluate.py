"""Tests for darpalyft.evaluate module."""

import pytest
from darpalyft.core import (
    DroneComponent,
    DroneDesign,
    MaterialType,
    PhysicsConstraints,
)
from darpalyft.evaluate import (
    payload_to_weight_ratio,
    is_feasible,
    design_score,
    pareto_designs,
)


def make_design(
    design_id: str,
    mass_kg: float = 5.0,
    area_m2: float = 1.0,
    material: MaterialType = MaterialType.CARBON_FIBER,
    load_bearing: bool = True,
) -> DroneDesign:
    comp = DroneComponent(
        component_id="C1",
        name="Frame",
        material=material,
        mass_kg=mass_kg,
        area_m2=area_m2,
        load_bearing=load_bearing,
    )
    return DroneDesign(design_id=design_id, components=[comp])


def test_payload_to_weight_ratio_basic() -> None:
    design = make_design("D1", mass_kg=5.0)
    ratio = payload_to_weight_ratio(design, payload_kg=10.0)
    assert ratio == pytest.approx(2.0)


def test_payload_to_weight_ratio_zero_mass() -> None:
    design = DroneDesign(design_id="EMPTY")
    assert payload_to_weight_ratio(design, 5.0) == 0.0


def test_is_feasible_within_constraints() -> None:
    constraints = PhysicsConstraints(max_total_mass_kg=25.0, min_structural_factor=1.5)
    # Carbon fiber SSF = 3.5 >= 1.5; mass = 5.0 <= 25.0
    design = make_design("D1", mass_kg=5.0, area_m2=5.0)  # wing loading = 5*9.81/5 = 9.81 < 50
    assert is_feasible(design, constraints) is True


def test_is_feasible_exceeds_mass() -> None:
    constraints = PhysicsConstraints(max_total_mass_kg=3.0)
    design = make_design("D1", mass_kg=5.0)
    assert is_feasible(design, constraints) is False


def test_is_feasible_weak_material() -> None:
    constraints = PhysicsConstraints(min_structural_factor=2.0)
    # ABS_PLASTIC SSF = 0.6 < 2.0
    design = make_design("D1", mass_kg=1.0, material=MaterialType.ABS_PLASTIC, area_m2=5.0)
    assert is_feasible(design, constraints) is False


def test_design_score_feasible() -> None:
    constraints = PhysicsConstraints()
    design = make_design("D1", mass_kg=5.0, area_m2=5.0)
    score = design_score(design, payload_kg=10.0, constraints=constraints)
    assert score == pytest.approx(2.0)


def test_design_score_infeasible_returns_zero() -> None:
    constraints = PhysicsConstraints(max_total_mass_kg=1.0)
    design = make_design("D1", mass_kg=5.0)
    assert design_score(design, 10.0, constraints) == 0.0


def test_pareto_designs_basic() -> None:
    # D1: payload=10, mass=5 — should be non-dominated
    # D2: payload=5, mass=10 — dominated by D1
    # D3: payload=10, mass=3 — dominates D1
    d1 = make_design("D1", mass_kg=5.0)
    d2 = make_design("D2", mass_kg=10.0)
    d3 = make_design("D3", mass_kg=3.0)
    pareto = pareto_designs([d1, d2, d3], [10.0, 5.0, 10.0])
    ids = [d.design_id for d in pareto]
    assert "D3" in ids
    assert "D2" not in ids


def test_pareto_designs_mismatched_lengths_raises() -> None:
    d1 = make_design("D1")
    with pytest.raises(ValueError):
        pareto_designs([d1], [1.0, 2.0])
