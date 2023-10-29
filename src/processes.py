"""
processes.py

High-level operations and workflows that orchestrate the use of functions from other modules. Includes:
- The overall process of converting TZT formatted data to KML.
"""

# Standard library imports
import os
import re

# Third-party library imports
from geopy.distance import distance as geopy_distance
from geopy.point import Point
from geographiclib.geodesic import Geodesic

# Local module imports
from utils import (get_coordinate_in_dd_or_dms, 
                   parse_dd_or_dms, is_polygon_close_to_being_closed, 
                   check_polygon_closure, transform_tzt_data_to_kml_format)

from computation import (compute_gps_coordinates_spherical, 
                         compute_gps_coordinates_vincenty, 
                         compute_gps_coordinates_karney, 
                         average_methods)

from file_io import (save_data_to_file, save_kml_to_file, 
                     generate_kml_placemark, generate_complete_kml, 
                     generate_kml_polygon, parse_tzt_file, order_points)


def get_coordinate_format():
    """
    Prompt the user to choose between DD and DMS format for coordinates input.
    Returns:
    - str: User's choice of coordinate format (either "1" or "2").
    """
    while True:
        coordinate_format = input("Enter coordinates format (1 for DD, 2 for DMS): ")
        if coordinate_format not in ["1", "2"]:
            print("Invalid choice. Please select 1 for DD or 2 for DMS.")
            continue
        return coordinate_format


def get_initial_coordinates(coordinate_format):
    """
    Get initial coordinates from the user based on the chosen format.
    Args:
    - coordinate_format (str): User's choice of coordinate format (either "1" or "2").
    Returns:
    - tuple: Initial latitude and longitude.
    """
    initial_lat = get_coordinate_in_dd_or_dms(coordinate_format, "latitude")
    initial_lon = get_coordinate_in_dd_or_dms(coordinate_format, "longitude")
    return initial_lat, initial_lon


def get_coordinate_use_choice():
    """
    Ask user how they'd like to use the initial coordinates.
    Returns:
    - str: User's choice on how to use the initial coordinates.
    """
    print("\nHow would you like to use the initial coordinates?")
    print("1) As a starting location (won't be included in the polygon).")
    print("2) As Point 1 of the polygon.")
    return input("Enter choice (1/2): ")


def get_point_use_choice():
    """
    Ask user how they'd like to use the initial point.
    Returns:
    - str: User's choice on how to use the initial point.
    """
    print("\nDo you want the initial point to be:")
    print("1) A Monument (will become a placemark).")
    print("2) First Point of the Polygon (no placemark).")
    return input("Enter choice (1/2): ")


def get_computation_method():
    """
    Prompt user to select the computation method for determining subsequent GPS coordinates.
    Returns:
    - int: User's choice of computation method.
    """
    while True:
        try:
            print("Choose a method:")
            print("1) Karney's Method")
            print("2) Vincenty's Method")
            print("3) Spherical Model")
            print("4) Average all models/methods")
            choice = int(input("Enter choice (1/2/3/4): "))
            if choice not in [1, 2, 3, 4]:
                raise ValueError("Invalid choice. Please select 1, 2, 3, or 4.")
            return choice
        except ValueError as e:
            print(e)


def get_num_points_to_compute():
    """
    Get the number of points user wants to compute.
    Returns:
    - int: Number of points the user wants to compute.
    """
    while True:
        try:
            num_points = int(input("How many points would you like to compute? "))
            return num_points
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def get_bearing_and_distance():
    """
    Prompt the user for bearing and distance.
    Returns:
    - tuple: Bearing and distance provided by the user.
    """
    while True:
        try:
            bearing = parse_dd_or_dms()
            if bearing is None:
                raise ValueError("Invalid input for bearing.")
            
            distance = float(input("Enter distance in feet: ").replace(',', ''))
            return bearing, distance
        except ValueError:
            print("Invalid input. Please enter valid values for bearing and distance.")
            continue


def get_add_point_decision():
    """
    Ask user if they want to add more points.
    Returns:
    - str: User's decision on whether to add more points.
    """
    return input("Would you like to enter another point before closing the polygon? (yes/no): ").strip().lower()


def compute_point_based_on_method(choice, lat, lon, bearing, distance):
    """
    Computes a new GPS point based on the chosen method.
    Args:
    - choice (int): User's choice of computation method.
    - lat (float): Current latitude.
    - lon (float): Current longitude.
    - bearing (float): Bearing to compute the new point.
    - distance (float): Distance to compute the new point.
    Returns:
    - tuple: Computed latitude and longitude.
    """
    try:
        if choice == 1:
            return compute_gps_coordinates_karney(lat, lon, bearing, distance)
        elif choice == 2:
            return compute_gps_coordinates_vincenty(lat, lon, bearing, distance)
        elif choice == 3:
            return compute_gps_coordinates_spherical(lat, lon, bearing, distance)
        elif choice == 4:
            return average_methods(lat, lon, bearing, distance)
        else:
            print("Invalid method choice.")
            return None, None
    except Exception as e:
        print(f"An error occurred while computing the point: {e}")
        return None, None


def update_polygon_data(data, lat, lon, bearing, distance):
    """
    Updates the data dictionary with the computed point's details.
    Args:
    - data (dict): Data dictionary to be updated.
    - lat (float): Computed latitude.
    - lon (float): Computed longitude.
    - bearing (float): Bearing used to compute the point.
    - distance (float): Distance used to compute the point.
    Returns:
    - dict: Updated data dictionary.
    """
    data_point = {
        "lat": lat, "lon": lon,
        "bearing_from_prev": bearing, 
        "distance_from_prev": distance
    }
    data["polygon"].append(data_point)
    return data


def display_computed_point(points, lat, lon):
    """
    Displays the computed point to the user.
    Args:
    - points (list): List of points already computed.
    - lat (float): Latitude of the computed point.
    - lon (float): Longitude of the computed point.
    """
    print(f"Computed Point {len(points)}: Latitude: {lat:.6f}, Longitude: {lon:.6f}\n")


def warn_if_polygon_not_closed(points, monument_coord=None):
    """
    Warns the user if the polygon is not closed.
    Args:
    - points (list): List of points in the polygon.
    - monument_coord (tuple, optional): Latitude and longitude of the monument. Defaults to None.
    """
    if check_polygon_closure(points, monument_coord):
        print("Your polygon is completed.")
    elif is_polygon_close_to_being_closed(points):
        print("Warning: Your polygon is not closed.")
        print("Your polygon is close enough to being closed.")
    else:
        print("Warning: Your polygon is not closed.")


def display_starting_point(lat, lon):
    """
    Displays the starting point to the user.
    Args:
    - lat (float): Latitude of the starting point.
    - lon (float): Longitude of the starting point.
    """
    print(f"Starting Point: Latitude: {lat:.6f}, Longitude: {lon:.6f}\n")


def display_monument_point(lat, lon):
    """
    Displays the monument point to the user.
    Args:
    - lat (float): Latitude of the monument point.
    - lon (float): Longitude of the monument point.
    """
    print(f"Monument: Latitude: {lat:.6f}, Longitude: {lon:.6f}\n")


def tzt_to_kml(filepath):
    parsed_data = parse_tzt_file(filepath)
    if not parsed_data:
        print("Failed to parse the .tzt file.")
        return

    transformed_data = transform_tzt_data_to_kml_format(parsed_data)
    kml_content = generate_kml_from_tzt_data(transformed_data)
    save_kml_to_file(kml_content)

    print("Conversion from .tzt to .kml completed!")


def gather_data_from_user():
    """
    Function prompts the user to input initial coordinates, choose computation methods,
    compute a discovery point (monument) if chosen, and then compute subsequent GPS points for a polygon.
    
    Returns:
    - dict: A dictionary containing initial coordinates, monument details (if chosen), and polygon points.
    """
    # Initializing latitude and longitude
    initial_lat = None
    initial_lon = None

    # Dictionary to store initial coordinates, monument details, and polygon points
    data = {
        'initial': {
            'lat': None,
            'lon': None
        },
        'polygon': [],
        'monument': {
            'label': None,
            'lat': None,
            'lon': None,
            'bearing_from_prev': None,
            'distance_from_prev': None
        }
    }

    # Prompt user for input details
    coordinate_format = get_coordinate_format()
    initial_lat, initial_lon = get_initial_coordinates(coordinate_format)
    lat, lon = initial_lat, initial_lon

    # Check if valid coordinates were provided
    if lat is None or lon is None:
        return
    
    # Save initial coordinates to the data dictionary
    data["initial"] = {"lat": lat, "lon": lon}

    point_use_choice = get_point_use_choice()
    points = []

    if point_use_choice == "1":
        # Compute discovery point (monument) relative to the initial point
        bearing, distance = get_bearing_and_distance()
        if bearing is not None:
            lat, lon = compute_point_based_on_method(1, lat, lon, bearing, distance)
            monument_label = input("Enter a label for the monument (e.g., Monument, Point A, etc.): ")

            # Store the bearing and distance directly from user input
            data["monument"] = {
                "lat": lat,
                "lon": lon,
                "label": monument_label,
                "bearing_from_prev": bearing,
                "distance_from_prev": distance
            }
        display_monument_point(lat, lon)

    elif point_use_choice == "2":
        display_starting_point(lat, lon)

    choice = get_computation_method()
    num_points = get_num_points_to_compute()

    for _ in range(num_points):
        bearing, distance = get_bearing_and_distance()
        if bearing is not None:
            lat, lon = compute_point_based_on_method(choice, lat, lon, bearing, distance)
            data = update_polygon_data(data, lat, lon, bearing, distance)
            points.append((lat, lon))
            display_computed_point(points, lat, lon)

    while True:
        warn_if_polygon_not_closed(points)
        
        add_point_decision = get_add_point_decision()
        if add_point_decision == 'yes':
            bearing, distance = get_bearing_and_distance()
            if bearing is not None:
                lat, lon = compute_point_based_on_method(choice, lat, lon, bearing, distance)
                data = update_polygon_data(data, lat, lon, bearing, distance)
                points.append((lat, lon))
                display_computed_point(points, lat, lon)
        elif add_point_decision == 'no':
            break
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")

    return data


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
            # For KML, we might need to close the polygon. So, work on a copy of the list.
            if points[0] != points[-1]:
                points_closed = points + [points[0]]
            else:
                points_closed = points
            kml_polygon = generate_kml_polygon(points_closed, color="#3300FF00")
            
            # Add a placemark if a monument exists
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

        if file_type_choice in ["D", "B"]:
            try:
                print("Attempting to save data to TZT file...")
                print(data)
                # For the TZT file, use the original list of points.
                save_data_to_file(data)
                print("Data file saved successfully!")
            except Exception as e:
                print(f"An error occurred while saving the data file: {e}")

    return data  # returning data for inspection purposes
