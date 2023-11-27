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
<<<<<<< HEAD
import logging
import random  # Import the random module
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
=======
>>>>>>> parent of 2d50135 (### Added)
from scipy.spatial import ConvexHull
from xml.dom.minidom import Document


def setup_directories():
    kml_directory = os.path.abspath(os.path.join(os.pardir, 'saves', 'kml'))
    json_directory = os.path.abspath(os.path.join(os.pardir, 'saves', 'json'))
    os.makedirs(kml_directory, exist_ok=True)
    os.makedirs(json_directory, exist_ok=True)
    return kml_directory, json_directory


<<<<<<< HEAD
def save_kml_to_file(kml_content, full_path):
    """
    Save the provided KML content into a file.
    """
    # Ensure the directory exists or create it
    directory = os.path.dirname(full_path)
    try:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory {directory}: {e}")
        return False
=======
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
>>>>>>> parent of 2d50135 (### Added)

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
<<<<<<< HEAD
        return True
    except IOError as e:
        print(f"Error writing to KML file at {full_path}: {e}")
        return False
=======
    except Exception as e:
        print(f"Error writing to file: {e}")
>>>>>>> parent of 2d50135 (### Added)


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


def import_json_data(filepath):
    """
    Imports JSON data from a given file path and converts it into a Python dictionary.
    
    Args:
        filepath (str): The path of the JSON file to be imported.

    Returns:
        dict: A dictionary containing the imported JSON data.
    """
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
        # Additional validation can be added here to check the structure of the JSON.
        return data
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        return None
    except FileNotFoundError:
        logging.error("JSON file not found.")
        return None


from xml.dom.minidom import Document
from pathlib import Path
import logging
import tkinter as tk
from tkinter import filedialog
import random

def export_json_to_kml(data, filename='exported_file'):
    """
    Exports the provided JSON data to a KML file, with an option to choose a different save directory.

    Args:
        data (dict): The JSON data to be exported in KML format.
        filename (str): The default filename for the KML file. 
                        The file extension '.kml' will be added automatically.

    Returns:
        bool: True if the file was successfully saved, False otherwise.
    """
    try:
        # Correct the default directory path
        script_directory = Path(__file__).resolve().parent
        default_directory = script_directory.parent / 'exports' / 'kml'

        user_choice = input("Use default directory 'exports/kml'? (Y/N): ").strip().lower()

        if user_choice == 'n':
            save_directory = choose_save_directory(str(default_directory))
        else:
            save_directory = str(default_directory)

        # Setting the full filepath
        filepath = Path(save_directory).joinpath(filename + '.kml').as_posix()
        
        # Create the KML document structure
        doc = Document()
        kml = doc.createElement('kml')
        kml.setAttribute('xmlns', 'http://www.opengis.net/kml/2.2')
        doc.appendChild(kml)

        document = doc.createElement('Document')
        kml.appendChild(document)

        # Document name and description
        name_element = doc.createElement('name')
        name_text = doc.createTextNode(data.get('polygon_name', 'Unknown'))
        name_element.appendChild(name_text)
        document.appendChild(name_element)

        description_element = doc.createElement('description')
        description_text = doc.createTextNode('Polygon and reference points based on provided data')
        description_element.appendChild(description_text)
        document.appendChild(description_element)

        # Define styles
        style_polygon = doc.createElement('Style')
        style_polygon.setAttribute('id', 'polygonStyle')
        poly_style = doc.createElement('PolyStyle')
        color_poly = doc.createElement('color')
        color_poly_text = doc.createTextNode(random_color_with_transparency())
        color_poly.appendChild(color_poly_text)
        poly_style.appendChild(color_poly)
        style_polygon.appendChild(poly_style)

        line_style = doc.createElement('LineStyle')
        color_line = doc.createElement('color')
        color_line_text = doc.createTextNode('ff000000')
        color_line.appendChild(color_line_text)
        line_style.appendChild(color_line)
        style_polygon.appendChild(line_style)

        document.appendChild(style_polygon)

        # Construct the placemark for the polygon
        polygon_placemark = doc.createElement('Placemark')
        polygon_name = doc.createElement('name')
        polygon_name_text = doc.createTextNode(data['polygon_name'])
        polygon_name.appendChild(polygon_name_text)
        polygon_placemark.appendChild(polygon_name)
        polygon_placemark.appendChild(style_polygon.cloneNode(True))
        
        polygon_element = doc.createElement('Polygon')
        outer_boundary_is_element = doc.createElement('outerBoundaryIs')
        linear_ring_element = doc.createElement('LinearRing')
        
        coords_str = " ".join(
            f"{point['lon']},{point['lat']},0" for point in data['polygon']
        ) + f" {data['polygon'][0]['lon']},{data['polygon'][0]['lat']},0"

        coords_element = doc.createElement('coordinates')
        coords_text_node = doc.createTextNode(coords_str)
        coords_element.appendChild(coords_text_node)
        
        linear_ring_element.appendChild(coords_element)
        outer_boundary_is_element.appendChild(linear_ring_element)
        polygon_element.appendChild(outer_boundary_is_element)
        
        polygon_placemark.appendChild(polygon_element)
        document.appendChild(polygon_placemark)

        # Optionally, create a placemark for the monument if it exists in the data
        if 'monument' in data:
            monument = data['monument']
            monument_placemark = doc.createElement('Placemark')
            
            monument_name = doc.createElement('name')
            monument_name_text = doc.createTextNode(monument.get('label', 'Unknown'))
            monument_name.appendChild(monument_name_text)
            monument_placemark.appendChild(monument_name)

            monument_description = doc.createElement('description')
            monument_description_text = doc.createTextNode('Reference Point')
            monument_description.appendChild(monument_description_text)
            monument_placemark.appendChild(monument_description)
            
            point_element = doc.createElement('Point')
            coords_element = doc.createElement('coordinates')
            coords_text_node = doc.createTextNode(f"{monument['lon']},{monument['lat']},0")
            coords_element.appendChild(coords_text_node)
            point_element.appendChild(coords_element)

            monument_placemark.appendChild(point_element)
            document.appendChild(monument_placemark)

        # Convert the Document object to a string and use the save_kml_to_file function
        kml_content = doc.toprettyxml(indent="  ")
        save_success = save_kml_to_file(kml_content, filepath)

        if not save_success:
            print("Failed to save KML file.")
            return False

        print(f"KML file successfully exported to {filepath}")
        return True

    except Exception as e:
        logging.error(f"Error exporting to KML: {e}")
        print(f"Error exporting to KML: {e}")
        return False


def random_color_with_transparency():
    """
    Generates a random color with 20% transparency in KML format.
    """
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    # 20% transparency (33 in hexadecimal)
    return f"33{b:02x}{g:02x}{r:02x}"


def choose_save_directory(default_dir, title="Select Save Directory"):
    """
    Prompts the user to choose a save directory.

    Args:
        default_dir (str): The default directory path.
        title (str): The title for the dialog window.

    Returns:
        str: The selected directory path.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    chosen_directory = filedialog.askdirectory(initialdir=default_dir, title=title)
    root.destroy()  # Close the Tkinter root window
    return chosen_directory if chosen_directory else default_dir

def choose_file(default_dir, filetypes, title="Select File"):
    """
    Prompts the user to choose a file.

    Args:
        default_dir (str): The default directory path.
        filetypes (list): List of tuples for file types, e.g., [("JSON files", "*.json")]
        title (str): The title for the dialog window.

    Returns:
        str: The selected file path.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(initialdir=default_dir, title=title, filetypes=filetypes)
    root.destroy()  # Close the Tkinter root window
    return file_path