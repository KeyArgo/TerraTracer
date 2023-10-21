# Standard library imports
import math
import os
import re

# Third-party library imports
from geopy.distance import distance as geopy_distance
from geopy.point import Point
from geographiclib.geodesic import Geodesic
from scipy.spatial import ConvexHull

# Local module imports
from utils import (validate_dms, get_coordinate_in_dd_or_dms, 
                   parse_and_convert_dms_to_dd, parse_and_convert_dms_to_dd_survey, 
                   parse_dd_or_dms, is_polygon_close_to_being_closed, 
                   check_polygon_closure)
from computation import (compute_gps_coordinates_spherical, 
                         compute_gps_coordinates_vincenty, 
                         compute_gps_coordinates_karney, 
                         average_methods, calculate_distance)
from file_io import (save_data_to_file, save_kml_to_file, order_points, 
                     generate_kml_placemark, generate_complete_kml, 
                     generate_kml_polygon)
    
def main():
    """
    Main function to run the program. It prompts the user to input initial coordinates, choose computation methods,
    and compute subsequent GPS points to form a polygon. It also offers the ability to export the results to KML or data files.
    
    Returns:
    - dict: A dictionary containing initial coordinates, monument details (if any), and polygon points.
    """

    # Initializing latitude and longitude
    initial_lat = None
    initial_lon = None

 # Dictionary to store initial coordinates, monument details, and polygon points
    data = {
        "initial": {},
        "monument": {},
        "polygon": []
    }
    
    # Prompt user to choose between DD (Decimal Degrees) and DMS (Degrees Minutes Seconds) format for coordinates input
    while True:
        coordinate_format = input("Enter coordinates format (1 for DD, 2 for DMS): ")
        if coordinate_format not in ["1", "2"]:
            print("Invalid choice. Please select 1 for DD or 2 for DMS.")
            continue
        break

    # Get initial coordinates from the user
    initial_lat = get_coordinate_in_dd_or_dms(coordinate_format, "latitude")
    initial_lon = get_coordinate_in_dd_or_dms(coordinate_format, "longitude")
    lat, lon = initial_lat, initial_lon

    # Check if valid coordinates were provided
    if lat is None or lon is None:
        return
    
    # Save initial coordinates to the data dictionary
    data["initial"] = {"lat": lat, "lon": lon}

    # Ask user how they'd like to use the initial coordinates
    print("\nHow would you like to use the initial coordinates?")
    print("1) As a starting location (won't be included in the polygon).")
    print("2) As Point 1 of the polygon.")
    coordinate_use_choice = input("Enter choice (1/2): ")

    # List to store all computed points
    points = []  # List to store all computed points

    # Depending on the user's choice, determine if the initial coordinates should be used as a monument or as a point in the polygon
    if coordinate_use_choice == "1":
        print("\nDo you want the initial point to be:")
        print("1) A Monument (will become a placemark).")
        print("2) First Point of the Polygon (no placemark).")
        point_use_choice = input("Enter choice (1/2): ")
        if point_use_choice == "1":
            # If user chooses monument, get its label and store it
            monument_label = input("Enter a label for the monument (e.g., Monument, Point A, etc.): ")
            data["monument"] = {"lat": lat, "lon": lon, "label": monument_label}
        elif point_use_choice == "2":
            # If user chooses to use the initial point as the first point of the polygon, store it
            points.append((lat, lon))
            points.append((lat, lon))
            print(f"Point 1: Latitude: {lat:.6f}, Longitude: {lon:.6f}\n")

    # If user chooses to use the initial coordinates as the first point of the polygon, store i            
    elif coordinate_use_choice == "2":
        points.append((lat, lon))
        print(f"Point 1: Latitude: {lat:.6f}, Longitude: {lon:.6f}\n")

    # Prompt user to select the computation method for determining subsequent GPS coordinates
    print("Choose a method:")
    print("Choose a method:")
    print("1) Karney's Method")
    print("2) Vincenty's Method")
    print("3) Spherical Model")
    print("4) Average all models/methods")
    choice = int(input("Enter choice (1/2/3/4): "))

    # Get the number of points user wants to compute
    num_points = int(input("How many points would you like to compute? "))

    # Loop for the number of points the user wants to compute
    for i in range(num_points):  # Loop for the number of points the user wants to compute
        bearing = parse_dd_or_dms()
        if bearing is not None:
            distance = float(input("Enter distance in feet: ").replace(',', ''))

            prev_lat, prev_lon = lat, lon
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

            # Update the monument's location if it exists
            if i == 0 and data["monument"]:
                data["monument"]["lat"] = lat
                data["monument"]["lon"] = lon

             # Store the computed point
            points.append((lat, lon))
            data_point = {
                "lat": lat, "lon": lon,
                "bearing_from_prev": bearing, 
                "distance_from_prev": distance
            }
            data["polygon"].append(data_point)

            # Display the computed point to the user
            print(f"Computed Point {len(points)}: Latitude: {lat:.6f}, Longitude: {lon:.6f}\n")

    # Continuously prompt the user until the polygon is completed or user decides not to add more points
    while True:  # Infinite loop to prompt the user
        if check_polygon_closure(points, (data["monument"]["lat"], data["monument"]["lon"]) if "lat" in data["monument"] else None):
            print("Your polygon is completed.")
            break
        elif is_polygon_close_to_being_closed(points):
            print("Warning: Your polygon is not closed.")
            print("Your polygon is close enough to being closed.")
        else:
            print("Warning: Your polygon is not closed.")
        
        # Ask user if they want to add more points
        add_point_decision = input("Would you like to enter another point before closing the polygon? (yes/no): ").strip().lower()

        if add_point_decision == 'yes':
            bearing = parse_dd_or_dms()
            if bearing is not None:
                distance = float(input("Enter distance in feet: ").replace(',', ''))

                prev_lat, prev_lon = lat, lon
                # Compute and store new point
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
                data_point = {
                    "lat": lat, "lon": lon,
                    "bearing_from_prev": bearing, 
                    "distance_from_prev": distance
                }
                data["polygon"].append(data_point)
                print(f"Computed Point {len(points)}: Latitude: {lat:.6f}, Longitude: {lon:.6f}\n")

        elif add_point_decision == 'no':
            break
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")

    # Check one last time if the polygon is closed
    if not check_polygon_closure(points, (data["monument"]["lat"], data["monument"]["lon"]) if "lat" in data["monument"] else None):
        print("Warning: Your polygon is not closed.")

     # Prompt user if they want to export the data                                                
    export_choice = input("Do you want to export the polygon to a KML file or Data File? (yes/no): ")
    if export_choice.lower() == 'yes':
        file_type_choice = input("Would you like to save a (K)ML, (D)ata File or (B)oth? ").upper()
        
        if file_type_choice in ["K", "B"]:
            kml_polygon = generate_kml_polygon(points, color="#3300FF00")
            kml_content = kml_polygon  # default to just the polygon

            # Save as KML file if chosen
            if "label" in data.get("monument", {}):  # check if there's a monument
                kml_placemark = generate_kml_placemark(data["monument"]["lat"], 
                                                    data["monument"]["lon"], 
                                                    name=data["monument"]["label"])
                kml_content = generate_complete_kml(kml_placemark, kml_polygon)

            save_kml_to_file(kml_content)

        # Add a placemark if a monument exists
        if file_type_choice in ["D", "B"]:
            save_data_to_file(data, (initial_lat, initial_lon))

    return data  # returning data for inspection purposes


if __name__ == "__main__":
    main()

