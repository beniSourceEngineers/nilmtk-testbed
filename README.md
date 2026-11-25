# nilmtk-testbed

A small, practical sandbox for **Non-Intrusive Load Monitoring (NILM)**: learning appliance "fingerprints" from aggregate voltage/current/power and disaggregating them, using [NILMTK](https://github.com/nilmtk/nilmtk) plus a lightweight, dependency-free event/signature toolkit for experimenting without any dataset.

## What's inside

```
nilmtk-testbed/
├── environment.yml           # conda env (NILMTK is easiest via conda)
├── requirements-lite.txt     # pip deps for the dataset-free parts + tests
├── src/nilm_fingerprints/    # our own minimal NILM toolkit (no NILMTK needed)
│   ├── synthetic.py          #   synthetic household with known ground truth
│   ├── events.py             #   step/event detection on P & Q
│   └── signatures.py         #   P-Q signature library + clustering
├── examples/
│   ├── 00_synthetic_fingerprints.py   # runs anywhere, no dataset
│   ├── 01_explore_dataset.py          # NILMTK: load & inspect REDD / UK-DALE
│   ├── 02_appliance_signatures.py     # NILMTK: activations -> fingerprints
│   └── 03_disaggregate_api.py         # NILMTK: train/test CO, Mean, (FHMM...)
├── scripts/convert_dataset.py  # raw REDD / UK-DALE -> NILMTK HDF5
├── tests/                      # pytest suite (NILMTK tests auto-skip)
└── data/README.md              # where to get datasets
```

## Quick start (no dataset needed)

```bash
pip install -r requirements-lite.txt
pip install -e .
python examples/00_synthetic_fingerprints.py   # writes pq_plane.png
pytest -q
```

## Full NILMTK setup

```bash
conda env create -f environment.yml
conda activate nilmtk-testbed
pip install -e .
```

Then download a dataset (see `data/README.md`) and convert it:

```bash
python scripts/convert_dataset.py redd   /path/to/redd/low_freq   data/redd.h5
python scripts/convert_dataset.py ukdale /path/to/ukdale          data/ukdale.h5
```

## Code snippets

**Load a dataset and look at a building**

```python
from nilmtk import DataSet

redd = DataSet("data/redd.h5")
redd.set_window(start="2011-04-18", end="2011-04-25")
elec = redd.buildings[1].elec

print(elec)                       # MeterGroup: mains + submeters
mains = elec.mains()
fridge = elec["fridge"]
top5 = elec.submeters().select_top_k(k=5)
```

**Pull data out as pandas**

```python
df = next(fridge.load(physical_quantity="power", ac_type="active", sample_period=6))
series = fridge.power_series_all_data(sample_period=6)
```

**Extract appliance activations (on-cycles) = raw fingerprints**

```python
activations = fridge.get_activations()     # list of pd.Series, one per on-cycle
print(len(activations), activations[0].max())
```

**Train & evaluate disaggregation with the NILMTK experiment API**

```python
from nilmtk.api import API
from nilmtk.disaggregate import CO, Mean

experiment = {
    "power": {"mains": ["apparent"], "appliance": ["active"]},
    "sample_rate": 60,
    "appliances": ["fridge", "microwave", "dish washer"],
    "methods": {"CO": CO({}), "Mean": Mean({})},
    "train": {"datasets": {"REDD": {"path": "data/redd.h5",
              "buildings": {1: {"start_time": "2011-04-18", "end_time": "2011-04-28"}}}}},
    "test":  {"datasets": {"REDD": {"path": "data/redd.h5",
              "buildings": {1: {"start_time": "2011-04-28", "end_time": "2011-05-01"}}}},
              "metrics": ["mae", "rmse", "f1score"]},
}
results = API(experiment)
for key, err in zip(results.errors_keys, results.errors):
    print(key); print(err)
```

**Dataset-free: detect events and match P-Q fingerprints**

```python
from nilm_fingerprints import synthetic, detect_events, SignatureLibrary

hh = synthetic.make_household(hours=6, seed=1)
events = detect_events(hh.aggregate, threshold=25)
lib = SignatureLibrary.from_ground_truth(hh)
print(lib.label_events(events).head())
```

## Notes & caveats

- NILMTK is pinned to older Python/pandas versions; use the conda env rather than your system Python.
- API names above match NILMTK 0.4.x. If something has moved, check the NILMTK docs / `nilmtk-contrib` (which hosts newer deep-learning disaggregators like Seq2Point, DAE, RNN).
- **Hardware safety:** never probe mains directly. Use a clip-on CT for current and an isolated step-down transformer for voltage, and have an electrician install anything inside the panel.
