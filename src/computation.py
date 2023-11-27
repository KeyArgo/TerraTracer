"""
computation.py

Functions that handle data computations, transformations, and general operations. Contains:
- Ordering points to form polygons.
- Generating KML representations from TZT data.
"""

# Standard library imports
import math  # Used for basic mathematical operations
import logging

logging.basicConfig(level=logging.DEBUG)

# Third-party library imports
from geopy.point import Point  # Used for representing geographical points
from geographiclib.geodesic import Geodesic  # Provides geodesic calculations
from scipy.spatial import ConvexHull  # Used for computations related to convex hulls

# Imports from io_operations
from io_operations import (
    get_computation_method,
    get_bearing_and_distance
)


# Spherical Model
def compute_gps_coordinates_spherical(lat, long, bearing, distance):
    """
    Computes GPS coordinates using the spherical model.

    This function calculates the new latitude and longitude based on the starting coordinates, 
    a bearing, and a distance. It assumes a spherical model of the Earth.

    Args:
    - lat (float): Latitude of the starting point in degrees.
    - long (float): Longitude of the starting point in degrees.
    - bearing (float): Bearing in degrees from the starting point.
    - distance (float): Distance from the starting point in feet.

    Returns:
    - tuple: A tuple (latitude, longitude) of the computed coordinates in degrees.
    """
    R = 6378137.0  # Earth radius in meters
    distance = distance * 0.3048  # Convert distance from feet to meters

    lat_rad = math.radians(lat)
    long_rad = math.radians(long)

    # Calculate the new latitude and longitude using the spherical model
    new_lat = math.asin(math.sin(lat_rad) * math.cos(distance/R) +
                        math.cos(lat_rad) * math.sin(distance/R) * math.cos(math.radians(bearing)))
    new_long = long_rad + math.atan2(math.sin(math.radians(bearing)) * math.sin(distance/R) * math.cos(lat_rad),
                                     math.cos(distance/R) - math.sin(lat_rad) * math.sin(new_lat))

    return (math.degrees(new_lat), math.degrees(new_long))
    

# Vincenty's Method
def compute_gps_coordinates_vincenty(lat, long, bearing, distance):
    """
    Computes GPS coordinates using Vincenty's formula.

    Vincenty's formula is more accurate over long distances than the spherical model, 
    as it considers the Earth's ellipsoidal shape.

    Args:
    - lat (float): Latitude of the starting point in degrees.
    - long (float): Longitude of the starting point in degrees.
    - bearing (float): Bearing in degrees from the starting point.
    - distance (float): Distance from the starting point in feet.

    Returns:
    - tuple: A tuple (latitude, longitude) of the computed coordinates in degrees.
    """
    start_point = Point(latitude=lat, longitude=long)
    distance_in_meters = distance * 0.3048  # Convert distance from feet to meters
    destination = geopy_distance(meters=distance_in_meters).destination(point=start_point, bearing=bearing)
    return destination.latitude, destination.longitude
    
    
# Karney's Method
def compute_gps_coordinates_karney(lat, long, bearing, distance):
    """
    Computes GPS coordinates using the Karney algorithm.

    This function calculates new latitude and longitude based on the starting coordinates,
    a bearing, and a distance using the Karney algorithm. This method is known for its
    high accuracy over both short and long distances and across various bearing angles.

    Args:
    - lat (float): Latitude of the starting point in degrees.
    - long (float): Longitude of the starting point in degrees.
    - bearing (float): Bearing in degrees from the starting point.
    - distance (float): Distance from the starting point in feet.

    Returns:
    - tuple: A tuple containing the new latitude and longitude in degrees.
    """
    distance_in_meters = distance * 0.3048  # Convert distance from feet to meters
    geod = Geodesic.WGS84
    result = geod.Direct(lat, long, bearing, distance_in_meters)
    return result['lat2'], result['lon2']


# Average Methods
def average_methods(lat, long, bearing, distance):
    """
    Averages the latitude and longitude results obtained from different GPS coordinate computation methods.

    Parameters:
    - lat (float): Latitude of the starting point.
    - long (float): Longitude of the starting point.
    - bearing (float): Bearing from the starting point.
    - distance (float): Distance from the starting point.

    Returns:
    - tuple: Average latitude and longitude as computed by different methods.
    """
    # Compute coordinates using different methods
    lat_sph, long_sph = compute_gps_coordinates_spherical(lat, long, bearing, distance)
    lat_vin, long_vin = compute_gps_coordinates_vincenty(lat, long, bearing, distance)
    lat_kar, long_kar = compute_gps_coordinates_karney(lat, long, bearing, distance)

    # Average the results of different methods
    average_lat = (lat_sph + lat_vin + lat_kar) / 3
    average_long = (long_sph + long_vin + long_kar) / 3

    return average_lat, average_long


# Methods map for easy reference to computation functions
METHODS_MAP = {
    1: compute_gps_coordinates_karney,
    2: compute_gps_coordinates_vincenty,
    3: compute_gps_coordinates_spherical,
    4: average_methods
}
    
    
def calculate_distance(coord1, coord2):
    """
    Calculate the distance between two geographic coordinates using geopy.

    Parameters:
    - coord1 (tuple): First coordinate (latitude, longitude).
    - coord2 (tuple): Second coordinate (latitude, longitude).

    Returns:
    - float: Distance between the two coordinates in feet.
    """
    # Calculating distance using geopy
    return geopy_distance(coord1, coord2).feet


def compute_point_based_on_method(choice, lat, lon, bearing, distance):
    """
    Computes a point based on the selected GPS computation method.

    Parameters:
    - choice (int): The user's choice of computation method.
    - lat (float): Latitude of the starting point.
    - lon (float): Longitude of the starting point.
    - bearing (float): Bearing from the starting point.
    - distance (float): Distance from the starting point.

    Returns:
    - tuple: The computed latitude and longitude, or None if an error occurs.
    """
    try:
        # Selecting the computation method based on user choice
        method = METHODS_MAP.get(choice)
        if method:
            return method(lat, lon, bearing, distance)
        else:
            print("Invalid method choice.")
            return None, None
    except Exception as e:
        print(f"An error occurred while computing the point: {e}")
        return None, None

    
def gather_monument_data(coordinate_format, lat, lon, use_same_format_for_all):
    """
    Gathers data for a monument based on user inputs and calculates its position.

    This function collects bearing and distance information from the user and computes the
    coordinates of the monument. The user can specify if they want to use a different coordinate
    format from the one initially provided. The function also prompts for a label for the monument.

    Args:
    - coordinate_format (int): The format of the coordinates.
    - lat (float): Latitude of the starting point.
    - lon (float): Longitude of the starting point.
    - use_same_format_for_all (bool): Flag to indicate if the same coordinate format should be used for all monuments.

    Returns:
    - tuple: A tuple containing the updated coordinate format and a tuple with the monument's data (latitude, longitude, label, bearing, distance).
    """
    from io_operations import get_coordinate_format_only, get_bearing_and_distance
    
    # If different coordinate format is needed, prompt the user to select one
    if not use_same_format_for_all:
        coordinate_format = get_coordinate_format_only()

    # Get bearing and distance from the user
    bearing, distance = get_bearing_and_distance(coordinate_format)

    # Check if user wants to exit
    if bearing is None and distance is None:  # User wants to exit
        return coordinate_format, None

    # Compute new coordinates for the monument
    lat, lon = compute_point_based_on_method(1, lat, lon, bearing, distance)

    # Prompt for a label for the monument
    monument_label = input("Enter a label for the monument (e.g., Monument, Point A, etc.): ")

    # Prepare and return the results
    results = (lat, lon, monument_label, bearing, distance)
    return coordinate_format, results


def gather_polygon_points(data, coordinate_format, lat, lon, use_same_format_for_all, num_points):
    """
    Gathers and computes polygon points based on user-provided inputs.

    This function interacts with the user to compute and collect new points for constructing a polygon. 
    It leverages the user's chosen computation method, along with specified bearing and distance, to calculate 
    each new point. The function continuously updates the polygon data structure with these points and returns 
    the updated data, the list of computed points, and the computation method used.

    Args:
        data (dict): The data dictionary to store polygon points.
        coordinate_format (str): Format for coordinates ('DMS' for degrees, minutes, seconds; 'DD' for decimal degrees).
        lat (float): Latitude of the starting point.
        lon (float): Longitude of the starting point.
        use_same_format_for_all (bool): Flag to use the same coordinate format for all points.
        num_points (int): Number of points to be gathered for the polygon.
    
    Returns:
        tuple: A tuple containing the updated data dictionary, list of points, and the computation method.
    """
    from computation import compute_point_based_on_method

    # Logging the initial sequence of construction steps for debug purposes
    logging.debug(f"Initial construction_sequence: {data['construction_sequence']}")

    points = []
    choice = get_computation_method()

    # Ensuring 'construction_sequence' is initialized in the data dictionary
    if 'construction_sequence' not in data:
        data['construction_sequence'] = ["tie_point"] if 'tie_point' in data else []
    # Explanation: Initializes 'construction_sequence' in the data dictionary if not present.
    # This sequence tracks the order of points added to the polygon.

    for i in range(num_points):
        # Allow changing the coordinate format for each point if required
        if not use_same_format_for_all:
            new_coordinate_format = get_coordinate_format_only()
            if new_coordinate_format:
                coordinate_format = new_coordinate_format
        # Explanation: Iterates over the specified number of points to gather.
        # Allows the user to change the coordinate format for each point if 'use_same_format_for_all' is False.

        # Obtain bearing and distance inputs for the new point calculation
        bearing, distance = get_bearing_and_distance(coordinate_format)
        if bearing is None and distance is None:
            # User requested to exit the process
            print("User requested to exit.")
            return data, points, choice
        # Explanation: For each point, obtains the bearing and distance from the user.
        # If the user chooses to exit, the function returns the current data and points collected.

        # Compute the new point based on selected method, then update data and points list
        lat, lon = compute_point_based_on_method(choice, lat, lon, bearing, distance)
        # Explanation: Computes the next point in the polygon using the selected method (e.g., bearing and distance).

        # Generating a unique identifier for the new point and incorporating it into the data
        point_id = f'P{i + 1}'
        data['polygon'].append({'lat': lat, 'lon': lon, 'id': point_id})
        data['construction_sequence'].append(point_id)
        # Explanation: Generates a unique ID for the new point and adds it to the polygon data structure.

        # Recording the computed point in the list for return
        points.append({'lat': lat, 'lon': lon})
        # Explanation: Stores the computed point's coordinates in a list for later use.

    # Logging the final state of construction_sequence for debugging
    logging.debug(f"Updated construction_sequence: {data['construction_sequence']}")
    # Explanation: Logs the updated sequence of construction steps for debugging purposes.
    return data, points, choice