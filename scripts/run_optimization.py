"""Run 100-iteration drone design optimization."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from darpalyft.core import PhysicsConstraints, DesignOptimizer, motor_thrust_n, payload_capacity
from darpalyft.evaluate import optimization_report, is_feasible


def main() -> None:
    constraints = PhysicsConstraints()
    optimizer = DesignOptimizer(constraints=constraints, seed=42)

    print("Running 100-iteration optimization...")
    history = []
    for _ in range(100):
        d = optimizer.random_design()
        thrust = motor_thrust_n(d.motor_count, d.propeller_diameter_m)
        cap = payload_capacity(d, thrust)
        history.append((d, cap))

    best_design, best_payload = optimizer.optimize(n_iterations=100)
    print(f"Best design ID: {best_design.design_id}")
    print(f"Best payload capacity: {best_payload:.3f} kg")
    print(f"Total mass: {best_design.total_mass():.3f} kg")
    print(f"Motor count: {best_design.motor_count}")
    print(f"Propeller diameter: {best_design.propeller_diameter_m:.3f} m")

    report = optimization_report(history)
    print(f"Optimization report: {report}")


if __name__ == "__main__":
    main()
