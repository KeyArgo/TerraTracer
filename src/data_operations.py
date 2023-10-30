"""
data_operations.py

Handles the creation, manipulation, and validation of data structures used 
in the main program workflow.
"""

from utils import (check_polygon_closure)

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