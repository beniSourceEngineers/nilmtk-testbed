"""Dataset-free demo: generate a household, detect events, learn & match fingerprints.

    python examples/00_synthetic_fingerprints.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from nilm_fingerprints import synthetic, detect_events, SignatureLibrary, cluster_events

hh = synthetic.make_household(hours=8, seed=42)
events = detect_events(hh.aggregate, threshold=25)
print(f"Detected {len(events)} events (ground truth: {len(hh.log)})")

# 1) Supervised: learn fingerprints from sub-metered recordings
lib = SignatureLibrary.from_ground_truth(hh)
print("\nLearned signatures (dP W, dQ VAR):")
for name, (p, q) in lib.signatures.items():
    print(f"  {name:10s} {p:8.1f} {q:8.1f}")

labelled = lib.label_events(events)
truth = hh.log.set_index("time")
joined = labelled.join(truth, rsuffix="_true", how="inner")
acc = (joined["appliance"] == joined["appliance_true"]).mean()
print(f"\nEvent labelling accuracy: {acc:.1%} on {len(joined)} matched events")

# 2) Unsupervised: cluster events on the P-Q plane
clusters = cluster_events(events, n_clusters=len(lib.signatures))

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
hh.aggregate["P"].iloc[:7200].plot(ax=axes[0], lw=0.6)
axes[0].set(title="Aggregate active power (first 2 h)", ylabel="W")
on = events["dP"] > 0
axes[1].scatter(events["dP"].abs(), events["dQ"] * events["dP"].apply(lambda x: 1 if x > 0 else -1),
                c=clusters, cmap="tab10", s=25)
for name, (p, q) in lib.signatures.items():
    axes[1].annotate(name, (p, q), fontsize=9, xytext=(5, 5), textcoords="offset points")
axes[1].set(title="Event fingerprints on the P-Q plane", xlabel="|ΔP| (W)", ylabel="ΔQ (VAR)")
fig.tight_layout()
fig.savefig("pq_plane.png", dpi=120)
print("\nSaved pq_plane.png")
