import math
from geopy.distance import distance as geopy_distance
from geopy.point import Point
from geographiclib.geodesic import Geodesic
import re
import os

def save_kml_to_file(kml_content):
    default_directory = os.getcwd()  # This gets the current working directory
    default_filename = "output.kml"

    # Ask the user for the directory and filename
    directory = input(f"Enter the directory to save the KML file (default is {default_directory}): ")
    filename = input(f"Enter the filename for the KML file (default is {default_filename}): ")

    # If the user just presses 'Enter', use the default values
    directory = directory if directory else default_directory
    filename = filename if filename else default_filename

    # Ensure the filename ends with ".kml"
    if not filename.endswith(".kml"):
        filename += ".kml"

    # Join the directory and filename to get the full path
    full_path = os.path.join(directory, filename)

    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Save the KML content to the specified path
    with open(full_path, 'w') as file:
        file.write(kml_content)

    print(f"KML file saved at {full_path}")
    
def order_points(points):
    hull = ConvexHull(points)
    return [points[i] for i in hull.vertices]
    
def generate_kml_polygon(points, color="#ffffff"):
    kml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>GPS Polygon</name>
    <description>Polygon from the computed GPS points</description>
'''

    kml_footer = '''  </Document>
</kml>'''

    ordered_points = order_points(points)
    ordered_points.append(ordered_points[0])  # Close the polygon
    coordinates_str = "\n".join([f"{lon},{lat}" for lat, lon in ordered_points])

    # Here's the modification to add a black border
    kml_polygon = f'''
    <Placemark>
      <name>Polygon</name>
      <Style>
         <LineStyle>
            <color>ff000000</color>
            <width>2</width>
         </LineStyle>
         <PolyStyle>
            <color>{color[1:]}</color>
         </PolyStyle>
      </Style>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              {coordinates_str}
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
'''
    
    return kml_header + kml_polygon + kml_footer
    
def validate_dms(degrees, coordinate_name):
    if coordinate_name == "latitude" and (degrees < 0 or degrees > 90):
        raise ValueError("Invalid latitude degree value. It should be between 0 and 90.")
    elif coordinate_name == "longitude" and (degrees < 0 or degrees > 180):
        raise ValueError("Invalid longitude degree value. It should be between 0 and 180.")

def get_coordinate_in_dd_or_dms(coordinate_format, coordinate_name="latitude"):
    if coordinate_format == "1":
        value = float(input(f"Enter {coordinate_name} in decimal degrees (e.g., 68.0106 or -68.0106): "))
        return value

    elif coordinate_format == "2":
        dms_str = input(f"Enter {coordinate_name} in DMS format (e.g., 68° 00' 38\"N [for latitude] or 110° 00' 38\"W [for longitude]): ")
        _, dd_value = parse_and_convert_dms_to_dd(dms_str, coordinate_name)
        return dd_value

    else:
        print("Invalid choice.")
        return None

def parse_and_convert_dms_to_dd(dms_str, coordinate_name):
    match = re.match(r"(?i)([NSEW])?\s*(\d+)[^\d]*(°|degrees)?\s*(\d+)?'?\s*(\d+(\.\d+)?)?\"?\s*([NSEW])?", dms_str)
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
        print(f"Start Direction: {start_direction}, Turn Direction: {turn_direction}")  # Debug print
        raise ValueError("Invalid combination of starting and turning directions.")
    
    return bearing

def parse_dd_or_dms():
    format_choice = input("Enter direction format (1 for DD, 2 for DMS): ")

    if format_choice == "1":
        direction = input("Enter the starting direction (North, South, East, West) abbreviated as N, S, E, or W: ").upper()
        dd_value = float(input("Enter the angle from the starting direction in decimal degrees (e.g., 68.0106): "))

        # Adjust for land survey notation in DD format
        if direction == "E":
            bearing = 90  # Setting East to 90°
        elif direction == "N":
            bearing = dd_value
        elif direction == "S":
            bearing = 180 + dd_value
        elif direction == "W":
            bearing = 270 + dd_value
        else:
            print("Invalid direction")
            return None

        return bearing

    elif format_choice == "2":
        dms_direction = input("Enter direction in DMS format (e.g., N 68° 00' 38\"): ")
        if " " in dms_direction:  # Check for space to differentiate between land survey and typical GPS
            bearing = parse_and_convert_dms_to_dd_survey(dms_direction, "direction")
        else:
            _, bearing = parse_and_convert_dms_to_dd(dms_direction, "direction")
            if _ == "S":
                bearing = 180 + bearing
            elif _ == "W":
                bearing = 270 + bearing
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
    coordinate_format = input("Enter coordinates format (1 for DD, 2 for DMS): ")
    
    lat = get_coordinate_in_dd_or_dms(coordinate_format, "latitude")
    long = get_coordinate_in_dd_or_dms(coordinate_format, "longitude")
    
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
    points = []  # List to store all computed points
    for idx in range(num_points):
        bearing = parse_dd_or_dms()
        if bearing is not None:
            distance = float(input("Enter distance in feet: ").replace(',', ''))
            if choice == 1:
                lat, long = compute_gps_coordinates_karney(lat, long, bearing, distance)
            elif choice == 2:
                lat, long = compute_gps_coordinates_vincenty(lat, long, bearing, distance)
            elif choice == 3:
                lat, long = compute_gps_coordinates_spherical(lat, long, bearing, distance)
            elif choice == 4:
                lat, long = average_methods(lat, long, bearing, distance)
            points.append((lat, long))
            print(f"Computed Point {idx+1}: Latitude: {lat:.6f}, Longitude: {long:.6f}\n")

    # Check if the last point is the same as the first point to determine if the polygon is closed
    while geopy_distance(points[0], points[-1]).feet > 10:  # Using a threshold of 10 feet
        print("Warning: Your polygon is not closed.")
        add_point = input("Would you like to enter one more point to close the polygon? (yes/no): ").strip().lower()
        
        if add_point == "yes":
            bearing = parse_dd_or_dms()
            if bearing is not None:
                distance = float(input("Enter distance in feet: ").replace(',', ''))
                # Use the last point's latitude and longitude as the starting point
                lat, long = points[-1]
                if choice == 1:
                    lat, long = compute_gps_coordinates_karney(lat, long, bearing, distance)
                elif choice == 2:
                    lat, long = compute_gps_coordinates_vincenty(lat, long, bearing, distance)
                elif choice == 3:
                    lat, long = compute_gps_coordinates_spherical(lat, long, bearing, distance)
                elif choice == 4:
                    lat, long = average_methods(lat, long, bearing, distance)
                points.append((lat, long))
                print(f"Computed Point {len(points)}: Latitude: {lat:.6f}, Longitude: {long:.6f}\n")  # Displaying the point number dynamically
        else:
            print("The polygon will be closed using the first point as the last point.")
            points.append(points[0])  # Add the first point as the last point to close the polygon

    export_choice = input("Do you want to export the points to a KML file? (yes/no): ")
    if export_choice.lower() == 'yes':
        # Generate KML content for polygon
        kml_content = generate_kml_polygon(points, color="#3300FF00")  # 20% transparent green
    
        # Save to a .kml file
        save_kml_to_file(kml_content)

main()
