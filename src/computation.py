"""
computation.py

Functions that handle data computations, transformations, and general operations. Contains:
- Ordering points to form polygons.
- Generating KML representations from TZT data.
"""

# Standard library imports
<<<<<<< HEAD
import math  # Used for basic mathematical operations
import logging

logging.basicConfig(level=logging.DEBUG)
=======
import math
>>>>>>> parent of 2d50135 (### Added)

# Third-party library imports
from geopy.point import Point
from geographiclib.geodesic import Geodesic
from scipy.spatial import ConvexHull

# Imports from io_operations
from io_operations import (
    get_computation_method,
    get_bearing_and_distance
)


# Spherical Model
def compute_gps_coordinates_spherical(lat, long, bearing, distance):
    R = 6378137.0  # Earth radius in meters
    distance = distance * 0.3048  # Convert distance from feet to meters

    lat_rad = math.radians(lat)
    long_rad = math.radians(long)

    new_lat = math.asin(math.sin(lat_rad) * math.cos(distance/R) +
                        math.cos(lat_rad) * math.sin(distance/R) * math.cos(math.radians(bearing)))
    new_long = long_rad + math.atan2(math.sin(math.radians(bearing)) * math.sin(distance/R) * math.cos(lat_rad),
                                     math.cos(distance/R) - math.sin(lat_rad) * math.sin(new_lat))

    return (math.degrees(new_lat), math.degrees(new_long))
    
# Vincenty's Method
def compute_gps_coordinates_vincenty(lat, long, bearing, distance):
    start_point = Point(latitude=lat, longitude=long)
    distance_in_meters = distance * 0.3048
    destination = geopy_distance(meters=distance_in_meters).destination(point=start_point, bearing=bearing)
    return destination.latitude, destination.longitude
    
# Karney's Method
def compute_gps_coordinates_karney(lat, long, bearing, distance):
    distance_in_meters = distance * 0.3048
    geod = Geodesic.WGS84
    result = geod.Direct(lat, long, bearing, distance_in_meters)
    return result['lat2'], result['lon2']

# Average Methods
def average_methods(lat, long, bearing, distance):
    lat_sph, long_sph = compute_gps_coordinates_spherical(lat, long, bearing, distance)
    lat_vin, long_vin = compute_gps_coordinates_vincenty(lat, long, bearing, distance)
    lat_kar, long_kar = compute_gps_coordinates_karney(lat, long, bearing, distance)

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
    return geopy_distance(coord1, coord2).feet


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

    
def gather_monument_data(coordinate_format, lat, lon, use_same_format_for_all):
    from io_operations import get_coordinate_format_only, get_bearing_and_distance
    if not use_same_format_for_all:
        coordinate_format = get_coordinate_format_only()
    
    bearing, distance = get_bearing_and_distance(coordinate_format)
    if bearing is None and distance is None:  # User wants to exit
        return coordinate_format, None
    
    lat, lon = compute_point_based_on_method(1, lat, lon, bearing, distance)
    monument_label = input("Enter a label for the monument (e.g., Monument, Point A, etc.): ")
    results = (lat, lon, monument_label, bearing, distance)
    return coordinate_format, results