# Research: DARPA LIFT — Drone Payload Optimization

**Anote, Inc. | Defense AI Research**

---

## DARPA LIFT Challenge Context

The **DARPA Lifting Improved Flexible Technology (LIFT)** challenge targets advanced manufacturing and structural design for next-generation unmanned systems. This repository applies AI-driven design optimization to maximize payload-per-weight for small UAS platforms under realistic physics and structural constraints.

---

## Payload-Per-Weight Optimization

Maximize:
$$\text{score} = \frac{\text{payload\_kg}}{\text{total\_mass\_kg}}$$

Subject to:
- Total mass ≤ 25 kg
- Structural safety factor ≥ 1.5
- Thrust-to-weight ratio ≥ 1.5
- Wing loading ≤ 50 kg/m²

---

## Design Variables

| Variable | Type | Range |
|---|---|---|
| Frame material | Categorical | CARBON_FIBER, ALUMINUM_ALLOY, TITANIUM, FIBERGLASS, ABS_PLASTIC |
| Motor count | Integer | 4, 6, 8 |
| Propeller diameter | Continuous | 0.2 – 0.5 m |
| Battery capacity | Continuous | 400 – 1200 Wh |
| Component masses | Continuous | per component |

---

## Physics Constraints

- **Thrust model**: `T = 10 × N_motors × D_prop² × throttle` (simplified actuator disk)
- **Structural safety factor**: mean UTS of load-bearing materials / 100 MPa reference
- **Payload capacity**: `(T / 9.81) - total_mass`

---

## Optimization Methodology

1. **Random search baseline** (n=50–100 iterations)
2. **Pareto front analysis**: non-dominated designs by (payload, -total_mass)
3. **Physics feasibility filter**: applied at every iteration

---

## Results Template

| Method | Best Payload (kg) | Feasible Designs | Convergence Iter |
|---|---|---|---|
| Random Search (n=100) | TBD | TBD | TBD |

---

## Python Package (`src/darpalyft/`)

### Install

```bash
pip install -e ".[dev]"
```

### Quick Start

```python
from darpalyft.core import PhysicsConstraints, DesignOptimizer
from darpalyft.evaluate import optimization_report

constraints = PhysicsConstraints()
optimizer = DesignOptimizer(constraints=constraints, seed=42)
best_design, best_payload = optimizer.optimize(n_iterations=100)
print(f"Best payload: {best_payload:.2f} kg")
```

### Run Tests

```bash
pytest tests/ -v --cov=src
```

---

## DARPA Disclaimer

This research is conducted independently by Anote, Inc. and is not affiliated with or endorsed by DARPA. No export-controlled, classified, or proprietary data is used.

---

## Citation

```bibtex
@techreport{anote_darpalyft2026,
  author = {Vidra, Natan and Anote, Inc.},
  title  = {AI-Driven Payload Optimization for DARPA LIFT UAS Design},
  year   = {2026},
  url    = {https://github.com/anote-ai/research-darpalyft}
}
```
