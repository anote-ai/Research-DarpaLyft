"""Tests for darpalyft.evaluate."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from darpalyft.core import (
    MaterialType, DroneComponent, DroneDesign, PhysicsConstraints,
    motor_thrust_n, payload_capacity,
)
from darpalyft.evaluate import (
    total_thrust_n, payload_to_weight_ratio, is_feasible,
    design_score, pareto_designs, optimization_report,
)


def _heavy_design():
    """A design that is clearly too heavy."""
    c = DroneComponent("C0", "frame", MaterialType.CARBON_FIBER, 100.0, 0.1, True)
    return DroneDesign(components=[c], motor_count=4, propeller_diameter_m=0.3, battery_capacity_wh=800.0)


def _feasible_design():
    """A light design that should pass all checks."""
    c = DroneComponent("C0", "frame", MaterialType.CARBON_FIBER, 0.5, 0.01, True)
    return DroneDesign(components=[c], motor_count=8, propeller_diameter_m=0.5, battery_capacity_wh=800.0)


def test_total_thrust_positive():
    d = _feasible_design()
    assert total_thrust_n(d) > 0


def test_payload_to_weight_ratio():
    d = _feasible_design()
    ratio = payload_to_weight_ratio(d, 1.0)
    assert ratio == 1.0 / d.total_mass()


def test_is_feasible_heavy_false():
    d = _heavy_design()
    pc = PhysicsConstraints()
    assert not is_feasible(d, pc)


def test_is_feasible_good_design():
    d = _feasible_design()
    pc = PhysicsConstraints()
    assert is_feasible(d, pc)


def test_design_score_infeasible_zero():
    d = _heavy_design()
    pc = PhysicsConstraints()
    assert design_score(d, 5.0, pc) == 0.0


def test_pareto_designs_non_dominated():
    c1 = DroneComponent("C0", "frame", MaterialType.CARBON_FIBER, 0.5, 0.01, True)
    c2 = DroneComponent("C1", "frame", MaterialType.TITANIUM, 2.0, 0.02, True)
    d1 = DroneDesign(components=[c1], motor_count=4, propeller_diameter_m=0.3, battery_capacity_wh=800.0)
    d2 = DroneDesign(components=[c2], motor_count=4, propeller_diameter_m=0.3, battery_capacity_wh=800.0)
    # d1 has lower mass and higher payload => dominates d2
    pareto = pareto_designs([d1, d2], [10.0, 5.0])
    assert d1 in pareto


def test_optimization_report_structure():
    d = _feasible_design()
    history = [(d, 3.5), (d, 4.0), (d, 2.0)]
    report = optimization_report(history)
    assert "best_payload" in report
    assert abs(report["best_payload"] - 4.0) < 1e-9
    assert report["convergence_iter"] == 1
