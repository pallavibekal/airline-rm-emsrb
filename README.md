# Airline Seat Inventory Control: EMSR-b vs First-Come-First-Served

**Live dashboard:** https://airline-rm-emsrb-wctgyomxsycmqncm6hdlza.streamlit.app/

A single-leg revenue management project. It compares EMSR-b nested booking
limits with first-come-first-served (FCFS) selling, and tests how forecast
bias changes the value of seat protection.

> Status: demand is synthetic. Next step is to estimate demand per fare class
> from real route data (US DOT T-100 / DB1B).

## Question

How much revenue does protecting seats for high fares add on one flight, and
how much of that benefit survives when the demand forecast is wrong?

## Method

- One flight, 100 seats, five fare classes (1200, 900, 650, 450, 300).
- Demand per class is normal, with a coefficient of variation of 0.35.
- EMSR-b protection levels and booking limits computed from the forecast.
- Monte Carlo simulation of 20,000 flights against actual demand
  (forecast x (1 + bias)), with low-fare demand arriving first.
- Baseline: FCFS with no seat protection.

## Results (synthetic demand)

| Scenario | EMSR-b vs FCFS |
|---|---|
| Forecast correct | about +14% revenue |
| Demand over-forecast by 15% | about +3% |
| Demand over-forecast by 30% | about -2% |

Seat protection adds material revenue when the forecast is right. The benefit
shrinks as forecast bias grows, and a large enough bias makes it worse than
FCFS. Forecast calibration matters as much as the optimisation algorithm.

## Run it

    conda create -n rm-project python=3.11 numpy scipy pandas matplotlib -y
    conda activate rm-project
    pip install streamlit
    python emsrb_demo.py        # command-line simulation
    streamlit run app.py        # interactive dashboard

## Files

- `emsrb_demo.py` - command-line simulation of EMSR-b vs FCFS
- `app.py` - Streamlit dashboard
- `requirements.txt` - dependencies for deployment
- `docs/index.md` - project write-up (GitHub Pages)

## Limitations

- Single leg only: no network (O&D) effects, overbooking, cancellations or recapture.
- Synthetic demand. Small differences between runs are Monte Carlo noise.

## Author

Pallavi Krishna - [Portfolio](https://www.pallavikrishnadata.com) | [LinkedIn](https://www.linkedin.com/in/pallavikrish/)
