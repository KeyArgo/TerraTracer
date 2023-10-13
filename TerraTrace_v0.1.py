import math
from geopy.distance import distance as geopy_distance
from geopy.point import Point
from geographiclib.geodesic import Geodesic
import re

def get_coordinate_in_dd_or_dms(coordinate_name="latitude"):
    format_choice = input(f"Enter {coordinate_name} format (1 for DD, 2 for DMS): ")

    if format_choice == "1":
        value = float(input(f"Enter {coordinate_name} in decimal degrees (e.g., 68.0106 or -68.0106): "))
        return value

    elif format_choice == "2":
        dms_str = input(f"Enter {coordinate_name} in DMS format (e.g., N 68° 00' 38\" or S 68° 00' 38\"): ")
        _, dd_value = parse_and_convert_dms_to_dd_updated(dms_str)
        return dd_value

    else:
        print("Invalid choice.")
        return None

def parse_and_convert_dms_to_dd_updated(dms_str):
    match = re.match(r"(?i)([NSEW])?\s*(\d+)[^\d]+(°|degrees)?\s*(\d+)'(\s*(\d+(\.\d+)?)\"?)?\s*([NSEW])?", dms_str)

    if not match:
        raise ValueError("Invalid DMS string format.")
    
    direction1, degrees, _, minutes, seconds, _, _, direction2 = match.groups()
    if seconds:
        seconds = float(seconds.replace("\"", ""))
    else:
        seconds = 0.0
    
    dd = float(degrees) + float(minutes)/60 + seconds/3600
    
    direction = ((direction1 or '') + (direction2 or '')).upper()
        
    if direction in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]:
        if direction == "N":
            pass  # already in positive
        elif direction == "S":
            if direction2 and direction2.upper() == "E":
                dd = 180 - dd
            else:
                dd = 180 + dd
        elif direction == "E":
            dd = dd
        elif direction == "W":
            dd = 360 - dd
        elif direction == "SE":
            dd = 180 - dd
        elif direction == "SW":
            dd = 180 + dd
    else:
        raise ValueError("Direction not provided.")


    return direction, dd

def parse_dd_or_dms():
    format_choice = input("Enter direction format (1 for DD, 2 for DMS): ")

    if format_choice == "1":
        direction = input("Enter direction (e.g., N, S, E, W, NE, NW, SE, SW): ").upper()
        dd_value = float(input("Enter direction in decimal degrees (e.g., 68.0106): "))

        if direction == "N":
            bearing = dd_value
        elif direction == "S":
            bearing = 180 - dd_value
        elif direction == "E":
            bearing = dd_value
        elif direction == "W":
            bearing = 270 - dd_value
        else:
            print("Invalid direction")
            return None

        return bearing

    elif format_choice == "2":
        dms_direction = input("Enter direction in DMS format (e.g., N 68° 00' 38\"): ")
        _, bearing = parse_and_convert_dms_to_dd_updated(dms_direction)
        return bearing

    else:
        print("Invalid choice.")
        return None

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
    
def main():
    lat = get_coordinate_in_dd_or_dms("latitude")
    long = get_coordinate_in_dd_or_dms("longitude")
    
    if lat is None or long is None:
        return

    print(f"Starting Coordinates: {lat:.6f}, {long:.6f}\n")
    
    print("Choose a method:")
    print("1) Karney's Method")
    print("2) Vincenty's Method")
    print("3) Spherical Model")
    print("4) Average all models/methods")
    choice = int(input("Enter choice (1/2/3/4): "))

    num_points = int(input("Enter the number of points to compute: "))

    for idx in range(num_points):
        bearing = parse_dd_or_dms()
        if bearing is None:
            continue
        
        print(f"Bearing: {bearing:.6f}\n")
        distance = float(input("Enter distance in feet: ").replace(',', ''))

        if choice == 1:
            lat, long = compute_gps_coordinates_karney(lat, long, bearing, distance)
        elif choice == 2:
            lat, long = compute_gps_coordinates_vincenty(lat, long, bearing, distance)
        elif choice == 3:
            lat, long = compute_gps_coordinates_spherical(lat, long, bearing, distance)
        elif choice == 4:
            lat, long = average_methods(lat, long, bearing, distance)
        else:
            print("Invalid choice.")
            return

        print(f"N{idx+1}: {lat:.6f}, {long:.6f}\n")

main()
