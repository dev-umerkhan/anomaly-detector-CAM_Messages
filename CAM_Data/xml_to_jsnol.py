import xml.etree.ElementTree as ET
import json
import argparse
from pathlib import Path


def xml_to_dict(element):
    """Recursively convert XML to dictionary."""
    data = {}

    # Add attributes
    if element.attrib:
        data["@attributes"] = element.attrib

    # Add child elements
    children = list(element)
    if children:
        child_dict = {}
        for child in children:
            child_data = xml_to_dict(child)
            tag = child.tag

            if tag not in child_dict:
                child_dict[tag] = []
            child_dict[tag].append(child_data)

        for key in child_dict:
            if len(child_dict[key]) == 1:
                child_dict[key] = child_dict[key][0]

        data.update(child_dict)

    # Add text if present
    text = element.text.strip() if element.text else ""
    if text:
        data["#text"] = text

    return data


def main():
    parser = argparse.ArgumentParser(description="Convert XML file to JSON")
    parser.add_argument("--infile", required=True, help="Input XML file")
    parser.add_argument("--outfile", required=True, help="Output JSON file")
    args = parser.parse_args()

    infile = Path(args.infile).resolve()
    outfile = Path(args.outfile).resolve()

    if not infile.exists():
        raise FileNotFoundError(f"Input file not found: {infile}")

    tree = ET.parse(infile)
    root = tree.getroot()

    data = {root.tag: xml_to_dict(root)}

    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"✅ Conversion complete:\n{outfile}")


if __name__ == "__main__":
    main()
