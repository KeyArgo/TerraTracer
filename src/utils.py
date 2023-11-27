"""
utils.py

Utility functions that offer general-purpose tools and transformations. Includes:
- Data transformations between JSON and KML formats.
"""

import re  # Regular expression operations for string processing
from geopy.distance import distance as geopy_distance  # Geographical distance calculations


def validate_dms(degrees, coordinate_name):
    """
    Validates the degrees value for latitude (0 to 90) and longitude (0 to 180) in DMS format.

    Parameters:
    - degrees (float): Degree value to validate. For latitude, the range is 0 to 90. 
                       For longitude, it's 0 to 180.
    - coordinate_name (str): Name of the coordinate ("latitude" or "longitude").

    Raises:
    - ValueError: If degrees value is outside the valid range for the given coordinate.
    """
    if coordinate_name == "latitude" and (degrees < 0 or degrees > 90):
        raise ValueError("Invalid latitude degree value. It should be between 0 and 90.")
    elif coordinate_name == "longitude" and (degrees < 0 or degrees > 180):
        raise ValueError("Invalid longitude degree value. It should be between 0 and 180.")
		

def get_coordinate_in_dd_or_dms(coordinate_format, coordinate_name="latitude"):
    """
    Prompts the user to enter coordinates in either decimal degrees (DD) or degrees, 
    minutes, seconds (DMS) format. DD is a decimal format, while DMS includes degrees, 
    minutes, and seconds.

    Parameters:
    - coordinate_format (str): The chosen format ("1" for DD, "2" for DMS).
    - coordinate_name (str, optional): Name of the coordinate ("latitude" or "longitude").

    Returns:
    - float or None: Coordinate value in the chosen format or None if the user exits.
    """
    print(f"\nEntering `get_coordinate_in_dd_or_dms` for {coordinate_name}.")

    print(f"\n-------------------- Enter {coordinate_name.capitalize()} --------------------")
    
    while True:
        if coordinate_format == "1":
            print(f"Entering DD format for {coordinate_name}.")
            print(f"\n{coordinate_name.capitalize()} (DD Format):")
            example_value = "68.0106" if coordinate_name == "latitude" else "-110.0106"
            print(f"Example: {example_value}")
            value = input("\nEnter your value or type 'exit' to go to main menu: ").strip()
            print(f"Raw DD input received: {value}")
            if value.lower() == 'exit':
                print("Exiting `get_coordinate_in_dd_or_dms` due to user exiting.")
                return None
            try:
                result = float(value)
                print(f"Exiting `get_coordinate_in_dd_or_dms` with DD value: {result}")
                return result
            except ValueError:
                print("Invalid input. Please enter a valid decimal degree value.")

        elif coordinate_format == "2":
            print(f"Entering DMS format for {coordinate_name}.")
            print(f"\n{coordinate_name.capitalize()} (DMS Format):")
            example_format = "68° 00' 38\"N" if coordinate_name == "latitude" else "110° 00' 38\"W"
            print(f"Example: {example_format}")
            dms_str = input("\nEnter your value or type 'exit' to go to main menu: ").strip()
            print(f"Raw DMS input received: {dms_str}")
            if dms_str.lower() == 'exit':
                print("Exiting `get_coordinate_in_dd_or_dms` due to user exiting.")
                return None
            try:
                _, dd_value = parse_and_convert_dms_to_dd(dms_str, coordinate_name)
                print(f"Exiting `get_coordinate_in_dd_or_dms` with DMS value: {dd_value}")
                return dd_value
            except ValueError as e:
                print(f"Error: {e}. Please try again.")
        else:
            print("Invalid coordinate format choice detected. Exiting `get_coordinate_in_dd_or_dms` with None.")
            return None


def parse_and_convert_dms_to_dd(dms_str, coordinate_name):
    """
    Parses a DMS (Degrees, Minutes, Seconds) formatted string and converts it to decimal degrees.
    
    The DMS string format should be 'N/S/E/W degrees° minutes\' seconds"', e.g., "68° 00' 38\"N".

    Parameters:
    - dms_str (str): String in DMS format.
    - coordinate_name (str): Name of the coordinate ("latitude" or "longitude").

    Returns:
    - tuple: (Primary direction [N/S/E/W], Coordinate value in decimal degrees).
    - Raises ValueError for invalid DMS string formats.
    """
    match = re.match(r"(?i)([NSEW])?\s*(\d{1,3})[^\d]*(°|degrees)?\s*(\d{1,2})?'?\s*(\d{1,2}(\.\d+)?)?\"?\s*([NSEW])?", dms_str)
    if not match:
        raise ValueError("Invalid DMS string format.")
    
    groups = match.groups()
    primary_direction = groups[0] if groups[0] in ["N", "S", "E", "W"] else (groups[-1] if groups[-1] in ["N", "S", "E", "W"] else None)
    degrees = float(groups[1])
    minutes = float(groups[3]) if groups[3] else 0
    seconds = float(groups[4].replace("\"", "")) if groups[4] else 0
    
    dd = degrees + minutes/60 + seconds/3600
    validate_dms(degrees, coordinate_name)
    
    if primary_direction in ["S", "W"]:
        dd = -dd
    
    return primary_direction, dd


def parse_and_convert_dms_to_dd_survey(dms_str, coordinate_name):
    """
    Parses a DMS formatted string in land survey notation and converts it to decimal degrees.

    This function is designed to handle DMS strings in land survey format, which typically involves
    specific notation for bearings. It validates the format and calculates the equivalent bearing in decimal degrees.

    Parameters:
    - dms_str (str): String in DMS land survey format (e.g., "N 45° 30' 30\" E").
    - coordinate_name (str): Name of the coordinate ("latitude" or "longitude").

    Returns:
    - float: Bearing in decimal degrees.
    - Raises ValueError for invalid DMS string formats.
    """
    match = re.match(r"(?i)([NSEW])\s*(\d+)[^\d]*(°|degrees)?\s*(\d+)?'?\s*(\d+(\.\d+)?)?\"?\s*([NSEW])?$", dms_str)
    if not match:
        raise ValueError("Invalid DMS string format.")
    
    groups = match.groups()
    print(f"Captured groups: {groups}")  # Debug print
    
    start_direction = groups[0].upper() if groups[0] else None
    turn_direction = groups[-1].upper() if groups[-1] else None

    degrees = float(groups[1])
    minutes = float(groups[3]) if groups[3] else 0
    seconds = float(groups[4].replace("\"", "")) if groups[4] else 0
    
    dd = degrees + minutes/60 + seconds/3600
    
    # Adjust bearing calculation based on land survey notation
    if start_direction == "N" and turn_direction == "E":
        bearing = dd
    elif start_direction == "N" and turn_direction == "W":
        bearing = 360 - dd
    elif start_direction == "S" and turn_direction == "E":
        bearing = 180 - dd
    elif start_direction == "S" and turn_direction == "W":
        bearing = 180 + dd
    else:
        raise ValueError("Invalid combination of starting and turning directions.")
    
    return bearing
    
    
def parse_dd_or_dms(coordinate_format):
    """
    Processes the user's input for orientation and direction based on the chosen format (DD or DMS).

    This function prompts the user to enter orientation and direction in either Decimal Degrees (DD) 
    or Degrees, Minutes, and Seconds (DMS) format. It handles invalid inputs effectively and converts 
    the input into a bearing in decimal degrees.

    Parameters:
    - coordinate_format (str): The chosen format ("1" for DD, "2" for DMS).

    Returns:
    - float: The calculated bearing in decimal degrees, or None if the user exits.
    """
    # Prompt the user for a valid coordinate_format if it's None or not "1" or "2"
    while coordinate_format not in ["1", "2"]:
        print("Please specify the coordinate format: (1 for DD, 2 for DMS)")
        coordinate_format = input()

    while True:  # Added an outer loop to handle invalid inputs more effectively
        if coordinate_format == "1":  # DD format
            orientation = input("Enter starting orientation (N, S, E, W) or type 'exit' to go to main menu: ").upper()

            if orientation == "EXIT":
                return None

            # Check the orientation immediately
            if orientation not in ["N", "S", "E", "W"]:
                print("Invalid orientation.")
                continue

            dd_value = input("Enter direction in decimal degrees (e.g., 68.0106) or type 'exit' to go to main menu: ")

            if dd_value.lower() == "exit":
                return None

            try:
                dd_value = float(dd_value)
                if orientation == "N":
                    bearing = dd_value
                elif orientation == "S":
                    bearing = 180 + dd_value
                elif orientation == "E":
                    bearing = 90 + dd_value
                elif orientation == "W":
                    bearing = 270 + dd_value

                # Adjust bearing to be between 0 and 360
                while bearing > 360:
                    bearing -= 360
                while bearing < 0:
                    bearing += 360

                if 0 <= bearing <= 360:
                    return bearing
                else:
                    print("Invalid DD value. Must be between 0 and 360.")
            except ValueError:
                print("Invalid input. Please enter a valid decimal degree value.")

        elif coordinate_format == "2":  # DMS format
            dms_direction = input(
                "Enter direction in DMS format. Examples:\n"
                "- N 68° 00' 38\" E\n"
                "- N 68 degrees 0' 38\" E\n"
                "- n 68 0 38 e\n\n"
                "Enter your value or type 'exit' to go to main menu: "
            )

            if dms_direction.lower() == "exit":
                return None

            if " " in dms_direction:  # Check for space to differentiate between land survey and typical GPS
                bearing = parse_and_convert_dms_to_dd_survey(dms_direction, "direction")
                if bearing is not None:
                    return bearing

            else:
                direction, bearing = parse_and_convert_dms_to_dd(dms_direction, "direction")
                if direction:
                    if direction == "S":
                        bearing = 180 + bearing
                    elif direction == "W":
                        bearing = 270 + bearing
                    return bearing
                else:
                    print("Invalid DMS string format. Please try again.")


def parse_dms_to_dd_test(dms_str):
    """
    Converts a DMS string to decimal degrees for testing and verification purposes.

    This function is specifically designed for testing the accuracy of conversions from DMS format to decimal degrees.
    It handles various formats of DMS strings and correctly interprets cardinal directions. The function raises
    a ValueError for invalid formats or combinations of directions.

    Example DMS string: "N 68° 00' 38\" E", which would be converted to a decimal degree value based on the
    cardinal directions provided.

    Args:
    - dms_str (str): The DMS string in a format like "N 68° 00' 38\" E".

    Returns:
    - float: The converted bearing in decimal degrees.
    - Raises ValueError for invalid DMS string formats or invalid combinations of directions.
    """
    match = re.match(r"(?i)([NSEW])?\s*(\d+)[^\d]*(\d+)?'?\s*(\d+(\.\d+)?)?\"?\s*([NSEW])?$", dms_str.strip())
    if not match:
        raise ValueError("Invalid DMS string format.")

    groups = match.groups()
    start_direction = groups[0].upper() if groups[0] else None
    turn_direction = groups[-1].upper() if groups[-1] else None
    degrees = float(groups[1])
    minutes = float(groups[2]) if groups[2] else 0
    seconds = float(groups[3]) if groups[3] else 0

    dd = degrees + minutes / 60 + seconds / 3600

    if start_direction == "N" and turn_direction == "E":
        bearing = dd
    elif start_direction == "N" and turn_direction == "W":
        bearing = 360 - dd
    elif start_direction == "S" and turn_direction == "E":
        bearing = 180 - dd
    elif start_direction == "S" and turn_direction == "W":
        bearing = 180 + dd
    else:
        raise ValueError("Invalid combination of directions.")

    return bearing