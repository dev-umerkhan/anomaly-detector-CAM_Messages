# Part 1 — CAM Data Generation

## Repository Layout

```
part1-cam-generation/
├── data/
│   ├── map.osm
│   ├── deggendorf.net.xml
│   ├── trips.trips.xml
│   ├── routes.rou.xml
│   ├── vehicle_positions.xml
│   └── cam_data.jsonl
│
├── scripts/
│   ├── netconvert.sh
│   ├── run_sumo_fcd.sh
│   ├── xy_to_jsonl_stream.py
│   └── README.md
│
├── requirements.txt
└── LICENSE
```

---

## Prerequisites

### SUMO
Tested with SUMO 1.11, 1.10, 0.32+, and 6.2.  
Ensure these executables are in your PATH:

```
netconvert
duarouter
sumo
sumo-gui
```

### Python

```
pip install sumolib lxml tqdm pyproj
```

---

## Step 1 — Convert OSM → SUMO Network

```
netconvert    --osm-files map.osm    --proj.utm    --output-file deggendorf.net.xml
```

---

## Step 2 — Generate Trips & Routes

```
python3 $SUMO_HOME/tools/randomTrips.py -n deggendorf.net.xml -o trips.trips.xml -e 2000 -p 1

duarouter -n deggendorf.net.xml -t trips.trips.xml -o routes.rou.xml
```

---

## Step 3 — Run SUMO & Export FCD

```
sumo -n deggendorf.net.xml -r routes.rou.xml --fcd-output data/vehicle_positions.xml --fcd-output.geo --step-length 0.1
```

---

## Step 4 — Convert FCD XML → CAM JSONL

```
python3 xml_to_jsonl.py --infile vehicle_positions.xml --outfile cam_data.json
```

Example output line:

```json
{"time":12.3,"id":"veh_12","lat":48.84,"lon":12.96,"speed":13.4,"heading":179.2}
```

---

## Script Options

| Flag | Description |
|------|-------------|
| `--net` | SUMO network (.net.xml) |
| `--fcd` | SUMO FCD file |
| `--out` | JSONL output |
| `--include-speed` | Add speed values |
| `--step-frequency` | Downsampling |
| `--bbox` | Geographic bounding box |

---

## Recommended Settings for ML

- SUMO `--step-length 0.1` → **10 Hz** CAM frequency  
- Optionally downsample to **5 Hz** or **2 Hz**  
- Use bounding boxes to reduce dataset size  
- Compress with gzip when storing

---

This completes **Part 1: CAM Data Generation Pipeline**.
