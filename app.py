"""Streamlit dashboard: EMSR-b vs FCFS seat inventory control (synthetic demand)."""
import numpy as np
import pandas as pd
import streamlit as st
from scipy.stats import norm

st.set_page_config(page_title="EMSR-b Seat Inventory Control", layout="wide")

# ---------- core model (vectorised) ----------
def emsr_b(fares, means, sds, capacity):
    n = len(fares)
    y = np.zeros(n - 1)
    for j in range(n - 1):
        mu = means[: j + 1].sum()
        sd = np.sqrt((sds[: j + 1] ** 2).sum())
        pbar = (fares[: j + 1] * means[: j + 1]).sum() / mu
        ratio = min(max(fares[j + 1] / pbar, 1e-9), 1 - 1e-9)
        y[j] = max(0.0, mu + norm.ppf(1 - ratio) * sd)
    limits = np.clip(np.concatenate(([capacity], capacity - y)), 0, capacity)
    return y, limits

def simulate(fares, true_means, sds, capacity, limits, trials, seed):
    """Low-fare demand arrives first. limits=None -> FCFS."""
    rng = np.random.default_rng(seed)
    n = len(fares)
    demand = np.maximum(0, np.round(rng.normal(true_means, sds, size=(trials, n))))
    sold = np.zeros(trials)
    revenue = np.zeros(trials)
    for j in range(n - 1, -1, -1):
        cap_j = capacity if limits is None else limits[j]
        accept = np.clip(np.minimum(demand[:, j], cap_j - sold), 0, None)
        accept = np.minimum(accept, capacity - sold)
        sold += accept
        revenue += accept * fares[j]
    return revenue, sold

# ---------- sidebar ----------
st.title("Airline seat inventory control: EMSR-b vs first-come-first-served")
st.caption("Single flight leg, synthetic demand. A portfolio project on how forecast "
           "bias affects the value of seat protection.")

with st.sidebar:
    st.header("Inputs")
    capacity = st.slider("Seats on the flight", 50, 300, 100, 10)
    cv = st.slider("Demand variability (coefficient of variation)", 0.1, 0.8, 0.35, 0.05)
    bias = st.slider("Forecast bias (actual demand vs forecast)", -0.5, 0.3, 0.0, 0.05,
                     format="%.2f",
                     help="-0.30 means real demand is 30% lower than the forecast the optimiser used.")
    trials = st.select_slider("Simulated flights", [2000, 5000, 10000, 20000, 50000], 20000)
    seed = st.number_input("Random seed", 0, 9999, 42)

st.subheader("Fare classes and forecast demand")
default = pd.DataFrame({
    "Fare": [1200, 900, 650, 450, 300],
    "Forecast mean demand": [10, 14, 20, 28, 40],
}, index=["Class 1", "Class 2", "Class 3", "Class 4", "Class 5"])
table = st.data_editor(default, width="stretch")
table = table.sort_values("Fare", ascending=False)

fares = table["Fare"].to_numpy(float)
means = table["Forecast mean demand"].to_numpy(float)
sds = cv * means
labels = list(table.index)

if len(fares) < 2 or (means <= 0).any() or (fares <= 0).any():
    st.error("Enter at least two classes with positive fares and demand.")
    st.stop()

# ---------- optimise on the FORECAST, evaluate on ACTUAL demand ----------
y, limits = emsr_b(fares, means, sds, capacity)
actual_means = means * (1 + bias)

rev_f, sold_f = simulate(fares, actual_means, sds, capacity, None, trials, seed)
rev_e, sold_e = simulate(fares, actual_means, sds, capacity, limits, trials, seed)

c1, c2, c3, c4 = st.columns(4)
c1.metric("FCFS mean revenue", f"{rev_f.mean():,.0f}")
c2.metric("EMSR-b mean revenue", f"{rev_e.mean():,.0f}",
          f"{100 * (rev_e.mean() / rev_f.mean() - 1):+.1f}% vs FCFS")
c3.metric("FCFS load factor", f"{100 * sold_f.mean() / capacity:.0f}%")
c4.metric("EMSR-b load factor", f"{100 * sold_e.mean() / capacity:.0f}%")

left, right = st.columns(2)
with left:
    st.subheader("Booking limits from EMSR-b")
    st.caption("Maximum seats each class may sell (nested). The cheapest class is limited most.")
    bl = pd.DataFrame({"Booking limit": np.round(limits, 1)}, index=labels)
    st.bar_chart(bl)
    prot = pd.DataFrame({"Protected for higher classes": np.round(np.concatenate(([0], y)), 1)},
                        index=labels)
    st.dataframe(pd.concat([bl, prot], axis=1), width="stretch")
with right:
    st.subheader("Revenue distribution")
    bins = np.linspace(min(rev_f.min(), rev_e.min()), max(rev_f.max(), rev_e.max()), 40)
    hist = pd.DataFrame({
        "FCFS": np.histogram(rev_f, bins)[0],
        "EMSR-b": np.histogram(rev_e, bins)[0],
    }, index=np.round(bins[:-1]).astype(int))
    st.bar_chart(hist)

# ---------- bias sweep ----------
st.subheader("How forecast bias changes the benefit")
sweep_trials = min(trials, 10000)
rows = []
for b in np.arange(-0.5, 0.31, 0.1):
    f, _ = simulate(fares, means * (1 + b), sds, capacity, None, sweep_trials, seed)
    e, _ = simulate(fares, means * (1 + b), sds, capacity, limits, sweep_trials, seed)
    rows.append({"Forecast bias": round(b, 1), "EMSR-b vs FCFS (%)": 100 * (e.mean() / f.mean() - 1)})
sweep = pd.DataFrame(rows).set_index("Forecast bias")
st.line_chart(sweep)
st.caption("Negative bias means the forecast over-stated demand. Same random draws are used for "
           "both strategies at each point, so the comparison is not distorted by sampling noise.")

with st.expander("Method and limitations"):
    st.markdown("""
- EMSR-b protection levels are computed from the **forecast**; revenue is simulated against **actual** demand (forecast x (1 + bias)).
- Low-fare demand arrives first, the worst case for revenue. Demand is normal, rounded and floored at zero.
- Single leg only: no network (O&D) effects, overbooking, cancellations or recapture.
- Demand is synthetic. Next step: estimate demand per fare class from real route data (US DOT T-100 / DB1B).
""")
