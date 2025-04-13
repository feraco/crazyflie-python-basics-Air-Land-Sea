import os
import json

LICENSE_IDENTIFIER = "Part of the InnovatED STEM and DroneBlocks Land, Air, and Sea Robotics Curriculum"

directory = "."

for filename in os.listdir(directory):
    if filename.endswith(".ipynb"):
        path = os.path.join(directory, filename)
        with open(path, "r", encoding="utf-8") as f:
            notebook = json.load(f)

        if notebook["cells"] and notebook["cells"][0]["cell_type"] == "markdown":
            first_cell_text = "".join(notebook["cells"][0].get("source", []))
            if LICENSE_IDENTIFIER in first_cell_text:
                notebook["cells"].pop(0)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(notebook, f, indent=1)
                print(f"🗑️  Removed license from: {filename}")
