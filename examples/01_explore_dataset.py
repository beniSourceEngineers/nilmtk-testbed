"""Load a converted NILMTK dataset and inspect it.

    python examples/01_explore_dataset.py data/redd.h5 --building 1
"""
import argparse

from nilmtk import DataSet

ap = argparse.ArgumentParser()
ap.add_argument("path")
ap.add_argument("--building", type=int, default=1)
ap.add_argument("--start", default=None)
ap.add_argument("--end", default=None)
args = ap.parse_args()

ds = DataSet(args.path)
if args.start or args.end:
    ds.set_window(start=args.start, end=args.end)

print("Buildings:", list(ds.buildings))
elec = ds.buildings[args.building].elec
print(elec)

mains = elec.mains()
print("\nMains available AC types:", mains.available_ac_types("power"))
print("Total mains energy (kWh):", mains.total_energy())

print("\nSubmeters by energy share:")
fraction = elec.submeters().fraction_per_meter().sort_values(ascending=False)
print(fraction.head(10))

# Pull one chunk of mains data into pandas
chunk = next(mains.load(physical_quantity="power", sample_period=6))
print("\nMains sample:\n", chunk.head())
