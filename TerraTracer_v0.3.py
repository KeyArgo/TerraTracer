import math
from geopy.distance import distance as geopy_distance
from geopy.point import Point
from geographiclib.geodesic import Geodesic
from scipy.spatial import ConvexHull
import re
import os

def calculate_distance(coord1, coord2):
    return geopy_distance.distance(coord1, coord2).feet
    
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
    unique_points = list(set(points))  # Remove duplicates
    
    if len(unique_points) < 3:
        print("Warning: Not enough unique points to compute a convex hull.")
        return points  # Return the original points as there's no hull to compute
    
    hull = ConvexHull(unique_points)
    return [unique_points[i] for i in hull.vertices]

def generate_kml_placemark(lat, lon, name="Reference Point", description="Initial Reference Point"):
    """
    Generate a KML placemark for a single point.
    """
    placemark = f'''
    <Placemark>
      <name>{name}</name>
      <description>{description}</description>
      <Point>
        <coordinates>
          {lon},{lat}
        </coordinates>
      </Point>
    </Placemark>
    '''
    return placemark
    
def generate_complete_kml(placemark, polygon_kml, color="#ffffff"):
    """
    Combine placemark and polygon into a complete KML.
    """
    kml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>GPS Polygon and Reference Point</name>
    <description>Polygon from the computed GPS points with reference point</description>
'''
    kml_footer = '''  </Document>
</kml>'''
    
    # Extract the inner content of the polygon KML to avoid including the header and footer
    polygon_inner_content = polygon_kml.split("<Document>")[1].split("</Document>")[0].strip()
    
    return kml_header + placemark + polygon_inner_content + kml_footer
    
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
    elif degrees == 0:
        raise ValueError("Degree value cannot be zero.")

def get_coordinate_in_dd_or_dms(coordinate_format, coordinate_name="latitude"):
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
        orientation = input("Enter starting orientation (N, S, E, W): ").upper()
        dd_value = float(input("Enter direction in decimal degrees (e.g., 68.0106): "))

        if orientation == "N":
            bearing = dd_value
        elif orientation == "S":
            bearing = 180 + dd_value
        elif orientation == "E":
            bearing = 90 + dd_value
        elif orientation == "W":
            bearing = 270 + dd_value
        else:
            print("Invalid orientation.")
            return None

        if 0 <= bearing <= 360:
            return bearing
        else:
            print("Invalid DD value. Must be between 0 and 360.")
            return None

    elif format_choice == "2":
        dms_direction = input("Enter direction in DMS format (e.g., N 68° 00' 38\"): ")
        if " " in dms_direction:  # Check for space to differentiate between land survey and typical GPS
            bearing = parse_and_convert_dms_to_dd_survey(dms_direction, "direction")
        else:
            direction, bearing = parse_and_convert_dms_to_dd(dms_direction, "direction")
            if direction is None:
                print("Invalid DMS string format. Please try again.")
                return parse_dd_or_dms()  # Recursively ask for input again
            if direction == "S":
                bearing = 180 + bearing
            elif direction == "W":
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
    
def main():
    while True:
        coordinate_format = input("Enter coordinates format (1 for DD, 2 for DMS): ")
        if coordinate_format not in ["1", "2"]:
            print("Invalid choice. Please select 1 for DD or 2 for DMS.")
            continue
        break

    lat = get_coordinate_in_dd_or_dms(coordinate_format, "latitude")
    lon = get_coordinate_in_dd_or_dms(coordinate_format, "longitude")

    if lat is None or lon is None:
        return

    print("\nHow would you like to use the initial coordinates?")
    print("1) As a starting location (won't be included in the polygon).")
    print("2) As Point 1 of the polygon.")
    coordinate_use_choice = input("Enter choice (1/2): ")

    points = []  # List to store all computed points
    reference_point = None  # Store the reference point if it's a monument

    if coordinate_use_choice == "1":
        print("\nDo you want the initial point to be:")
        print("1) A Monument (will become a placemark).")
        print("2) First Point of the Polygon (no placemark).")
        point_use_choice = input("Enter choice (1/2): ")
        if point_use_choice == "1":
            monument_label = input("Enter a label for the monument (e.g., Monument, Point A, etc.): ")
            reference_point = (lat, lon, monument_label)
        elif point_use_choice == "2":
            # Do not add the initial coordinates to the points list here
            # This will be taken care of when the first computed point is added
            pass
        else:
            print("Invalid choice.")
            return
    elif coordinate_use_choice == "2":
        points.append((lat, lon))
        print(f"Point 1: Latitude: {lat:.6f}, Longitude: {lon:.6f}\n")
            
    print("Choose a method:")
    print("1) Karney's Method")
    print("2) Vincenty's Method")
    print("3) Spherical Model")
    print("4) Average all models/methods")
    choice = int(input("Enter choice (1/2/3/4): "))

    num_points = int(input("How many points would you like to compute? "))

    for i in range(num_points):  # Loop for the number of points the user wants to compute
        bearing = parse_dd_or_dms()
        if bearing is not None:
            distance = float(input("Enter distance in feet: ").replace(',', ''))

            # Compute new point
            if choice == 1:
                lat, lon = compute_gps_coordinates_karney(lat, lon, bearing, distance)
            elif choice == 2:
                lat, lon = compute_gps_coordinates_vincenty(lat, lon, bearing, distance)
            elif choice == 3:
                lat, lon = compute_gps_coordinates_spherical(lat, lon, bearing, distance)
            elif choice == 4:
                lat, lon = average_methods(lat, lon, bearing, distance)
            else:
                print("Invalid method choice.")
                return

            points.append((lat, lon))
            print(f"Computed Point {len(points)}: Latitude: {lat:.6f}, Longitude: {lon:.6f}\n")

            # If it's the first iteration and the user selected "As a starting location", adjust the monument location
            if i == 0 and coordinate_use_choice == "1" and 'monument_label' in locals():
                reference_point = (lat, lon, monument_label)

    while True:  # Infinite loop to prompt the user
        if check_polygon_closure(points, reference_point):
            print("Your polygon is completed.")
            break
        elif is_polygon_close_to_being_closed(points):
            print("Warning: Your polygon is not closed.")
            print("Your polygon is close enough to being closed.")
        else:
            print("Warning: Your polygon is not closed.")
        
        add_point_decision = input("Would you like to enter another point before closing the polygon? (yes/no): ").strip().lower()

        if add_point_decision == 'yes':
            bearing = parse_dd_or_dms()
            if bearing is not None:
                distance = float(input("Enter distance in feet: ").replace(',', ''))

                # Compute new point
                if choice == 1:
                    lat, lon = compute_gps_coordinates_karney(lat, lon, bearing, distance)
                elif choice == 2:
                    lat, lon = compute_gps_coordinates_vincenty(lat, lon, bearing, distance)
                elif choice == 3:
                    lat, lon = compute_gps_coordinates_spherical(lat, lon, bearing, distance)
                elif choice == 4:
                    lat, lon = average_methods(lat, lon, bearing, distance)
                else:
                    print("Invalid method choice.")
                    return

                points.append((lat, lon))
                print(f"Computed Point {len(points)}: Latitude: {lat:.6f}, Longitude: {lon:.6f}\n")

        elif add_point_decision == 'no':
            break
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")

    if not check_polygon_closure(points, reference_point):
        print("Warning: Your polygon is not closed.")
                                                                
    export_choice = input("Do you want to export the polygon to a KML file? (yes/no): ")
    if export_choice.lower() == 'yes':
        # Generate KML content for polygon
        kml_polygon = generate_kml_polygon(points, color="#3300FF00")  # 20% transparent green

        kml_content = kml_polygon  # By default, only the polygon is present

        # If there's a monument, generate its KML
        if reference_point:
            kml_placemark = generate_kml_placemark(*reference_point[:2], name=reference_point[2], description=reference_point[2])
            # Combine the placemark and polygon into a complete KML
            kml_content = generate_complete_kml(kml_placemark, kml_polygon)

        # Save to a .kml file
        save_kml_to_file(kml_content)

if __name__ == "__main__":
    main()

