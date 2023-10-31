"""
data_operations.py

Handles the creation, manipulation, and validation of data structures used 
in the main program workflow.
"""

from geopy.distance import distance as geopy_distance


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