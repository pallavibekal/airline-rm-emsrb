# Airline Seat Inventory Control: EMSR-b vs First-Come-First-Served

**Question:** How much revenue does protecting seats for high fares add on a single flight, and how much of that benefit survives when the demand forecast is wrong?

## Method

- One flight leg, capacity 100, five fare classes (1200, 900, 650, 450, 300).
- Demand per class is normally distributed (coefficient of variation 0.35).
- Booking limits from the EMSR-b heuristic, using nested protection levels.
- Monte Carlo simulation of 20,000 flights, with low-fare demand arriving first (the worst case for revenue).
- Baseline: first-come-first-served (no protection).

## Results (synthetic demand)

| Scenario | EMSR-b vs FCFS |
|---|---|
| Forecast correct | about +14% revenue |
| Demand over-forecast by 15% | about +3% |
| Demand over-forecast by 30% | about -2% |

## Takeaway

Seat protection adds material revenue when the forecast is right, but the benefit shrinks quickly as forecast bias grows, and a large enough bias makes it worse than selling first-come-first-served. Forecast calibration matters as much as the optimisation algorithm.

## Limitations and next steps

- Demand here is synthetic. Next step: fit demand per fare class from real route data (US DOT T-100 / DB1B).
- Single leg only; no network (O&D) effects, overbooking or recapture.
- Small differences between runs are Monte Carlo noise.

[Code on GitHub](https://github.com/pallavibekal/airline-rm-emsrb)
