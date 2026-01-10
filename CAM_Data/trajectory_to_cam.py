#!/usr/bin/env python3

import json
import argparse
import math

# -------------------------
# Utility functions
# -------------------------

def haversine(lat1, lon1, lat2, lon2):
    """Distance in meters between two lat/lon points"""
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def bearing(lat1, lon1, lat2, lon2):
    """Compute heading (bearing) in degrees from point 1 to point 2"""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1

    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - \
        math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

    brng = math.atan2(x, y)
    return (math.degrees(brng) + 360) % 360


def angle_diff(a, b):
    """Smallest difference between two headings (degrees)"""
    d = abs(a - b) % 360
    return min(d, 360 - d)


# -------------------------
# Main CAM generator
# -------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", required=True, help="trajectory jsonl")
    parser.add_argument("--outfile", default="cam_messages.jsonl")
    parser.add_argument("--T", type=float, default=1.0, help="CAM period (s)")
    parser.add_argument("--D", type=float, default=4.0, help="distance trigger (m)")
    parser.add_argument("--V", type=float, default=0.5, help="speed trigger (m/s)")
    parser.add_argument("--H", type=float, default=4.0, help="heading trigger (deg)")
    args = parser.parse_args()

    last_state = {}  # per vehicle

    with open(args.infile, "r") as fin, open(args.outfile, "w") as fout:
        for line in fin:
            rec = json.loads(line)

            vid = rec["vehicle_id"]
            t = float(rec["time"])
            lat = rec["lat"]
            lon = rec["lon"]
            speed = rec.get("speed", 0.0)

            # ---- heading computation ----
            if vid in last_state:
                prev = last_state[vid]
                heading = bearing(prev["lat"], prev["lon"], lat, lon)
            else:
                heading = None  # undefined for first CAM

            send_cam = False

            if vid not in last_state:
                send_cam = True
            else:
                prev = last_state[vid]

                dt = t - prev["time"]
                dist = haversine(prev["lat"], prev["lon"], lat, lon)
                dv = abs(speed - prev["speed"])
                if heading is None or prev["heading"] is None:
                    dh = 0
                else:
                    dh = angle_diff(heading, prev["heading"])


                if dt >= args.T:
                    send_cam = True
                elif dist >= args.D:
                    send_cam = True
                elif dv >= args.V:
                    send_cam = True
                elif heading is not None and dh >= args.H:
                    send_cam = True

            if send_cam:
                cam = {
                    "time": t,
                    "vehicle_id": vid,
                    "lat": lat,
                    "lon": lon,
                    "speed": speed,
                    "heading": heading,
                    "cam_type": "CAM",
                    "label": "normal"
                }
                fout.write(json.dumps(cam) + "\n")

                last_state[vid] = {
                    "time": t,
                    "lat": lat,
                    "lon": lon,
                    "speed": speed,
                    "heading": heading
                }


if __name__ == "__main__":
    main()

