"""
utils.py

Utility functions that offer general-purpose tools and transformations. Includes:
- Data transformations between TZT and KML formats.
"""

import re
from geopy.distance import distance as geopy_distance

def validate_dms(degrees, coordinate_name):
    """
    Validates the degrees value for latitude and longitude in DMS format.
    
    Parameters:
    - degrees (float): Degree value to validate.
    - coordinate_name (str): Name of the coordinate ("latitude" or "longitude").

    Raises:
    - ValueError: If degrees value is invalid.
    """
    if coordinate_name == "latitude" and (degrees < 0 or degrees > 90):
        raise ValueError("Invalid latitude degree value. It should be between 0 and 90.")
    elif coordinate_name == "longitude" and (degrees < 0 or degrees > 180):
        raise ValueError("Invalid longitude degree value. It should be between 0 and 180.")
    elif degrees == 0:
        raise ValueError("Degree value cannot be zero.")
		
def get_coordinate_in_dd_or_dms(coordinate_format, coordinate_name="latitude"):
    """
    Prompts the user to enter coordinates in either decimal degrees (DD) or degrees, minutes, seconds (DMS) format.
    
    Parameters:
    - coordinate_format (str): The chosen format ("1" for DD, "2" for DMS).
    - coordinate_name (str, optional): Name of the coordinate ("latitude" or "longitude").

    Returns:
    - float: Coordinate value in decimal degrees.
    """
    while True:
        if coordinate_format == "1":
            try:
                value = input(f"Enter {coordinate_name} in decimal degrees format (e.g., 68.0106 or -68.0106): ")
                # Check if entered value is in DMS format
                if any(char in value for char in ['°', '\'', '\"']):
                    raise ValueError("DMS format detected. Please enter in decimal degrees as chosen.")
                return float(value)
            except ValueError as e:
                print(f"Error: {e}. Please try again.")

        elif coordinate_format == "2":
            try:
                dms_str = input(f"Enter {coordinate_name} in DMS format (e.g., 68° 00' 38\"N [for latitude] or 110° 00' 38\"W [for longitude]): ")
                _, dd_value = parse_and_convert_dms_to_dd(dms_str, coordinate_name)
                return dd_value
            except ValueError as e:
                print(f"Error: {e}. Please try again.")
        else:
            print("Invalid choice.")
            return None

def parse_and_convert_dms_to_dd(dms_str, coordinate_name):
    """
    Parses a DMS formatted string and converts it to decimal degrees.
    
    Parameters:
    - dms_str (str): String in DMS format.
    - coordinate_name (str): Name of the coordinate ("latitude" or "longitude").

    Returns:
    - tuple: (Primary direction [N/S/E/W], Coordinate value in decimal degrees).
    """
    match = re.match(r"(?i)([NSEW])?\s*(\d{1,3})[^\d]*(°|degrees)?\s*(\d{1,2})?'?\s*(\d{1,2}(\.\d+)?)?\"?\s*([NSEW])?", dms_str)
    if not match:
        print("Invalid DMS string format. Please try again.")
        return None, None
    
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
    Parses a DMS formatted string in land survey notation and returns the bearing in decimal degrees.
    
    Parameters:
    - dms_str (str): String in DMS land survey format.
    - coordinate_name (str): Name of the coordinate ("latitude" or "longitude").

    Returns:
    - float: Bearing in decimal degrees.
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
    Process the user's input for direction based on the provided format (either DD or DMS).

    Returns:
    - float: Bearing in decimal degrees.
    """

    # Prompt the user for a valid coordinate_format if it's None or not "1" or "2"
    while coordinate_format not in ["1", "2"]:
        print("Please specify the coordinate format: (1 for DD, 2 for DMS)")
        coordinate_format = input()

    if coordinate_format == "1":  # DD format
        orientation = input("Enter starting orientation (N, S, E, W): ").upper()
        
        # Check the orientation immediately
        if orientation not in ["N", "S", "E", "W"]:
            print("Invalid orientation.")
            return None

        dd_value = float(input("Enter direction in decimal degrees (e.g., 68.0106): "))

        if orientation == "N":
            bearing = dd_value
        elif orientation == "S":
            bearing = 180 + dd_value
        elif orientation == "E":
            bearing = 90 + dd_value
        elif orientation == "W":
            bearing = 270 + dd_value

        if 0 <= bearing <= 360:
            return bearing
        else:
            print("Invalid DD value. Must be between 0 and 360.")
            return None

    elif coordinate_format == "2":  # DMS format
        dms_direction = input(
            "Enter direction in DMS format. Examples:\n"
            "- N 68° 00' 38\" E\n"
            "- N 68 degrees 0' 38\" E\n"
            "- n 68 0 38 e\n\n"
            "Your input: "
        )
        if " " in dms_direction:  # Check for space to differentiate between land survey and typical GPS
            bearing = parse_and_convert_dms_to_dd_survey(dms_direction, "direction")

        else:
            direction, bearing = parse_and_convert_dms_to_dd(dms_direction, "direction")
            if direction is None:
                print("Invalid DMS string format. Please try again.")
                return parse_dd_or_dms(coordinate_format)  # Recursively ask for input again, passing in the format
            if direction == "S":
                bearing = 180 + bearing
            elif direction == "W":
                bearing = 270 + bearing
        return bearing

    else:
        print("Invalid format passed to the function.")
        return None

            
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

def transform_tzt_data_to_kml_format(parsed_data):
    data = {
        'initial': {
            'lat': float(parsed_data['initial']['latitude']),
            'lon': float(parsed_data['initial']['longitude'])
        },
        'monument': {
            'label': parsed_data['monument']['label'],
            'lat': float(parsed_data['monument']['latitude']),
            'lon': float(parsed_data['monument']['longitude']),
            'bearing_from_prev': float(parsed_data['monument']['bearing from previous'].split('°')[0]),
            'distance_from_prev': float(parsed_data['monument']['distance from previous'].split(' ')[0])
        },
        'polygon': []
    }

    for key, value in parsed_data['polygon'].items():
        if 'latitude' in key:
            point = {
                'lat': float(value),
                'lon': float(parsed_data['polygon'][f'longitude {key.split()[-1]}']),
                'bearing_from_prev': float(parsed_data['polygon'][f'bearing from previous {key.split()[-1]}'].split('°')[0]),
                'distance_from_prev': float(parsed_data['polygon'][f'distance from previous {key.split()[-1]}'].split(' ')[0])
            }
            data['polygon'].append(point)

    return data
