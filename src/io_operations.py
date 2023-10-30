"""
io_operations.py

Handles input/output operations for the program. It prompts the user for inputs
and handles user choices related to the main workflow.
"""

from utils import (get_coordinate_in_dd_or_dms, parse_dd_or_dms)

def get_coordinate_format_only():
    """
    Prompt the user to choose between DD and DMS format for coordinates input.
    Returns:
    - str: User's choice of coordinate format (either "1" or "2").
    """
    while True:
        coordinate_format = input("Enter coordinates format (1 for DD, 2 for DMS): ")
        if coordinate_format in ["1", "2"]:
            return coordinate_format
        print("Invalid choice. Please select 1 for DD or 2 for DMS.")


def ask_use_same_format_for_all():
    """
    Ask the user if they want to use the same coordinate format for all computed points.
    Returns:
    - bool: True if the user wants to use the same format, False otherwise.
    """
    while True:
        decision = input("Do you want to use this format for all computed points? (yes/no): ").strip().lower()
        if decision == 'yes':
            return True
        elif decision == 'no':
            return False
        print("Invalid choice. Please enter 'yes' or 'no'.")


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


def get_bearing_and_distance(coordinate_format):
    """
    Prompt the user for bearing and distance.
    Returns:
    - tuple: Bearing and distance provided by the user.
    """
    while True:
        try:
            bearing = parse_dd_or_dms(coordinate_format)
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