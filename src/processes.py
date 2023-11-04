"""
processes.py

High-level operations and workflows that orchestrate the use of functions 
from other modules. Includes the overall process of converting JSON formatted 
data to KML.
"""

# Standard library imports
import os

# Third-party library imports
from geopy.distance import distance as geopy_distance
from geopy.point import Point
from geographiclib.geodesic import Geodesic

# Local module imports
from utils import (
    transform_tzt_data_to_kml_format,
    get_coordinate_in_dd_or_dms,
)
from computation import (
    compute_gps_coordinates_spherical,
    compute_gps_coordinates_vincenty,
    compute_gps_coordinates_karney,
    average_methods,
    gather_monument_data
)

from file_io import (
    save_data_to_json,
    save_kml_to_file,
    generate_kml_placemark,
    generate_complete_kml,
    generate_kml_polygon,
    load_data_from_json,
    get_unique_filename,
    setup_directories,
)

# Imports from io_operations
from io_operations import (
    get_coordinate_format_only,
    get_tie_point_coordinate_format,
    ask_use_same_format_for_all,
    get_computation_method,
    get_num_points_to_compute,
    get_bearing_and_distance,
    get_export_decision,
    get_file_type_choice,
    gather_tie_point_coordinates
)

# Imports from data_operations
from data_operations import (
    initialize_data,
    update_polygon_data,
    check_polygon_closure,
    finalize_json_structure,
    finalize_data,
    organize_data_for_export
)

# Imports from display_operations
from display_operations import (
    display_computed_point,
    display_starting_point,
    display_monument_point,
)


def json_to_kml(filepath):
    parsed_data = load_data_from_json(filepath)
    if not parsed_data:
        print("Failed to parse the .json file.")
        return

    transformed_data = transform_tzt_data_to_kml_format(parsed_data)
    kml_content = generate_kml_from_json_data(transformed_data)
    save_kml_to_file(kml_content)

    print("Conversion from .json to .kml completed!")


def gather_polygon_points(data, coordinate_format, lat, lon, use_same_format_for_all):
    from computation import compute_point_based_on_method
    points = []
    choice = get_computation_method()
    num_points = get_num_points_to_compute()
    
    for _ in range(num_points):
        if not use_same_format_for_all:
            new_coordinate_format = get_coordinate_format_only()
            if new_coordinate_format:
                coordinate_format = new_coordinate_format

        bearing, distance = get_bearing_and_distance(coordinate_format)
        if bearing is None and distance is None:  # User wants to exit
            break

        lat, lon = compute_point_based_on_method(choice, lat, lon, bearing, distance)
        data = update_polygon_data(data, lat, lon, bearing, distance)
        points.append((lat, lon))
        display_computed_point(points, lat, lon)
    return data, points, choice


def polygon_main_menu():
    print("\n\n\n------------------ Create Custom Geometric Polygon ------------------")
    print("_____________________________________________________________________")
    print("\nThis menu allows you to create a KML or JSON file for polygons")
    print("using common bearings, distances or metes and bounds commonly used")
    print("in land descriptions.  You can begin with a Tie Point or specify a")
    print("set of starting coordinates for your polygon.")
    print("_____________________________________________________________________")
    print("\nChoose an option:")
    print("1) Use a Tie Point")
    print("2) Specify the first point of the polygon")
    print("3) Exit to Main Menu")
    return input("Enter your choice (1/2/3): ")


def tie_point_menu():
    print("\nChoose an option:")
    print("1) Use initial point as Monument/Placemark")
    print("2) Find and place the first point of the polygon")
    print("3) Exit to Main Menu")
    choice = input("Enter your choice (1/2/3): ").strip()
    while choice not in ["1", "2", "3"]:
        print("Invalid choice. Please select 1, 2 or 3.")
        choice = input("Enter your choice (1/2/3): ").strip()
    return choice


def gather_data_from_user():
    data = initialize_data()
    
    # Display the Polygon Main Menu
    main_choice = polygon_main_menu()

    if main_choice == "1":  # Using a Tie Point
        # Gather initial coordinates (Tie Point Location)
        lat, lon = gather_tie_point_coordinates()
        
        # Check if lat and lon are None (indicating a return to the Main Menu)
        if lat is None and lon is None:
            # Handle return to Main Menu or exit the function.
            return
        data["initial"] = {"lat": lat, "lon": lon}
        
        # Initialize the coordinate_format here
        coordinate_format = get_coordinate_format_only()

        # Prompt the user if they want to use the same format for all computed points
        use_same_format_for_all = ask_use_same_format_for_all()

        # Display the Tie Point Menu
        point_use_choice = tie_point_menu()

        if point_use_choice == "1":  # Monument/Placemark choice
            # For monument choice
            coordinate_format, results = gather_monument_data(coordinate_format, lat, lon, use_same_format_for_all)
            if results:
                lat, lon, monument_label, bearing, distance = results
                data["monument"] = {
                    "lat": lat,
                    "lon": lon,
                    "label": monument_label,
                    "bearing_from_prev": bearing,
                    "distance_from_prev": distance
                }
                display_monument_point(lat, lon)
            else:
                print("Monument data could not be gathered. Please try again.")
                return  # Exit the function if no monument data is gathered

        elif point_use_choice == "2":  # Starting point of polygon choice
            display_starting_point(lat, lon)

    elif main_choice == "2":  # Directly specify the placement of the first point
        lat, lon = gather_tie_point_coordinates()
        if lat is None or lon is None:
            return
        data["initial"] = {"lat": lat, "lon": lon}

        # Initialize the coordinate_format here
        coordinate_format = get_coordinate_format_only()

        # Prompt the user if they want to use the same format for all computed points
        use_same_format_for_all = ask_use_same_format_for_all()

    elif main_choice == "3":  # Exit to Main Menu
        return None

    else:
        print("Invalid choice. Please enter 1, 2, or 3.")
        return None
    
    # If we reach this point, we're ready to gather the polygon points
    data, points, choice = gather_polygon_points(data, coordinate_format, lat, lon, use_same_format_for_all)
    
    # Finalize the data by potentially adding more points
    print(f"Debug: coordinate_format is {coordinate_format}")
    data = finalize_data(data, points, use_same_format_for_all, coordinate_format, choice)
    
    return data


def create_kml_content(data, close_polygon=False):
    try:
        monument_kml = ""
        polygon_kml = ""

        # Only create a monument placemark if lat and lon are provided and not None
        monument = data.get('monument', {})
        if monument.get('lat') is not None and monument.get('lon') is not None:
            monument_kml = generate_kml_placemark(
                monument['lat'], 
                monument['lon'], 
                name=monument.get('label', "Monument")
            )

        # Generate polygon KML as before
        if 'polygon' in data:
            polygon_points = [(point['lat'], point['lon']) for point in data['polygon'] if 'lat' in point and 'lon' in point]
            if close_polygon and not check_polygon_closure(polygon_points):
                # Close the polygon by appending the first point at the end if needed
                polygon_points.append(polygon_points[0])
            polygon_kml = generate_kml_polygon(polygon_points)

        # Combine monument and polygon into one KML, omitting monument if it doesn't exist
        complete_kml = generate_complete_kml(monument_kml, polygon_kml) if monument_kml else polygon_kml
        return complete_kml
    except (KeyError, ValueError) as e:
        print(f"An error occurred while creating KML content: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def export_kml(data, kml_path, points):
    # The check_polygon_closure function should be defined elsewhere
    close_polygon = check_polygon_closure(points)  # This should return True or False
    kml_content = create_kml_content(data, close_polygon=close_polygon)
    
    if kml_content:
        save_kml_to_file(kml_content, kml_path)
        print(f"KML file saved at {kml_path}")
    else:
        print("Failed to generate KML content.")


def export_json(data, json_path):
    final_data = finalize_json_structure(data)
    save_data_to_json(final_data, json_path)
    print(f"Data file saved at {json_path}")


def create_kml_process():
    data = gather_data_from_user()
    if not data or 'polygon' not in data:
        print("Data gathering was not completed. Exiting.")
        return

    # Extract polygon points from the data
    points = [(point['lat'], point['lon']) for point in data['polygon']]
    print("Polygon Points:", points)
    
    # Check if the polygon is closed
    is_polygon_closed = check_polygon_closure(points)
    if not is_polygon_closed:
        print("Warning: Your polygon is not closed.")

    # Get the user's decision to export
    if get_export_decision():
        file_type_choice = get_file_type_choice()
        kml_directory, json_directory = setup_directories()

        # Ask for the filename only once
        filename = input("Enter the filename for the file (without extension): ")
        kml_path = os.path.join(kml_directory, f"{filename}.kml")
        json_path = os.path.join(json_directory, f"{filename}.json")

        # Check if either file already exists
        while os.path.exists(kml_path) or os.path.exists(json_path):
            print("A file with that name already exists. Please choose a different filename.")
            filename = input("Enter a new filename for the file (without extension): ")
            kml_path = os.path.join(kml_directory, f"{filename}.kml")
            json_path = os.path.join(json_directory, f"{filename}.json")

        # Export KML if chosen
        if file_type_choice in ["K", "B"]:
            export_kml(data, kml_path, points)  # Points are now passed here as required
            
        # Export JSON if chosen
        if file_type_choice in ["D", "B"]:
            export_json(data, json_path)
            
        # Notify user of saved files
        if file_type_choice == 'B':
            print(f"Both KML and JSON files have been saved. KML: {kml_path}, JSON: {json_path}")
        elif file_type_choice == 'K':
            print(f"KML file location: {kml_path}")
        elif file_type_choice == 'D':
            print(f"JSON file location: {json_path}")

    return data

