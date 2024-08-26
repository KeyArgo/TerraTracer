"""
main_program.py

Entry point to the program. It calls the necessary functions from processes.py 
to execute the main workflow.
"""

import os
from pathlib import Path

# Local module imports
from processes import create_kml_process
from data_operations import generate_kml_from_json
#from placemark_operations import create_placemarks_process 
from file_io import import_json_data, save_kml_to_file


def main():
    """
    Main function that provides a menu for the user to interact with the program.

    The menu offers options to create custom geometric polygons, define individual placemarks,
    and convert JSON files to KML for visualization. The user's choice is taken as input, and
    the corresponding process is initiated.

    The function loops until the user chooses to exit ('X').
    """
    while True:
        print("\n#########################")
        print("###    TerraTracer    ###")
        print("#########################")
        
        print("\n1. Create Custom Geometric Polygons")
        print("   - Create mining claims based on land certificates.")
        print("   - Delineate property boundaries, agricultural fields, etc.")
        print("   - Create artful shapes: stars, triangles, hexagons, intricate patterns, and more.")
        print("   - Designate specific zones or areas for urban planning or environmental conservation.")
        
        print("\n2. Create Placemarks (COMING SOON)")
        print("   - Define individual placemarks based on coordinate inputs.")
        
        print("\n3. Convert JSON File to KML")
        print("   - Convert a previously saved JSON data file into a KML format for visualization in tools like Google Earth.")
        
        print("\nX. Exit")
        print("   - Terminate the program.")
        
        choice = input("\n\nEnter your choice (1/2/3/X): ")
        
        if choice == "1":
            # Call the function to create a new polygon
            create_polygon_process()
        elif choice == "2":
            create_placemarks_process()
        elif choice == "3":
            base_dir = Path(__file__).resolve().parent.parent / 'saves'
            default_json_directory = base_dir / 'json'
            json_path = choose_file_path(default_json_directory)
            data = import_json_data(json_path)

            if data:
                generate_kml_from_json(data)
            else:
                print("Failed to import JSON.")
        elif choice.upper() == "X":
            print("\nExiting program. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please select a valid option.")

def create_polygon_process():
    """
    Function to run the create polygon process. It guides the user through a series of prompts
    to input initial coordinates, choose computation methods, and compute subsequent GPS points
    to form a polygon. The results can be exported to KML or data files.

    Returns:
    - dict: A dictionary containing initial coordinates, monument details (if any), and polygon points.
    """
    polygon_name = input("Enter name of polygon: ")
    return create_kml_process(polygon_name)


def create_placemark_process():
    """
    Function to run the create placemark process. It prompts the user to input coordinates,
    and based on these inputs, individual placemarks are defined and processed.

    Returns:
    - None: The process updates the placemark data directly without returning any value.
    """
    return create_placemarks_process()


from pathlib import Path
import os

def choose_file_path(default_directory):
    """
    Allows the user to choose a file path within a given directory or navigate to a different directory.

    Args:
        default_directory (Path): The default directory path.

    Returns:
        str: The chosen file path.
    """
    # Ensure we're using the correct saves directory
    base_dir = Path(__file__).resolve().parent.parent / 'saves'
    current_directory = base_dir / 'json'
    
    while True:
        print(f"\nCurrent directory: {current_directory}")
        print("Files and directories:")
        try:
            for item in os.listdir(current_directory):
                print(f" - {item}")
        except FileNotFoundError:
            print(f"Directory not found: {current_directory}")
            current_directory = base_dir / 'json'
            continue

        choice = input("\nEnter file name to select, 'up' to go up a directory, or 'new' to enter a new path: ")
        
        if choice.lower() == 'up':
            current_directory = current_directory.parent
        elif choice.lower() == 'new':
            new_path = input("Enter new directory path: ")
            # Construct a new path relative to the current directory
            new_directory = Path(new_path)
            if not new_directory.is_absolute():
                new_directory = current_directory / new_directory
            new_directory = new_directory.resolve()  # Resolve to full path
            if new_directory.exists() and new_directory.is_dir():
                current_directory = new_directory
            else:
                print("Invalid directory. Please try again.")
        else:
            potential_file = current_directory / choice
            if potential_file.exists() and potential_file.is_file():
                return str(potential_file.resolve())  # Resolve to full path
            else:
                print("Invalid selection. Please try again.")


if __name__ == "__main__":
    main()
