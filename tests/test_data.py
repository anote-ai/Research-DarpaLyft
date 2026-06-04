"""Tests for darpalyft.data."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from darpalyft.data import (
    make_component, make_baseline_design, make_design_variants, STANDARD_COMPONENTS,
)
from darpalyft.core import DroneComponent, DroneDesign


def test_make_component_type():
    c = make_component()
    assert isinstance(c, DroneComponent)


def test_make_baseline_design_mass_positive():
    d = make_baseline_design()
    assert d.total_mass() > 0


def test_make_design_variants_length():
    variants = make_design_variants(n=5)
    assert len(variants) == 5


def test_standard_components_length():
    assert len(STANDARD_COMPONENTS) == 6
