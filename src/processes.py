"""
processes.py

High-level operations and workflows that orchestrate the use of functions 
from other modules. Includes the overall process of converting JSON formatted 
data to KML.
"""

"""
Bugs:
-   If user selects "Do you want to use this format for all computed points? (yes/no): no",
    they will not be prompted to choose their format in the future.
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
from utils import (check_polygon_closure, transform_tzt_data_to_kml_format)
from computation import (compute_gps_coordinates_spherical, 
                         compute_gps_coordinates_vincenty, 
                         compute_gps_coordinates_karney, 
                         average_methods)
from file_io import (save_data_to_json, save_kml_to_file, 
                     generate_kml_placemark, generate_complete_kml, 
                     generate_kml_polygon, load_data_from_json)
from io_operations import *
from data_operations import *
from display_operations import *


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


def gather_initial_coordinates():
    coordinate_format = get_coordinate_format_only()
    lat, lon = get_initial_coordinates(coordinate_format)
    if lat is None or lon is None:
        return None, None
    return lat, lon


def determine_point_use():
    return get_point_use_choice()


def gather_monument_data(coordinate_format, lat, lon, use_same_format_for_all):
    if not use_same_format_for_all:
        coordinate_format = get_coordinate_format_only()
    
    bearing, distance = get_bearing_and_distance(coordinate_format)
    if bearing is not None:
        lat, lon = compute_point_based_on_method(1, lat, lon, bearing, distance)
        monument_label = input("Enter a label for the monument (e.g., Monument, Point A, etc.): ")
        results = (lat, lon, monument_label, bearing, distance)
        return coordinate_format, results
    
    return coordinate_format, None


def gather_polygon_points(data, coordinate_format, lat, lon, use_same_format_for_all):
    points = []
    choice = get_computation_method()
    num_points = get_num_points_to_compute()
    
    for _ in range(num_points):
        if not use_same_format_for_all:
            coordinate_format = get_coordinate_format_only()
        bearing, distance = get_bearing_and_distance(coordinate_format)
        if bearing is not None:
            lat, lon = compute_point_based_on_method(choice, lat, lon, bearing, distance)
            data = update_polygon_data(data, lat, lon, bearing, distance)
            points.append((lat, lon))
            display_computed_point(points, lat, lon)
    return data, points


def finalize_data(data, points):
    while True:
        warn_if_polygon_not_closed(points)
        add_point_decision = get_add_point_decision()
        if add_point_decision == 'yes':
            if not use_same_format_for_all:
                coordinate_format = get_coordinate_format_only()
            bearing, distance = get_bearing_and_distance(coordinate_format)
            if bearing is not None:
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


def gather_data_from_user():
    data = initialize_data()
    
    # Gather initial coordinates
    lat, lon = gather_initial_coordinates()
    if lat is None or lon is None:
        return
    data["initial"] = {"lat": lat, "lon": lon}
    
    # Initialize the coordinate_format here
    coordinate_format = get_coordinate_format_only()
    
    # Determine the use of the initial point (monument or start of polygon)
    point_use_choice = determine_point_use()
    
    # Prompt the user if they want to use the same format for all computed points
    use_same_format_for_all = ask_use_same_format_for_all()
    
    if point_use_choice == "1":
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
    elif point_use_choice == "2":
        # For starting point of polygon choice
        display_starting_point(lat, lon)
    
    # Gather the polygon points
    data, points = gather_polygon_points(data, coordinate_format, lat, lon, use_same_format_for_all)
    
    # Finalize the data by potentially adding more points
    data = finalize_data(data, points)
    
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
    
    try:
        save_kml_to_file(kml_content)
        print("KML file saved successfully!")
    except Exception as e:
        print(f"An error occurred while saving the KML file: {e}")


def export_to_data(data):
    try:
        print("Attempting to save data to TZT file...")
        print(data)
        save_data_to_json(data)
        print("Data file saved successfully!")
    except Exception as e:
        print(f"An error occurred while saving the data file: {e}")


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
