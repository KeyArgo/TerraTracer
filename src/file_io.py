"""
file_io.py

This module provides functions related to file input and output operations, including:
- Retrieving file paths from the user.
- Writing data in the TZT format to files.
- Saving KML formatted data to files.
- Parsing TZT formatted files.
"""

import os
import json
from scipy.spatial import ConvexHull


def setup_directories():
    kml_directory = os.path.abspath(os.path.join(os.pardir, 'saves', 'kml'))
    json_directory = os.path.abspath(os.path.join(os.pardir, 'saves', 'json'))
    os.makedirs(kml_directory, exist_ok=True)
    os.makedirs(json_directory, exist_ok=True)
    return kml_directory, json_directory


def get_unique_filename(directory, extension):
    filename = input("Enter the filename for the file (without extension): ")
    file_path = os.path.join(directory, f"{filename}{extension}")
    while os.path.exists(file_path):
        print("A file with that name already exists. Please choose a different filename.")
        filename = input("Enter a new filename for the file (without extension): ")
        file_path = os.path.join(directory, f"{filename}{extension}")
    return file_path


def read_tzt_file(filepath):
    with open(filepath, 'r') as file:
        content = file.read()
    return content


def get_filepath(extension=".json"):
    default_directory = os.getcwd()
    default_filename = f"output{extension}"
    directory = input(f"Enter the directory to save the Data file (default is {default_directory}): ") or default_directory
    filename = input(f"Enter the filename for the Data file (default is {default_filename}): ") or default_filename
    if not filename.endswith(extension):
        filename += extension
    return os.path.join(directory, filename)


def write_initial_coordinates(file, initial):
    print(f"Type of lat in initial: {type(initial.get('lat'))}")
    print(f"Type of lon in initial: {type(initial.get('lon'))}")
    file.write("[INITIAL]\n")
    file.write(f"Latitude: {initial.get('lat', ''):.6f}\n")
    file.write(f"Longitude: {initial.get('lon', ''):.6f}\n\n")


def write_monument_details(file, monument):
    if monument and monument.get('lat') is not None and monument.get('lon') is not None:
        file.write("[MONUMENT]\n")
        file.write(f"Label: {monument.get('label', '')}\n")
        file.write(f"Latitude: {float(monument.get('lat', '0')):.6f}\n")
        file.write(f"Longitude: {float(monument.get('lon', '0')):.6f}\n")
        if monument.get('bearing_from_prev') is not None:
            file.write(f"Bearing from Previous: {float(monument.get('bearing_from_prev')):.2f}°\n")
        if monument.get('distance_from_prev') is not None:
            file.write(f"Distance from Previous: {float(monument.get('distance_from_prev')):.2f} ft\n\n")
        

def write_polygon_details(file, polygon):
    file.write("[POLYGON]\n")
    for i, point in enumerate(polygon):
        print(f"Type of lat in polygon point {i+1}: {type(point.get('lat'))}")
        print(f"Type of lon in polygon point {i+1}: {type(point.get('lon'))}")
        print(f"Type of bearing_from_prev in polygon point {i+1}: {type(point.get('bearing_from_prev'))}")
        print(f"Type of distance_from_prev in polygon point {i+1}: {type(point.get('distance_from_prev'))}")
        file.write(f"Point {i+1}:\n")
        file.write(f"Latitude: {point.get('lat', 0):.6f}\n")
        file.write(f"Longitude: {point.get('lon', 0):.6f}\n")
        file.write(f"Bearing from Previous: {point.get('bearing_from_prev', 0):.2f}°\n")
        file.write(f"Distance from Previous: {point.get('distance_from_prev', 0):.2f} ft\n\n")


def load_data_from_json(filepath):
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                if line.startswith("[") and line.endswith("]"):  # New section
                    current_section = line[1:-1].lower()
                    data[current_section] = {}
                else:
                    key, value = line.split(":")
                    key = key.strip().lower()
                    value = value.strip()
                    data[current_section][key] = value
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
        return None
    except Exception as e:
        print(f"Error parsing the .tzt file: {e}")
        return None

    return data


def save_kml_to_file(kml_content, full_path):
    """Save the provided KML content into a file."""
    # Ensure the directory exists or create it
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    # Save the KML content to the specified file
    try:
        with open(full_path, 'w') as file:
            file.write(kml_content)
        print(f"KML file saved at {full_path}")
    except Exception as e:
        print(f"Error writing to file: {e}")


def save_data_to_json(data_content, full_path):
    """Save the provided data as a JSON file."""
    # Ensure the directory exists or create it
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    # Save the data to the specified JSON file
    try:
        with open(full_path, 'w') as file:
            json.dump(data_content, file, indent=4)
        print(f"Data file saved at {full_path}")
    except Exception as e:
        print(f"Error writing to file: {e}")


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