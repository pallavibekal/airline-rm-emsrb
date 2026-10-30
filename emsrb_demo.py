"""
Single-leg seat inventory control: EMSR-b vs first-come-first-served (FCFS).
Starter project for a revenue-management portfolio piece.

Swap the synthetic inputs in `demand_inputs()` for real route data
(e.g. US DOT T-100 / DB1B) once you have a demand forecast per fare class.
"""
import numpy as np
from scipy.stats import norm

rng = np.random.default_rng(42)

def demand_inputs():
    # fare classes ordered high -> low
    fares = np.array([1200, 900, 650, 450, 300], dtype=float)
    means = np.array([10, 14, 20, 28, 40], dtype=float)
    cv = 0.35                      # coefficient of variation of demand
    sds = cv * means
    return fares, means, sds

def emsr_b(fares, means, sds, capacity):
    """Return protection levels y_j and booking limits (nested), classes high -> low."""
    n = len(fares)
    y = np.zeros(n - 1)
    for j in range(n - 1):
        mu = means[: j + 1].sum()
        sd = np.sqrt((sds[: j + 1] ** 2).sum())
        pbar = (fares[: j + 1] * means[: j + 1]).sum() / mu   # weighted avg fare
        z = norm.ppf(1 - fares[j + 1] / pbar)
        y[j] = max(0.0, mu + z * sd)
    booking_limits = np.concatenate(([capacity], capacity - y))
    return y, np.clip(booking_limits, 0, capacity)

def simulate(fares, true_means, sds, capacity, booking_limits=None, n_trials=20000):
    """Monte Carlo. Low-fare demand arrives first (worst case for revenue)."""
    n = len(fares)
    rev = np.zeros(n_trials)
    for t in range(n_trials):
        demand = np.maximum(0, np.round(rng.normal(true_means, sds)))
        sold_total, revenue = 0, 0.0
        for j in range(n - 1, -1, -1):             # lowest fare first
            limit = capacity if booking_limits is None else booking_limits[j]
            accept = int(max(0, min(demand[j], limit - sold_total, capacity - sold_total)))
            sold_total += accept
            revenue += accept * fares[j]
        rev[t] = revenue
    return rev

if __name__ == "__main__":
    capacity = 100
    fares, means, sds = demand_inputs()
    y, bl = emsr_b(fares, means, sds, capacity)
    print("Protection levels y_j:", np.round(y, 1))
    print("Booking limits (high->low):", np.round(bl, 1))

    print("\nScenario: forecast is right")
    fcfs = simulate(fares, means, sds, capacity)
    emsr = simulate(fares, means, sds, capacity, bl)
    print(f"  FCFS  mean revenue: {fcfs.mean():,.0f}")
    print(f"  EMSRb mean revenue: {emsr.mean():,.0f}  (+{100*(emsr.mean()/fcfs.mean()-1):.1f}%)")

    print("\nScenario: forecast over-states demand (calibration risk)")
    print("  bias  | EMSRb revenue | vs FCFS")
    for bias in [0.0, -0.15, -0.30]:
        true_means = means * (1 + bias)            # actual demand vs forecast
        f = simulate(fares, true_means, sds, capacity)
        e = simulate(fares, true_means, sds, capacity, bl)
        print(f"  {bias:+.0%} | {e.mean():>12,.0f} | {100*(e.mean()/f.mean()-1):+.1f}%")
