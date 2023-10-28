import os
from scipy.spatial import ConvexHull

def get_filepath():
    default_directory = os.getcwd()
    default_filename = "output.tzt"
    directory = input(f"Enter the directory to save the Data file (default is {default_directory}): ") or default_directory
    filename = input(f"Enter the filename for the Data file (default is {default_filename}): ") or default_filename
    if not filename.endswith(".tzt"):
        filename += ".tzt"
    return os.path.join(directory, filename)


def write_initial_coordinates(file, initial):
    file.write("[INITIAL]\n")
    file.write(f"Latitude: {initial.get('lat', ''):.6f}\n")
    file.write(f"Longitude: {initial.get('lon', ''):.6f}\n\n")


def write_monument_details(file, monument):
    if monument:
        file.write("[MONUMENT]\n")
        file.write(f"Label: {monument.get('label', '')}\n")
        file.write(f"Latitude: {monument.get('lat', ''):.6f}\n")
        file.write(f"Longitude: {monument.get('lon', ''):.6f}\n\n")


def write_polygon_details(file, polygon):
    file.write("[POLYGON]\n")
    for i, point in enumerate(polygon):
        lat = point.get('lat', 0)
        lon = point.get('lon', 0)
        bearing = point.get('bearing_from_prev', 0)
        distance = point.get('distance_from_prev', 0)
        file.write(f"Point {i+1}: Latitude: {lat:.6f}, Longitude: {lon:.6f}, ")
        file.write(f"Bearing from Previous: {bearing:.2f}°, Distance from Previous: {distance:.2f} ft\n")


def save_data_to_file(data_content, initial_coords, monument=None):
    full_path = get_filepath()
    
    # Check data structure
    if not isinstance(data_content, dict) or not all(key in data_content for key in ['initial', 'polygon']):
        print("Error: Invalid data structure or missing data.")
        return

    try:
        if not os.path.exists(os.path.dirname(full_path)):
            os.makedirs(os.path.dirname(full_path))
    except PermissionError:
        print(f"Error: No permission to create directory at {os.path.dirname(full_path)}")
        return
    except Exception as e:
        print(f"Error creating directory: {e}")
        return

    try:
        with open(full_path, 'w') as file:
            write_initial_coordinates(file, data_content.get('initial', {}))

            # Explicitly check if 'monument' key exists in the dictionary
            if 'monument' in data_content and data_content['monument']:
                write_monument_details(file, data_content['monument'])

            write_polygon_details(file, data_content.get('polygon', []))

        print(f"Data file saved at {full_path}")
    except PermissionError:
        print(f"Error: No permission to write to {full_path}")
    except IOError:
        print(f"Error: Unable to write to {full_path}. The file might be in use.")
    except Exception as e:
        print(f"Error writing to file: {e}")

    
def save_kml_to_file(kml_content):
    """
    Save the provided KML content into a file.
    
    Parameters:
    - kml_content (str): The KML content to be saved.

    Note:
    The user can specify the directory and filename for the KML file.
    """

    # Default directory and filename
    default_directory = os.getcwd()  # This gets the current working directory
    default_filename = "output.kml"

    # Ask the user for directory and filename to save the KML file
    directory = input(f"Enter the directory to save the KML file (default is {default_directory}): ")
    filename = input(f"Enter the filename for the KML file (default is {default_filename}): ")

    # If no directory/filename provided, use the default values
    directory = directory if directory else default_directory
    filename = filename if filename else default_filename

    # Ensure the filename has the correct extension
    if not filename.endswith(".kml"):
        filename += ".kml"

    # Get the full path for the file
    full_path = os.path.join(directory, filename)

    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Save the KML content to the specified file
    with open(full_path, 'w') as file:
        file.write(kml_content)

    # Inform the user about the saved file location
    print(f"KML file saved at {full_path}")
    

def order_points(points):
    """
    Order the provided points to form a convex hull.
    
    Parameters:
    - points (list): List of points (latitude, longitude).

    Returns:
    - list: Ordered points forming a convex hull.

    Note:
    If there are fewer than 3 unique points, the original list is returned.
    """
    # Remove duplicates
    unique_points = list(set(points))

    # Not enough points to form a convex hull
    if len(unique_points) < 3:
        print("Warning: Not enough unique points to compute a convex hull.")
        return points  # Return the original points as there's no hull to compute

    # Compute the convex hull
    hull = ConvexHull(unique_points)
    return [unique_points[i] for i in hull.vertices]


def generate_kml_initial_point(lat, lon, name="Initial Point"):
    """
    Generate a KML placemark for the initial point or monument.
    
    Parameters:
    - lat (float): Latitude of the point.
    - lon (float): Longitude of the point.
    - name (str, optional): Name for the placemark.

    Returns:
    - str: KML formatted string for the placemark.
    """

    kml_placemark = f'''
    <Placemark>
      <name>{name}</name>
      <Point>
        <coordinates>
          {lon},{lat}
        </coordinates>
      </Point>
    </Placemark>
'''
    return kml_placemark


def generate_kml_placemark(lat, lon, name="Reference Point", description="Initial Reference Point"):
    """
    Generate a KML placemark for a single point.
    
    Parameters:
    - lat (float): Latitude of the point.
    - lon (float): Longitude of the point.
    - name (str, optional): Name of the placemark.
    - description (str, optional): Description for the placemark.

    Returns:
    - str: KML formatted string for the placemark.
    """
    placemark = f"""<Placemark>
      <name>{name}</name>
      <description>{description}</description>
      <Point>
        <coordinates>
          {lon},{lat}
        </coordinates>
      </Point>
    </Placemark>"""
    return placemark

    
def generate_complete_kml(placemark_kml="", polygon_kml=""):
    """
    Combine the provided KML placemark and polygon content with the required KML header and footer.

    Args:
    - placemark_kml (str): KML representation of the placemark.
    - polygon_kml (str): KML representation of the polygon.

    Returns:
    - str: Complete KML content.
    """
    header = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>GPS Polygon and Reference Point</name>
    <description>Polygon from the computed GPS points with reference point</description>
"""

    footer = """
  </Document>
</kml>
"""
    return header + placemark_kml + polygon_kml + footer

    
def generate_kml_polygon(points, color="#3300FF00"):
    """
    Generate the KML representation of a polygon using a list of points.

    Args:
    - points (list of tuple): List of lat-long tuples representing the polygon vertices.
    - color (str): Color for the polygon fill.

    Returns:
    - str: KML representation of the polygon.
    """
    coordinates_str = "\n".join([f"{lon},{lat}" for lat, lon in points])
    kml = f"""
    <Placemark>
      <name>Polygon</name>
      <Style>
         <LineStyle>
            <color>ff000000</color>
            <width>2</width>
         </LineStyle>
         <PolyStyle>
            <color>{color}</color>
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
    """
    return kml


    # Ordering points to form a polygon
    ordered_points = order_points(points)
    ordered_points.append(ordered_points[0])  # Close the polygon
    coordinates_str = "\n".join([f"{lon},{lat}" for lat, lon in ordered_points])

    return kml_polygon_header + coordinates_str + kml_polygon_footer