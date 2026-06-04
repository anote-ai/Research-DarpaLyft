# DarpaLyft: Payload-per-Weight Optimization for DARPA LIFT Challenge

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)

Computational design and optimization study maximizing drone **payload-to-weight ratio** for the **DARPA LIFT (Lifting Intelligence From Technology) Challenge**.

## DARPA LIFT Challenge Context

The DARPA LIFT Challenge pushes the boundaries of drone payload efficiency, requiring participants to design autonomous aircraft that maximize the ratio of useful payload to total vehicle weight. Key objectives:

- Maximize `payload_kg / structural_mass_kg`
- Satisfy structural safety margins (safety factor >= 1.5)
- Comply with FAA/DoD regulatory mass limits (≤ 25 kg MTOW)
- Minimize wing loading for stable flight

## Design Variables

| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| Material | Categorical | 5 types | Structural material per component |
| Component mass | Continuous | 0.1–5.0 kg | Per-component mass |
| Motor count | Integer | 4, 6, 8 | Number of propulsion motors |
| Propeller diameter | Continuous | 0.2–0.6 m | Prop diameter |
| Battery capacity | Continuous | 50–500 Wh | Energy storage |

## Material Properties

| Material | Density (kg/m³) | Relative Strength |
|----------|----------------|-------------------|
| Carbon Fiber | 1600 | 3.5 |
| Aluminum Alloy | 2700 | 1.5 |
| Titanium | 4500 | 2.5 |
| Fiberglass | 1900 | 1.2 |
| ABS Plastic | 1050 | 0.6 |

## Optimization Methodology

1. **Random Search Baseline**: Sample designs uniformly over parameter space
2. **Surrogate Model** (planned): Gaussian Process or MLP trained on evaluated designs
3. **Bayesian Optimization** (planned): Acquisition function-guided search
4. **Pareto Analysis**: Multi-objective Pareto front over (payload, mass)

## Physics Constraints

```
max_total_mass_kg = 25.0    # MTOW limit
min_structural_factor = 1.5  # Safety margin
max_wing_loading = 50.0 N/m² # Stability constraint
```

## Quickstart

```bash
pip install -e ".[dev]"
```

```python
from darpalyft.core import PhysicsConstraints, DesignOptimizer
from darpalyft.evaluate import design_score, pareto_designs

constraints = PhysicsConstraints(max_total_mass_kg=25.0)
optimizer = DesignOptimizer(seed=42)

best = optimizer.optimize(constraints, n_iterations=500)
print(f"Best design: {best.design_id}")
print(f"Score: {design_score(best, payload_kg=10.0, constraints=constraints):.3f}")
```

## Running Tests

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

## Results Template

| Design ID | Mass (kg) | Payload (kg) | P/W Ratio | Feasible |
|-----------|-----------|--------------|-----------|----------|
| D_baseline | 12.4 | 8.1 | 0.65 | Yes |
| D_carbon_opt | 7.2 | 9.8 | 1.36 | Yes |
| D_ultra_light | 4.9 | 11.2 | 2.29 | Yes |

## DARPA Challenge Disclaimer

This repository is an independent research study. It is not affiliated with, endorsed by, or submitted to DARPA. All designs and simulations are for research and educational purposes only.

## Citation

```bibtex
@misc{anoteai2025darpalyft,
  title        = {DarpaLyft: Payload-per-Weight Optimization Study for DARPA LIFT},
  author       = {Anote AI},
  year         = {2025},
  howpublished = {\url{https://github.com/anote-ai/research-darpalyft}},
  note         = {DARPA LIFT Challenge Research}
}
```

## License

Apache 2.0
