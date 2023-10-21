# Standard library imports
import math

# Third-party library imports
from geopy.point import Point
from geographiclib.geodesic import Geodesic

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