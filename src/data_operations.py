"""
data_operations.py

Handles the creation, manipulation, and validation of data structures used 
in the main program workflow.
"""
import os
import math
import logging
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from geopy.distance import distance as geopy_distance
from geopy.distance import geodesic
from geographiclib.geodesic import Geodesic
from file_io import export_json_to_kml


logging.basicConfig(level=logging.DEBUG, filename='../logs/application.log', filemode='a', format='%(asctime)s:%(levelname)s:%(message)s')



def initialize_data():
    """
    Initializes the data structure for the application.

    This function sets up a dictionary with keys for 'polygon', 'construction_sequence', 
    and 'monument', each initialized to their default values. The 'polygon' key stores 
    the points of a polygon, 'construction_sequence' tracks the order of point additions, 
    and 'monument' holds details about any specific monuments.

    Returns:
        dict: A dictionary with structured keys for storing polygon and monument data.
    """
    return {
        'polygon': [],  # List to store points forming a polygon
        'construction_sequence': [],  # Tracks the order of construction steps
        'monument': {
            'label': None,  # Identifier or name of the monument
            'lat': None,    # Latitude of the monument
            'lon': None,    # Longitude of the monument
            'bearing_from_prev': None,  # Bearing from the previous point
            'distance_from_prev': None  # Distance from the previous point
        }
    }


def update_polygon_data(data, lat, lon, bearing, distance):
    """
    Updates the data dictionary with the computed point's details and updates the construction sequence.

    This function appends a new point, defined by its latitude (lat), longitude (lon), 
    bearing (in degrees), and distance (in meters), to the 'polygon' key of the data 
    dictionary. It also updates the 'construction_sequence' to reflect the addition 
    of this new point.

    Args:
    - data (dict): The data dictionary to be updated.
    - lat (float): Latitude of the new point.
    - lon (float): Longitude of the new point.
    - bearing (float): Bearing from the previous point to the new point in degrees.
    - distance (float): Distance from the previous point to the new point in meters.

    Modifies the 'data' dictionary in place, adding new point details and updating the construction sequence.
    """
    # Debugging: Log the state of construction_sequence before update
    logging.debug(f"Before update - construction_sequence: {data['construction_sequence']}")

    # Validate the input data types (note: assertions are used here for debugging purposes
    # and should be supplemented with robust error handling in production code)
    assert isinstance(data, dict), "Debug: Data should be a dictionary"
    assert isinstance(lat, float) and isinstance(lon, float), "Latitude and Longitude should be floats"

    # Creating a new data point
    data_point = {
        "lat": lat, "lon": lon,
        "bearing_from_prev": bearing, 
        "distance_from_prev": distance
    }

    # Appending the new point to the polygon data
    data["polygon"].append(data_point)
    
    # Generating a unique ID for the new point and updating the construction sequence
    point_id = f"P{len(data['polygon']) + 1}"  # Assuming sequential IDs (P1, P2, ...)
    data['construction_sequence'].append(point_id)

    # Debugging: Log the state of construction_sequence after update
    logging.debug(f"After update - construction_sequence: {data['construction_sequence']}")
    return data


def warn_if_polygon_not_closed(data):
    """
    Warns the user if the polygon is not closed and updates the construction sequence.
    The function checks if the first and last points of the polygon are within a specified 
    proximity threshold (0.05 km) to determine closure. It logs and prints appropriate 
    messages based on the closure status and the redundancy of the last point.

    Args:
    - data (dict): Data structure containing the polygon points and construction sequence.

    Returns:
    - bool: True if the polygon is closed (within the proximity threshold), False otherwise.
    """
    points = data['polygon']
    logging.debug(f"Points before closure check: {points}")

    message = f"Points list before closure check: {points}"
    logging.debug(message)
    print(message)  # Print to console

    # Check if the polygon is closed
    polygon_closed = check_polygon_closure(data)

    # Spatial check for the proximity of the last point to the first point
    first_point = (points[0]['lat'], points[0]['lon'])
    last_point = (points[-1]['lat'], points[-1]['lon'])
    proximity_threshold = 0.05  # Adjusted threshold in kilometers
    is_last_point_redundant = geodesic(first_point, last_point).kilometers < proximity_threshold

    # Handling based on polygon closure and redundancy of the last point
    if polygon_closed and is_last_point_redundant:
        data['construction_sequence'] = [point['id'] for point in data['polygon'][:-1]]
        message = "Your polygon is completed and closed. Redundant last point excluded."
    elif polygon_closed:
        data['construction_sequence'] = [point['id'] for point in data['polygon']]
        message = "Your polygon is completed."
    else:
        data['construction_sequence'] = [point['id'] for point in data['polygon']]
        message = "Your polygon is not closed."

    logging.info(message)
    print(message)  # Print to console

    return polygon_closed


def is_polygon_close_to_being_closed(points, tolerance_feet=1):
    """
    Check if the polygon is close to being closed.
    
    Args:
    points (list): List of points as (lat, lon) tuples.
    tolerance_feet (float): Maximum allowed distance between first and last points in feet.
    
    Returns:
    bool: True if the polygon is close to being closed, False otherwise.
    """
    if len(points) < 3:
        return False
    
    start_point = points[0]
    end_point = points[-1]
    
    # Calculate distance between first and last point
    distance = geopy_distance(start_point, end_point).feet
    
    logging.debug(f"Distance between first and last point: {distance} feet")
    
    return distance <= tolerance_feet


def check_polygon_closure(data, reference_point=None):
    """
    Checks if the polygon formed by a sequence of points is closed. The polygon is considered closed if 
    the distance between the first and last points is less than 0.1 feet. The function handles points 
    in either dictionary or tuple format and logs an error for invalid formats.

    If a reference point is provided, the polygon is also considered closed if the last point is within 
    10 feet of the reference point.

    Args:
    - data (dict): Data structure containing the polygon points.
    - reference_point (tuple, optional): An optional reference point (latitude, longitude) used in the closure check.

    Returns:
    - bool: True if the polygon is closed, False otherwise or if there are insufficient points to form a polygon.
    """
    # Extract points list from data
    points = data['polygon']

    # Debugging: Log the state of construction_sequence before check
    logging.debug(f"Before check - construction_sequence: {data['construction_sequence']}")

    if len(points) > 2:
        for idx, point in enumerate(points):
            # Ensure that point is in the correct format (latitude, longitude)
            if isinstance(point, dict):
                lat_lon = (point['lat'], point['lon'])  # Extract lat and lon
            elif isinstance(point, tuple) and len(point) == 2:
                lat_lon = point
            else:
                logging.error(f"Invalid point format at index {idx}: {point}")
                return False

            # If it's the first point, set it as the starting point
            if idx == 0:
                start_lat_lon = lat_lon
                continue

            # Check the distance between the current point and the start point
            distance = geopy_distance(start_lat_lon, lat_lon).feet
            logging.debug(f"Distance between points: {distance} feet")

        # Check distance between last point and the first point
        last_lat_lon = (points[-1]['lat'], points[-1]['lon']) if isinstance(points[-1], dict) else points[-1]
        distance_between_first_and_last = geopy_distance(start_lat_lon, last_lat_lon).feet
        logging.debug(f"Distance between first and last point: {distance_between_first_and_last} feet")

        is_closed = distance_between_first_and_last < 0.1
        if reference_point:
            distance_from_reference_to_last = geopy_distance(reference_point, last_lat_lon).feet
            is_closed |= distance_from_reference_to_last <= 10

    else:
        logging.warning("Not enough points to form a polygon.")
        return False

    # Log the state of construction_sequence after check
    logging.debug(f"After check - construction_sequence: {data['construction_sequence']}")
    
    return is_closed


def finalize_json_structure(data, tie_point_used, polygon_name):
    """
    Finalizes the JSON structure of the data, focusing on the handling of the construction sequence 
    and special elements like tie points and monuments. It updates the polygon name, checks if the 
    polygon is closed, and adjusts the construction sequence accordingly. The function also inserts 
    tie points and monument information into the construction sequence when applicable.

    Args:
    - data (dict): Data structure containing polygon and related information.
    - tie_point_used (bool): Indicates if a tie point was used in the polygon construction.
    - polygon_name (str): The name of the polygon.

    Modifies the 'data' dictionary, updating the construction sequence and handling special cases 
    for tie points and monuments.
    """
    data['polygon_name'] = polygon_name

    # Check if polygon is closed and warn about polygon closure status
    polygon_closed = warn_if_polygon_not_closed(data)

    # Handle construction_sequence based on polygon closure
    if polygon_closed:
        # Ensure construction_sequence starts and ends with the same point if closed
        if data['construction_sequence'][0] != data['construction_sequence'][-1]:
            data['construction_sequence'].append(data['construction_sequence'][0])
    else:
        # If polygon is not closed, make sure construction_sequence does not repeat the first point at the end
        if len(data['construction_sequence']) != len(data['polygon']):
            data['construction_sequence'] = [point['id'] for point in data['polygon']]

    # Handle tie_point in construction_sequence
    if tie_point_used and 'tie_point' not in data['construction_sequence']:
        data['construction_sequence'].insert(0, 'tie_point')

    # Handle monument in construction_sequence
    monument = data.get('monument', {})
    if monument.get('lat') is not None and monument.get('lon') is not None:
        if 'monument' not in data['construction_sequence']:
            data['construction_sequence'].insert(1, 'monument')

    # Remove invalid keys if necessary
    if not tie_point_used and 'tie_point' in data:
        del data['tie_point']
    if 'monument' in data and monument.get('lat') is None:
        del data['monument']

    return data


def finalize_data(data, use_same_format_for_all, coordinate_format, choice):
    points = [(point['lat'], point['lon']) for point in data['polygon']]
    if is_polygon_close_to_being_closed(points):
        logging.info("The polygon is close enough to being closed. Adjusting the last point to the initial point.")
        first_point = data['polygon'][0]
        last_point = data['polygon'][-1]
        
        # Use the user-entered values for the last segment
        closing_point = {
            "id": "P1",
            "bearing": last_point['bearing'],
            "distance_feet": last_point['distance_feet'],
            "lat": first_point['lat'],
            "lon": first_point['lon']
        }
        data['polygon'][-1] = closing_point
        
        # Update construction_sequence if it exists and has elements
        if 'construction_sequence' in data and data['construction_sequence']:
            data['construction_sequence'][-1] = 'P1'
        elif 'construction_sequence' in data:
            # If construction_sequence exists but is empty, initialize it
            data['construction_sequence'] = ['P1' for _ in range(len(data['polygon']))]
        else:
            # If construction_sequence doesn't exist, create it
            data['construction_sequence'] = ['P1' for _ in range(len(data['polygon']))]
    
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