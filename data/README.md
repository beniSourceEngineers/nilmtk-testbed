# Datasets

Datasets are NOT committed. Download, then convert with `scripts/convert_dataset.py`.

| Dataset | Rate | Notes |
|---|---|---|
| REDD | ~1 Hz mains / 1/3 Hz circuits | Classic US benchmark; request access from MIT |
| UK-DALE | 6 s appliances, 16 kHz mains (some houses) | 5 UK homes, long duration |
| PLAID | 30 kHz V & I | Individual appliance waveforms; great for V-I fingerprints |
| WHITED | 44 kHz | Appliance startup transients |

Converted files go here as `redd.h5`, `ukdale.h5`, etc.
