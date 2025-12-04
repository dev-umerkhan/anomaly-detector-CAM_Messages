from sumolib import net
import xml.etree.ElementTree as ET
import json

net = net.readNet("deggendorf.net.xml")

output = open("cam_data.jsonl", "w")   # JSON Lines format (one JSON per line)

# Stream parse the XML
for event, elem in ET.iterparse("vehicle_positions.xml", events=("start", "end")):
    if event == "end" and elem.tag == "vehicle":
        x = float(elem.attrib["x"])
        y = float(elem.attrib["y"])
        lat, lon = net.convertXY2LonLat(x, y)
        speed = float(elem.attrib["speed"])
        heading = float(elem.attrib["angle"])

        timestep = elem.getparent().attrib["time"] if hasattr(elem, "getparent") else None

        cam = {
            "time": timestep,
            "id": elem.attrib["id"],
            "lat": lat,
            "lon": lon,
            "speed": speed,
            "heading": heading
        }

        output.write(json.dumps(cam) + "\n")

        elem.clear()    # FREE MEMORY

output.close()
print("Finished streaming CAM extraction.")

