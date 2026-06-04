"""Tests for darpalyft.core module."""

import pytest
from darpalyft.core import (
    MaterialType,
    DroneComponent,
    DroneDesign,
    PhysicsConstraints,
    DesignOptimizer,
    total_mass,
    payload_capacity,
    structural_safety_factor,
)


def make_component(
    cid: str,
    material: MaterialType = MaterialType.CARBON_FIBER,
    mass_kg: float = 1.0,
    area_m2: float = 0.5,
    load_bearing: bool = True,
) -> DroneComponent:
    return DroneComponent(
        component_id=cid,
        name=cid,
        material=material,
        mass_kg=mass_kg,
        area_m2=area_m2,
        load_bearing=load_bearing,
    )


def test_material_type_enum() -> None:
    assert MaterialType.CARBON_FIBER == "CARBON_FIBER"
    assert MaterialType.ABS_PLASTIC == "ABS_PLASTIC"
    assert len(MaterialType) == 5


def test_drone_component_construction() -> None:
    comp = make_component("FRAME")
    assert comp.component_id == "FRAME"
    assert comp.mass_kg == 1.0
    assert comp.load_bearing is True


def test_drone_component_invalid_mass() -> None:
    with pytest.raises(ValueError):
        DroneComponent(
            component_id="BAD", name="Bad", material=MaterialType.ABS_PLASTIC,
            mass_kg=-1.0, area_m2=0.1
        )


def test_drone_design_construction() -> None:
    design = DroneDesign(
        design_id="D001",
        components=[make_component("F1"), make_component("F2")],
        motor_count=6,
        propeller_diameter_m=0.4,
        battery_capacity_wh=200.0,
    )
    assert design.motor_count == 6
    assert len(design.components) == 2


def test_drone_design_invalid_motor_count() -> None:
    with pytest.raises(ValueError):
        DroneDesign(design_id="BAD", motor_count=0)


def test_physics_constraints_defaults() -> None:
    constraints = PhysicsConstraints()
    assert constraints.max_total_mass_kg == pytest.approx(25.0)
    assert constraints.min_structural_factor == pytest.approx(1.5)
    assert constraints.max_wing_loading == pytest.approx(50.0)


def test_total_mass_known_components() -> None:
    design = DroneDesign(
        design_id="D001",
        components=[
            make_component("C1", mass_kg=2.0),
            make_component("C2", mass_kg=3.5),
        ],
    )
    assert total_mass(design) == pytest.approx(5.5)


def test_total_mass_empty_design() -> None:
    design = DroneDesign(design_id="EMPTY")
    assert total_mass(design) == 0.0


def test_payload_capacity_basic() -> None:
    design = DroneDesign(
        design_id="D001",
        components=[make_component("C1", mass_kg=5.0)],
    )
    # max_thrust=100N; 100/9.81 - 5 ≈ 5.19 kg
    cap = payload_capacity(design, 100.0)
    assert cap == pytest.approx(100.0 / 9.81 - 5.0, rel=1e-6)


def test_structural_safety_factor_carbon_fiber() -> None:
    design = DroneDesign(
        design_id="D001",
        components=[make_component("C1", material=MaterialType.CARBON_FIBER, load_bearing=True)],
    )
    ssf = structural_safety_factor(design)
    assert ssf == pytest.approx(3.5)


def test_structural_safety_factor_no_components() -> None:
    design = DroneDesign(design_id="EMPTY")
    assert structural_safety_factor(design) == pytest.approx(1.0)


def test_design_optimizer_returns_design() -> None:
    opt = DesignOptimizer(seed=42)
    constraints = PhysicsConstraints()
    result = opt.optimize(constraints, n_iterations=20)
    assert isinstance(result, DroneDesign)
    assert result.design_id is not None
