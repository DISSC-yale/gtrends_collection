"""Builds metadata."""

import json
import re

import requests

if __name__ == "__main__":
    # retrieve locations (US states + metro areas)
    req = requests.get("https://trends.google.com/trends/api/explore/pickers/geo", timeout=999)
    if req.status_code == 200:
        geos = json.loads(re.sub("^[^{]+", "", req.content.decode()))
        locations = []
        for child in geos["children"]:
            if child["id"] == "US":
                for state in child["children"]:
                    state_id = state["id"]
                    locations.append(f"US-{state_id}")
                    if "children" in state:
                        for area in state["children"]:
                            locations.append(f"US-{state_id}-{area["id"]}")
                break
        with open("scope/locations.txt", "w", encoding="utf-8") as file:
            file.write("\n".join(locations))
