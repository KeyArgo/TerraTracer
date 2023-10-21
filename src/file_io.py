import os
from scipy.spatial import ConvexHull

def save_data_to_file(data_content, initial_coords, monument=None):
    """
    Save the provided data content into a file.
    
    Parameters:
    - data_content (dict): The content to be saved, including initial point, monument details, and polygon points.
    - initial_coords (tuple): The initial latitude and longitude coordinates.
    - monument (dict, optional): Details of the monument if it exists.

    Note:
    The file format is .tzt and the user can specify the directory and filename.
    """
    # Default directory and filename
    default_directory = os.getcwd()
    default_filename = "output.tzt"

    # Taking input for directory and filename to save the file
    directory = input(f"Enter the directory to save the Data file (default is {default_directory}): ")
    filename = input(f"Enter the filename for the Data file (default is {default_filename}): ")

    # If no directory/filename provided, use the default
    directory = directory if directory else default_directory
    filename = filename if filename else default_filename

    # Ensure the filename has the correct extension
    if not filename.endswith(".tzt"):
        filename += ".tzt"

    full_path = os.path.join(directory, filename)

    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Writing the data into the file
    with open(full_path, 'w') as file:
        # Write initial coordinates
        file.write("[INITIAL]\n")
        initial = data_content.get('initial', {})
        file.write(f"Latitude: {initial.get('lat', ''):.6f}\n")
        file.write(f"Longitude: {initial.get('lon', ''):.6f}\n\n")
        
        # If a monument exists, write its details
        monument = data_content.get('monument', {})
        if monument:
            file.write("[MONUMENT]\n")
            file.write(f"Label: {monument.get('label', '')}\n")
            file.write(f"Latitude: {monument.get('lat', ''):.6f}\n")
            file.write(f"Longitude: {monument.get('lon', ''):.6f}\n\n")
        
        # Write polygon points, bearing, and distance
        file.write("[POLYGON]\n")
        for i, point in enumerate(data_content.get('polygon', [])):
            lat = point.get('lat', 0)
            lon = point.get('lon', 0)
            bearing = point.get('bearing_from_prev', 0)
            distance = point.get('distance_from_prev', 0)
            file.write(f"Point {i+1}: Latitude: {lat:.6f}, Longitude: {lon:.6f}, ")
            file.write(f"Bearing from Previous: {bearing:.2f}°, Distance from Previous: {distance:.2f} ft\n")
 
    # Inform the user about the saved file location 
    print(f"Data file saved at {full_path}")
    
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
    Combine a placemark and polygon into a complete KML document.
    
    Parameters:
    - placemark (str): KML formatted string for the placemark.
    - polygon_kml (str): KML formatted string for the polygon.
    - color (str, optional): Color for the polygon.

    Returns:
    - str: Complete KML document combining the placemark and polygon.
    """
    kml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>GPS Polygon and Reference Point</name>
    <description>Polygon from the computed GPS points with reference point</description>
'''
    
    kml_footer = '''  </Document>
</kml>'''

    # Combine header, placemark, polygon, and footer to create the complete KML
    complete_kml = kml_header + placemark + polygon_kml + kml_footer

    return complete_kml

    
def generate_kml_polygon(points, color="#ffffff"):
    """
    Generate a KML polygon from the provided list of points.
    
    Parameters:
    - points (list): List of points (latitude, longitude) to form the polygon.
    - color (str, optional): Color for the polygon.

    Returns:
    - str: KML formatted string for the polygon.
    """
    
    # KML polygon header
    kml_polygon_header = f'''
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
'''
    
    # KML polygon footer
    kml_polygon_footer = '''
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
'''

    # Ordering points to form a polygon
    ordered_points = order_points(points)
    ordered_points.append(ordered_points[0])  # Close the polygon
    coordinates_str = "\n".join([f"{lon},{lat}" for lat, lon in ordered_points])

    return kml_polygon_header + coordinates_str + kml_polygon_footer

def tzt_to_kml(tzt_content):
    """
    Converts a given .tzt formatted string to a .kml formatted string.
    
    Parameters:
    - tzt_content (str): The content of the .tzt file.
    
    Returns:
    - str: The generated .kml content.
    """
    
    # Splitting the content into lines and initializing data storage
    lines = tzt_content.strip().split("\n")
    data = {
        'initial': {},
        'monument': {},
        'polygon': []
    }
    
    # Parsing the .tzt file
    section = None
    for line in lines:
        try:
            if "[INITIAL]" in line:
                section = 'initial'
            elif "[MONUMENT]" in line:
                section = 'monument'
            elif "[POLYGON]" in line:
                section = 'polygon'
            elif section == 'initial':
                key, value = line.split(":")
                data['initial'][key.strip().lower()] = float(value.strip())
            elif section == 'monument' and "Label" not in line:
                key, value = line.split(":")
                data['monument'][key.strip().lower()] = float(value.strip()) if "Latitude" in key or "Longitude" in key else value.strip()
            elif section == 'polygon':
                point_data = {}
                parts = line.split(",")
                for part in parts:
                    key, value = part.split(":")
                    if "Latitude" in key or "Longitude" in key:
                        point_data[key.strip().lower()] = float(value.strip())
                data['polygon'].append(point_data)
        except ValueError:
            print(f"Error parsing line: {line}")
    
    # Generating KML for the initial point and monument
    initial_lat = data['initial']['latitude']
    initial_lon = data['initial']['longitude']
    
    initial_placemark = generate_kml_initial_point(initial_lat, initial_lon)
    
    monument_lat = data['monument']['latitude']
    monument_lon = data['monument']['longitude']
    
    monument_placemark = generate_kml_placemark(monument_lat, monument_lon, name=data['monument']['label'], description=data['monument']['label'])
    
    # Generating KML for the polygon
    polygon_coords = [(point['latitude'], point['longitude']) for point in data['polygon']]
    
    polygon_kml = generate_kml_polygon(polygon_coords)
    
    # Combining the KML segments
    complete_kml = generate_complete_kml(initial_placemark + monument_placemark, polygon_kml)
    
    return complete_kml

