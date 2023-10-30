"""
main_program.py

Entry point to the program. It calls the necessary functions from processes.py 
to execute the main workflow.
"""

# Local module imports
from processes import create_kml_process

def main():
    """
    Main function that provides a menu for the user to interact with the program.
    """
    while True:
        print("\n#########################")
        print("###    TerraTracer    ###")
        print("#########################")
        
        print("\n1. Create Custom Geometric Shapes")
        print("   - Create mining claims based on land certificates.")
        print("   - Delineate property boundaries, agricultural fields, etc.")
        print("   - Create artful shapes: stars, triangles, hexagons, intricate patterns, and more.")
        print("   - Designate specific zones or areas for urban planning or environmental conservation.")
        
        print("\n2. Convert JSON File to KML - COMING SOON")
        print("   - Convert a previously saved JSON data file into a KML format for visualization in tools like Google Earth.")
        
        print("\n3. Exit")
        print("   - Terminate the program.")
        
        choice = input("\n\nEnter your choice (1/2/3): ")
        
        if choice == "1":
            # Call the function to create a new polygon
            create_polygon_process()
        elif choice == "2":
            # Call the function to convert a TZT file to KML
            convert_tzt_to_kml()
        elif choice == "3":
            print("\nExiting program. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please select a valid option.")

def create_polygon_process():
    """
    Function to run the create polygon process. It prompts the user to input initial coordinates, choose computation methods,
    and compute subsequent GPS points to form a polygon. It also offers the ability to export the results to KML or data files.
    
    Returns:
    - dict: A dictionary containing initial coordinates, monument details (if any), and polygon points.
    """
    return create_kml_process()

def get_tzt_filepath():
    return input("Please enter the path to the TZT file you want to convert: ")

def convert_tzt_to_kml():
    # Placeholder function for now, until you implement the TZT to KML conversion
    print("This feature is not yet implemented.")
    pass

if __name__ == "__main__":
    main()
