"""
rename.py - Rename files in a directory to a numbered format. Useful for when adding a bunch of .ani files for the panel

"""


import os
import sys

def rename_files_in_directory(directory, start_number):
    try:
        # Get a sorted list of files in the directory
        files = sorted([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
        
        for index, file in enumerate(files, start=start_number):
            # Get file extension
            file_extension = os.path.splitext(file)[1]
            # Create new file name
            new_name = f"{index}{file_extension}"
            # Get full paths
            old_path = os.path.join(directory, file)
            new_path = os.path.join(directory, new_name)
            # Rename file
            os.rename(old_path, new_path)
            print(f"Renamed: {file} -> {new_name}")

    except FileNotFoundError:
        print(f"The directory '{directory}' was not found.")
    except PermissionError:
        print(f"Permission denied to access '{directory}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <directory> <start_number>")
        sys.exit(1)

    directory_path = sys.argv[1]
    try:
        start_number = int(sys.argv[2])
    except ValueError:
        print("Error: start_number must be an integer.")
        sys.exit(1)

    rename_files_in_directory(directory_path, start_number)
