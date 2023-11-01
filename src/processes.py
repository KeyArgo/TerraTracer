"""
processes.py

High-level operations and workflows that orchestrate the use of functions 
from other modules. Includes the overall process of converting JSON formatted 
data to KML.
"""

"""
Bugs:
-   The JSON file has different coordinates than the KML, they should be the same
-   "Do you want to use this format for all computed points?" should be asked immediately after
    the user selecting the coordinate format.  Currently it is being asked after
    "Do you want the initial point to be:"

Potential Improvements:
-   User should be advised that if they choose DD format and if they pick a direction, 
    if they want true West for instance, they need to select O.  They should probably
    be told they are now turning that direction so they know it adjusts their bearings.
-   Adding functionality to Convert TZT File to KML and rechanging the name to Convert
    JSON to KML.
-   The save function should be more stream lined, also it should probably go into a
    saves directory.
-   There should a new menu that gives the option of a tie point
"""

# Standard library imports
import os
import re

# Third-party library imports
from geopy.distance import distance as geopy_distance
from geopy.point import Point
from geographiclib.geodesic import Geodesic

# Local module imports
from utils import transform_tzt_data_to_kml_format, get_coordinate_in_dd_or_dms
from computation import compute_gps_coordinates_spherical, compute_gps_coordinates_vincenty, compute_gps_coordinates_karney, average_methods
from file_io import save_data_to_json, save_kml_to_file, generate_kml_placemark, generate_complete_kml, generate_kml_polygon, load_data_from_json

# Imports from io_operations
from io_operations import (
    get_coordinate_format_only,
    get_tie_point_coordinate_format,
    ask_use_same_format_for_all,
    get_initial_coordinates,
    get_coordinate_use_choice,
    get_point_use_choice,
    get_computation_method,
    get_num_points_to_compute,
    get_bearing_and_distance,
    get_add_point_decision
)
# Imports from data_operations
from data_operations import initialize_data, update_polygon_data, warn_if_polygon_not_closed, check_polygon_closure

# Imports from display_operations
from display_operations import display_computed_point, display_starting_point, display_monument_point


METHODS_MAP = {
    1: compute_gps_coordinates_karney,
    2: compute_gps_coordinates_vincenty,
    3: compute_gps_coordinates_spherical,
    4: average_methods
}

def compute_point_based_on_method(choice, lat, lon, bearing, distance):
    try:
        method = METHODS_MAP.get(choice)
        if method:
            return method(lat, lon, bearing, distance)
        else:
            print("Invalid method choice.")
            return None, None
    except Exception as e:
        print(f"An error occurred while computing the point: {e}")
        return None, None


def json_to_kml(filepath):
    parsed_data = load_data_from_json(filepath)
    if not parsed_data:
        print("Failed to parse the .json file.")
        return

    transformed_data = transform_tzt_data_to_kml_format(parsed_data)
    kml_content = generate_kml_from_json_data(transformed_data)
    save_kml_to_file(kml_content)

    print("Conversion from .json to .kml completed!")


def gather_tie_point_coordinates():
    """Gather initial coordinates (Tie Point) from the user."""
    coordinate_format = get_tie_point_coordinate_format()
    
    if coordinate_format == "1":  # Checking for "1" instead of "DD"
        lat = get_coordinate_in_dd_or_dms(coordinate_format, "latitude")
        if lat is None:  # User chose to exit
            return None, None
        lon = get_coordinate_in_dd_or_dms(coordinate_format, "longitude")
        if lon is None:  # User chose to exit
            return None, None

    elif coordinate_format == "2":  # Checking for "2" instead of "DMS"
        lat = get_coordinate_in_dd_or_dms(coordinate_format, "latitude")
        if lat is None:  # User chose to exit
            return None, None
        lon = get_coordinate_in_dd_or_dms(coordinate_format, "longitude")
        if lon is None:  # User chose to exit
            return None, None

    elif coordinate_format == "3":  # Checking for "3" instead of "Main Menu"
        return None, None

    else:
        print("Invalid choice. Returning to main menu.")
        return None, None
    
    return lat, lon


def gather_monument_data(coordinate_format, lat, lon, use_same_format_for_all):
    if not use_same_format_for_all:
        coordinate_format = get_coordinate_format_only()
    
    bearing, distance = get_bearing_and_distance(coordinate_format)
    if bearing is None and distance is None:  # User wants to exit
        return coordinate_format, None
    
    lat, lon = compute_point_based_on_method(1, lat, lon, bearing, distance)
    monument_label = input("Enter a label for the monument (e.g., Monument, Point A, etc.): ")
    results = (lat, lon, monument_label, bearing, distance)
    return coordinate_format, results


def gather_polygon_points(data, coordinate_format, lat, lon, use_same_format_for_all):
    points = []
    choice = get_computation_method()
    num_points = get_num_points_to_compute()
    
    for _ in range(num_points):
        if not use_same_format_for_all:
            new_coordinate_format = get_coordinate_format_only()
            if new_coordinate_format:
                coordinate_format = new_coordinate_format

        bearing, distance = get_bearing_and_distance(coordinate_format)
        if bearing is None and distance is None:  # User wants to exit
            break

        lat, lon = compute_point_based_on_method(choice, lat, lon, bearing, distance)
        data = update_polygon_data(data, lat, lon, bearing, distance)
        points.append((lat, lon))
        display_computed_point(points, lat, lon)
    return data, points


def finalize_data(data, points, use_same_format_for_all):
    while True:
        warn_if_polygon_not_closed(points)
        add_point_decision = get_add_point_decision()
        if add_point_decision == 'yes':
            if not use_same_format_for_all:
                coordinate_format = get_coordinate_format_only()
            bearing, distance = get_bearing_and_distance(coordinate_format)
            if bearing is None and distance is None:  # User wants to exit
                break
            lat, lon = compute_point_based_on_method(choice, lat, lon, bearing, distance)
            data = update_polygon_data(data, lat, lon, bearing, distance)
            points.append((lat, lon))
            display_computed_point(points, lat, lon)
        elif add_point_decision == 'no':
            break
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")
    data['units'] = 'imperial'
    return data


def polygon_main_menu():
    print("\nChoose an option:")
    print("1) Use a Tie Point")
    print("2) Specify the placement of the first point in the polygon")
    print("3) Exit to Main Menu")
    return input("Enter your choice (1/2/3): ")


def tie_point_menu():
    print("\nChoose an option:")
    print("1) Use initial point as Monument/Placemark")
    print("2) Find and place the first point of the polygon")
    print("3) Exit to Main Menu")
    choice = input("Enter your choice (1/2/3): ").strip()
    while choice not in ["1", "2", "3"]:
        print("Invalid choice. Please select 1, 2 or 3.")
        choice = input("Enter your choice (1/2/3): ").strip()
    return choice


def gather_data_from_user():
    data = initialize_data()
    
    # Display the Polygon Main Menu
    main_choice = polygon_main_menu()

    if main_choice == "1":  # Using a Tie Point
        # Gather initial coordinates (Tie Point Location)
        lat, lon = gather_tie_point_coordinates()
        
        # Check if lat and lon are None (indicating a return to the Main Menu)
        if lat is None and lon is None:
            # Handle return to Main Menu or exit the function.
            return
        data["initial"] = {"lat": lat, "lon": lon}
        
        # Initialize the coordinate_format here
        coordinate_format = get_coordinate_format_only()

        # Prompt the user if they want to use the same format for all computed points
        use_same_format_for_all = ask_use_same_format_for_all()

        # Display the Tie Point Menu
        point_use_choice = tie_point_menu()

        if point_use_choice == "1":  # Monument/Placemark choice
            # For monument choice
            coordinate_format, results = gather_monument_data(coordinate_format, lat, lon, use_same_format_for_all)
            if results:
                lat, lon, monument_label, bearing, distance = results
                data["monument"] = {
                    "lat": lat,
                    "lon": lon,
                    "label": monument_label,
                    "bearing_from_prev": bearing,
                    "distance_from_prev": distance
                }
                display_monument_point(lat, lon)
            else:
                print("Monument data could not be gathered. Please try again.")
                return  # Exit the function if no monument data is gathered

        elif point_use_choice == "2":  # Starting point of polygon choice
            display_starting_point(lat, lon)

    elif main_choice == "2":  # Directly specify the placement of the first point
        lat, lon = gather_tie_point_coordinates()
        if lat is None or lon is None:
            return
        data["initial"] = {"lat": lat, "lon": lon}

        # Initialize the coordinate_format here
        coordinate_format = get_coordinate_format_only()

        # Prompt the user if they want to use the same format for all computed points
        use_same_format_for_all = ask_use_same_format_for_all()

    elif main_choice == "3":  # Exit to Main Menu
        return None

    else:
        return None
    
    # If we reach this point, we're ready to gather the polygon points
    data, points = gather_polygon_points(data, coordinate_format, lat, lon, use_same_format_for_all)
    
    # Finalize the data by potentially adding more points
    data = finalize_data(data, points, use_same_format_for_all)
    
    return data


def export_to_kml(data, points):
    if points[0] != points[-1]:
        points_closed = points + [points[0]]
    else:
        points_closed = points

    kml_polygon = generate_kml_polygon(points_closed, color="#3300FF00")
    if data.get("monument", {}).get("lat") and data.get("monument", {}).get("lon"):  # check if there's a monument with valid coordinates
        kml_placemark = generate_kml_placemark(data["monument"]["lat"], 
                                               data["monument"]["lon"], 
                                               name=data["monument"]["label"])
        # Combine the placemark and the polygon for the KML
        kml_content = generate_complete_kml(kml_placemark, kml_polygon)
    else:
        kml_content = generate_complete_kml(polygon_kml=kml_polygon)
    
    default_directory = os.getcwd()
    default_filename = "output.kml"
    directory = input(f"Enter the directory to save the KML file (default is {default_directory}): ") or default_directory
    filename = input(f"Enter the filename for the KML file (default is {default_filename}): ") or default_filename
    if not filename.endswith(".kml"):
        filename += ".kml"
    full_path = os.path.join(directory, filename)

    save_kml_to_file(kml_content, full_path)


def export_to_data(data):
    default_directory = os.getcwd()
    default_filename = "output.json"
    directory = input(f"Enter the directory to save the Data file (default is {default_directory}): ") or default_directory
    filename = input(f"Enter the filename for the Data file (default is {default_filename}): ") or default_filename
    if not filename.endswith(".json"):
        filename += ".json"
    full_path = os.path.join(directory, filename)

    save_data_to_json(data, full_path)


def create_kml_process():
    data = gather_data_from_user()  # Get the data using the function

    # Check if data was returned and has the expected keys
    if not data or 'polygon' not in data:
        print("Data gathering was not completed. Exiting.")
        return
    
    # This is your primary list of points from which both KML and TZT should be generated.
    points = [(point['lat'], point['lon']) for point in data['polygon']]
    print("Polygon Points:", points)

    # Check one last time if the polygon is closed
    if not check_polygon_closure(points, (data["monument"]["lat"], data["monument"]["lon"]) if "lat" in data["monument"] else None):
        print("Warning: Your polygon is not closed.")

    # Prompt user if they want to export the data                                                
    export_choice = input("Do you want to export the polygon to a KML file or Data File? (yes/no): ")
    if export_choice.lower() == 'yes':
        file_type_choice = input("Would you like to save a (K)ML, (D)ata File or (B)oth? ").upper()
        
        if file_type_choice in ["K", "B"]:
            export_to_kml(data, points)
        if file_type_choice in ["D", "B"]:
            export_to_data(data)

    return data  # returning data for inspection purposes
