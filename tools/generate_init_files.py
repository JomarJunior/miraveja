"""
This script generates __init__.py files for all packages in the project.
"""

import os

def generate_init_files(package_dir):
    # Traverse the package directory
    for root, dirs, files in os.walk(package_dir):
        if "__init__.py" not in files:
            with open(os.path.join(root, "__init__.py"), "w") as f:
                f.write("# Init file for package\n")


# Generate init files for the directory passed by the CLI parameter
from sys import argv

if __name__ == "__main__":
    if len(argv) > 1:
        package_dir = argv[1]
        generate_init_files(package_dir)
    else:
        print("Please provide a package directory.")
