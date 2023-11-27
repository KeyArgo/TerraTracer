"""
data_operations.py

Handles the creation, manipulation, and validation of data structures used 
in the main program workflow.
"""
<<<<<<< HEAD
import os
import logging
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from geopy.distance import distance as geopy_distance
from geopy.distance import geodesic

from file_io import export_json_to_kml


logging.basicConfig(level=logging.DEBUG, filename='../logs/application.log', filemode='a', format='%(asctime)s:%(levelname)s:%(message)s')
=======

from geopy.distance import distance as geopy_distance
>>>>>>> parent of 2d50135 (### Added)

from display_operations import display_computed_point
from io_operations import (
    get_add_point_decision,
    get_bearing_and_distance,
    get_coordinate_format_only
)

def initialize_data():
    return {
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


def is_polygon_close_to_being_closed(points, threshold=20):
    for i in range(len(points) - 1):  # Exclude the last point itself
        distance = geopy_distance(points[-1], points[i]).feet
        if distance <= threshold:
            return True
    return False


def check_polygon_closure(points, reference_point=None):
    if len(points) > 2:
        distance_between_first_and_last = geopy_distance(points[0], points[-1]).feet
        
        # Check if the distance is extremely close
        if distance_between_first_and_last < 0.1:
            points[-1] = points[0]
            return True
        
        if reference_point:
            distance_from_reference_to_last = geopy_distance(reference_point[:2], points[-1]).feet
            return distance_between_first_and_last <= 10 or distance_from_reference_to_last <= 10
        else:
            return distance_between_first_and_last <= 10
    return False


def finalize_json_structure(data):
    # Extract the polygon points and convert them to the required format for the checking functions
    points = [(point['lat'], point['lon']) for point in data.get('polygon', [])]

    # Warn the user about the polygon closure status
    warn_if_polygon_not_closed(points, data.get('monument', {}).get('coord'))

    # Rename 'initial' to 'tie_point'
    if 'initial' in data:
        data['tie_point'] = data.pop('initial')
    
    # Assign IDs to the polygon points
    for i, point in enumerate(data.get('polygon', []), start=1):
        point['id'] = f"P{i}"

    # If the polygon is closed, ensure the last point's ID matches the first point's ID
    # and also match the coordinates
    if check_polygon_closure(points):
        first_point_id = data['polygon'][0]['id']
        data['polygon'][-1]['id'] = first_point_id
        data['polygon'][-1]['lat'] = data['polygon'][0]['lat']
        data['polygon'][-1]['lon'] = data['polygon'][0]['lon']

    # Create the construction sequence
    construction_sequence = ['tie_point'] if 'tie_point' in data else []
    
    # Add 'monument' to the construction sequence if it exists and is valid
    monument = data.get('monument', {})
    if monument.get('lat') is not None and monument.get('lon') is not None:
        construction_sequence.append('monument')
    elif 'monument' in data:
        del data['monument']  # Remove the monument key if the monument is not valid

    construction_sequence.extend(point['id'] for point in data.get('polygon', []))
    data['construction_sequence'] = construction_sequence

    return data


def organize_data_for_export(data, sequence):
    """Organize the data into an ordered list for KML recreation based on a given sequence."""
    ordered_data = {'points': [], 'units': data.get('units', 'imperial')}
    construction_sequence = []

    # Add tie_point if it exists
    if 'tie_point' in data:
        ordered_data['tie_point'] = data['tie_point']
    
    # Add monument if it exists
    if 'monument' in data:
        ordered_data['monument'] = data['monument']
    
    # Process the points based on the user-defined sequence
    for item in sequence:
        if item == 'tie_point':
            construction_sequence.append('tie_point')
        elif item == 'monument':
            construction_sequence.append('monument')
        else:
            # Assuming item is a point ID like 'P1', 'P2', etc.
            point_data = next((point for point in data['polygon'] if point['id'] == item), None)
            if point_data:
                ordered_data['points'].append({'id': item, 'data': point_data})
                construction_sequence.append(item)

    ordered_data['construction_sequence'] = construction_sequence
    
    # Return the final structured data
    return ordered_data


def finalize_data(data, points, use_same_format_for_all, coordinate_format, choice):
    from computation import compute_point_based_on_method
    # If there are already points, use the last one as the starting point
    lat, lon = points[-1] if points else (None, None)

    # The loop allows the user to add points until they decide not to add more
    while True:
        # Warn the user if the polygon is not closed
        warn_if_polygon_not_closed(points)

        # Ask the user if they want to add another point
        add_point_decision = get_add_point_decision()

        if add_point_decision == 'yes':
            # If the user wants to add a point, get the format if needed
            if not use_same_format_for_all:
                coordinate_format = get_coordinate_format_only()

            # Get the bearing and distance for the new point
            bearing, distance = get_bearing_and_distance(coordinate_format)
            if bearing is None and distance is None:
                # If the user decides to exit during input, break from the loop
                break

            # Compute the new point
            lat, lon = compute_point_based_on_method(choice, lat, lon, bearing, distance)

            # If the computation was successful, update the polygon data and display the point
            if lat is not None and lon is not None:
                data = update_polygon_data(data, lat, lon, bearing, distance)
                points.append((lat, lon))
                display_computed_point(points, lat, lon)
            else:
                print("An error occurred while computing the point. Please try again.")
                continue  # Skip to the next iteration of the loop
        elif add_point_decision == 'no':
            # If the user does not want to add more points, break from the loop
            break
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")
            continue  # Skip to the next iteration of the loop

    # After the loop, add any other finalization steps if needed
    data['units'] = 'imperial'
    return data


def generate_kml_from_json(json_data):
    """
    Generate KML data from JSON data and save it using export_json_to_kml.

    Args:
        json_data (dict): The JSON data to convert.
    """
    try:
        kml_file_name = input("Enter name for KML file (without extension): ")
        if export_json_to_kml(json_data, kml_file_name):
            print(f"JSON data successfully converted and saved as KML.")
        else:
            print("Failed to generate KML data.")
    except Exception as e:
        print(f"Error generating KML data: {e}")