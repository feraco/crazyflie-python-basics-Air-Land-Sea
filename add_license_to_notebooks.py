import os
import json

license_cell = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "<small>\n",
        "Part of the InnovatED STEM and DroneBlocks Land, Air, and Sea Robotics Curriculum  \n",
        "Licensed for educational use in schools only.  \n",
        "Redistribution, commercial use, or resale is strictly prohibited.  \n",
        "© 2025 InnovatED STEM & DroneBlocks. All rights reserved.\n",
        "</small>"
    ]
}

directory = "."

for filename in os.listdir(directory):
    if filename.endswith(".ipynb"):
        path = os.path.join(directory, filename)
        with open(path, "r", encoding="utf-8") as f:
            notebook = json.load(f)

        # Check if license is already there
        if notebook["cells"] and "DroneBlocks" in "".join(notebook["cells"][0].get("source", [])):
            print(f"✅ Already contains license: {filename}")
            continue

        notebook["cells"].insert(0, license_cell)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(notebook, f, indent=1)

        print(f"✅ License added to: {filename}")
