"""
display_operations.py

Handles the display of data to the user. This module separates the display logic 
from computational logic for clarity and maintainability.
"""

def display_computed_point(points, lat, lon):
    """
    Displays the computed point to the user.
    Args:
    - points (list): List of points already computed.
    - lat (float): Latitude of the computed point.
    - lon (float): Longitude of the computed point.
    """
    print(f"Computed Point {len(points)}: Latitude: {lat:.6f}, Longitude: {lon:.6f}\n")


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