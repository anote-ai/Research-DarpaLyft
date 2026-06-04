"""Tests for darpalyft.core."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from darpalyft.core import (
    MaterialType, MATERIAL_DENSITY, MATERIAL_STRENGTH,
    DroneComponent, DroneDesign, PhysicsConstraints,
    motor_thrust_n, structural_safety_factor, payload_capacity,
    DesignOptimizer,
)


def test_material_type_values():
    values = {m.value for m in MaterialType}
    assert values == {"CARBON_FIBER", "ALUMINUM_ALLOY", "TITANIUM", "FIBERGLASS", "ABS_PLASTIC"}


def test_material_type_count():
    assert len(MaterialType) == 5


def test_material_density_has_all():
    for m in MaterialType:
        assert m in MATERIAL_DENSITY


def _make_design(mass=1.0):
    c = DroneComponent("C0", "frame", MaterialType.CARBON_FIBER, mass, 0.01, True)
    return DroneDesign(components=[c], motor_count=4, propeller_diameter_m=0.3, battery_capacity_wh=800.0)


def test_drone_design_total_mass():
    d = _make_design(mass=2.5)
    assert abs(d.total_mass() - 2.5) < 1e-9


def test_drone_design_component_count():
    d = _make_design()
    assert d.component_count() == 1


def test_motor_thrust_positive():
    t = motor_thrust_n(4, 0.3)
    assert t > 0


def test_structural_safety_factor_positive():
    d = _make_design()
    ssf = structural_safety_factor(d)
    assert isinstance(ssf, float)
    assert ssf > 0


def test_payload_capacity():
    d = _make_design(mass=1.0)
    thrust = motor_thrust_n(4, 0.3)
    cap = payload_capacity(d, thrust)
    assert isinstance(cap, float)


def test_physics_constraints_defaults():
    pc = PhysicsConstraints()
    assert pc.max_total_mass_kg == 25.0
    assert pc.min_structural_factor == 1.5


def test_design_optimizer_instantiation():
    pc = PhysicsConstraints()
    opt = DesignOptimizer(constraints=pc, seed=1)
    assert opt.seed == 1


def test_random_design_returns_drone_design():
    pc = PhysicsConstraints()
    opt = DesignOptimizer(constraints=pc, seed=7)
    d = opt.random_design()
    assert isinstance(d, DroneDesign)
