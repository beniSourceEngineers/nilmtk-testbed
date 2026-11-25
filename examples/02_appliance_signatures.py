"""Turn sub-metered appliance data into fingerprints (activations + summary stats).

    python examples/02_appliance_signatures.py data/redd.h5 --building 1
"""
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from nilmtk import DataSet

ap = argparse.ArgumentParser()
ap.add_argument("path")
ap.add_argument("--building", type=int, default=1)
ap.add_argument("--appliances", nargs="+", default=["fridge", "microwave", "dish washer"])
args = ap.parse_args()

elec = DataSet(args.path).buildings[args.building].elec
rows = []
fig, axes = plt.subplots(len(args.appliances), 1, figsize=(8, 3 * len(args.appliances)))

for ax, name in zip(axes, args.appliances):
    try:
        meter = elec[name]
    except KeyError:
        print(f"skip {name}: not in building {args.building}")
        continue
    acts = meter.get_activations()           # list of pd.Series (one on-cycle each)
    if not acts:
        continue
    peaks = [a.max() for a in acts]
    durs = [(a.index[-1] - a.index[0]).total_seconds() / 60 for a in acts]
    rows.append({"appliance": name, "n_activations": len(acts),
                 "median_peak_W": pd.Series(peaks).median(),
                 "median_duration_min": pd.Series(durs).median()})
    for a in acts[:5]:                         # overlay a few cycles
        ax.plot((a.index - a.index[0]).total_seconds() / 60, a.values, alpha=0.7)
    ax.set(title=name, xlabel="minutes since switch-on", ylabel="W")

print(pd.DataFrame(rows).to_string(index=False))
fig.tight_layout()
fig.savefig("activations.png", dpi=120)
print("Saved activations.png")
