"""
display_operations.py

Handles the display of data to the user. This module separates the display logic 
from computational logic for clarity and maintainability.
"""

def display_computed_point(points, lat, lon, is_initial_point=False, is_closing_point=False):
    """
    Displays the computed point or the initial point to the user.

    This function prints out the details of a computed point. It labels the point as either the 
    initial point, a regular computed point, or the closing point of a polygon, based on flags.

    Args:
    - points (list): List of points already computed.
    - lat (float): Latitude of the computed point.
    - lon (float): Longitude of the computed point.
    - is_initial_point (bool): Flag to indicate if this is the initial point.
    - is_closing_point (bool): Flag to indicate if this is the closing point of the polygon.
    """
    if is_initial_point:
        point_label = "Initial Point"
    elif is_closing_point:
        # Label as returning to the initial point if it's the closing point of the polygon
        point_label = "Returning to Initial Point"
    else:
        # Label as a regular computed point with its index in the points list
        point_label = f"Computed Point {len(points)}"

    print(f"{point_label}: Latitude: {lat}, Longitude: {lon}")


def display_starting_point(lat, lon):
    """
    Displays the starting point to the user.

    This function is called to show the latitude and longitude of the starting point of a computation
    or a polygon drawing process.

    Args:
    - lat (float): Latitude of the starting point.
    - lon (float): Longitude of the starting point.
    """
    # Display the starting point coordinates with precision up to 6 decimal places
    print(f"Starting Point: Latitude: {lat:.6f}, Longitude: {lon:.6f}\n")


def display_monument_point(lat, lon):
    """
    Displays the monument point to the user.

    This function prints the latitude and longitude of a monument point. It is typically called
    when the monument's location has been computed or identified, providing a visual confirmation
    to the user.

    Args:
    - lat (float): Latitude of the monument point.
    - lon (float): Longitude of the monument point.
    """
    # Display the monument point coordinates with precision up to 6 decimal places
    print(f"Monument: Latitude: {lat:.6f}, Longitude: {lon:.6f}\n")