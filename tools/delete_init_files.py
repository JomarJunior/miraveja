"""
This script deletes __init__.py files for a specified directory and its subdirectories.
"""

import os
def delete_init_files(package_dir):
    for root, dirs, files in os.walk(package_dir):
        for filename in files:
            if filename == "__init__.py":
                file_path = os.path.join(root, filename)
                os.remove(file_path)
                print(f"Deleted: {file_path}")

from sys import argv

if __name__ == "__main__":
    if len(argv) != 2:
        print("Usage: python delete_init_files.py <package_directory>")
        exit(1)

    package_dir = argv[1]
    delete_init_files(package_dir)
