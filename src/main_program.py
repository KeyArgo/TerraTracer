# Local module imports
from processes import create_kml_process

def main():
    """
    Main function to run the program. It prompts the user to input initial coordinates, choose computation methods,
    and compute subsequent GPS points to form a polygon. It also offers the ability to export the results to KML or data files.
    
    Returns:
    - dict: A dictionary containing initial coordinates, monument details (if any), and polygon points.
    """

    # Execute the main process
    data = create_kml_process()



if __name__ == "__main__":
    main()