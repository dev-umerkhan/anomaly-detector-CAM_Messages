import argparse
import xml.etree.ElementTree as ET
import json

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", required=True, help="Input SUMO FCD XML")
    parser.add_argument("--outfile", required=True, help="Output JSONL file")
    return parser.parse_args()

def main():
    args = parse_args()

    tree = ET.parse(args.infile)
    root = tree.getroot()

    with open(args.outfile, "w") as out:
        for timestep in root.findall("timestep"):
            t = float(timestep.get("time"))

            for veh in timestep.findall("vehicle"):
                # SUMO sometimes uses x/y for lon/lat when using geo projection
                lat = veh.get("lat")
                lon = veh.get("lon")

                # If lat/lon missing, use x/y
                if lat is None or lon is None:
                    lon = veh.get("x")
                    lat = veh.get("y")

                record = {
                    "time": t,
                    "vehicle_id": veh.get("id"),
                    "lat": float(lat),
                    "lon": float(lon),
                    "speed": float(veh.get("speed")),
                }

                out.write(json.dumps(record) + "\n")

    print(f"✔ CAM-style JSONL saved → {args.outfile}")

if __name__ == "__main__":
    main()

