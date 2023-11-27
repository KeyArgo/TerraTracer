"""
file_io.py

This module provides functions related to file input and output operations, including:
- Retrieving file paths from the user.
- Writing data in JSON format to files.
- Saving KML formatted data to files.
- Parsing JSON formatted files.
"""

import os
import json
import logging
from scipy.spatial import ConvexHull

logging.basicConfig(level=logging.DEBUG, filename='../logs/application.log', filemode='a', format='%(asctime)s:%(levelname)s:%(message)s')


def setup_directories():
    """
    Sets up directories for storing KML and JSON files.

    This function creates directories to store KML and JSON files. It ensures that these directories
    exist, and if not, they are created. The function returns the absolute paths of these directories.

    Returns:
        tuple: A tuple containing the paths to the KML and JSON directories.
    """
    # Define paths for KML and JSON directories
    kml_directory = os.path.abspath(os.path.join(os.pardir, 'saves', 'kml'))
    json_directory = os.path.abspath(os.path.join(os.pardir, 'saves', 'json'))

    # Create the directories if they do not exist
    os.makedirs(kml_directory, exist_ok=True)
    os.makedirs(json_directory, exist_ok=True)

    return kml_directory, json_directory


def save_kml_to_file(kml_content, full_path):
    """
    Save the provided KML content into a file.

    This function writes the KML content to a specified file path. It ensures that the directory
    where the file is to be saved exists, and if not, creates it. Any errors during file writing 
    or directory creation are reported to the user.

    Parameters:
    - kml_content (str): The KML file content to be written. Expected to be in XML format.
    - full_path (str): The full path (including filename) where the KML file should be saved.
    """
    # Ensure the directory exists or create it
    directory = os.path.dirname(full_path)
    try:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory {directory}: {e}")
        return

    # Save the KML content to the specified file
    try:
        # Writing KML content to file
        with open(full_path, 'w') as file:
            file.write(kml_content)
        print(f"KML file saved at {full_path}")
    except IOError as e:
        print(f"Error writing to KML file at {full_path}: {e}")


def save_data_to_json(data_content, full_path):
    """
    Save the provided data as a JSON file.

    This function writes the given data content into a JSON file at the specified path. It ensures
    that the directory where the file is to be saved exists, creating it if necessary. Errors encountered
    during the file-writing process are reported to the user.

    Parameters:
    - data_content: The data to be saved, expected to be in a format compatible with JSON serialization.
    - full_path (str): The full path (including filename) where the JSON file should be saved.
    """
    # Ensure the directory exists or create it
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    # Save the data to the specified JSON file
    try:
        with open(full_path, 'w') as file:
            json.dump(data_content, file, indent=4)
        logging.info(f"JSON file created: {full_path}")
        print(f"JSON file saved at {full_path}")
    except Exception as e:
        print(f"Error writing to file: {e}")


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
    # Format the point into a KML Placemark structure
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

    
def generate_complete_kml(placemark_kml="", polygon_kml="", polygon_name="GPS Polygon and Reference Point"):
    """
    Combine the provided KML placemark and polygon content with the required KML header and footer.

    This function creates a complete KML document by combining the header, footer, placemark KML, 
    and polygon KML content. It can be used to generate a complete KML file that includes both 
    a placemark and a polygon representation.

    Args:
    - placemark_kml (str): KML representation of the placemark.
    - polygon_kml (str): KML representation of the polygon.
    - polygon_name (str): Name of the polygon to be included in the KML file.

    Returns:
    - str: Complete KML content.
    """
    # KML header with the document name and description
    header = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{polygon_name}</name>
    <description>Polygon from the computed GPS points with reference point</description>
    """

    # KML footer to close the document
    footer = """
  </Document>
</kml>
"""
    return header + placemark_kml + polygon_kml + footer

    
def generate_kml_polygon(points, color="#3300FF00", polygon_name="Polygon"):
    """
    Generate the KML representation of a polygon using a list of points.

    Args:
    - points (list of tuple): List of lat-long tuples representing the polygon vertices.
    - color (str): Color for the polygon fill.
    - polygon_name (str): Name of the polygon.

    Returns:
    - str: KML representation of the polygon.
    """
    coordinates_str = "\n".join([f"{lon},{lat}" for lat, lon in points])
    kml = f"""
    <Placemark>
      <name>{polygon_name}</name>
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


    # Ordering points to form a polygon
    ordered_points = order_points(points)
    ordered_points.append(ordered_points[0])  # Close the polygon
    coordinates_str = "\n".join([f"{lon},{lat}" for lat, lon in ordered_points])

    return kml_polygon_header + coordinates_str + kml_polygon_footer