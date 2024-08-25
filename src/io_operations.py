"""
io_operations.py

Handles input/output operations for the program. It prompts the user for inputs
and handles user choices related to the main workflow.
"""


from utils import (get_coordinate_in_dd_or_dms, parse_dd_or_dms)


def gather_tie_point_coordinates():
    """
    Gather initial coordinates (Tie Point) from the user.

    This function prompts the user to enter the initial coordinates, also known as the Tie Point, 
    which serves as a starting reference for further operations in the application. 
    The user can choose between different coordinate formats or exit to the main menu.

    Returns:
    - tuple: The latitude and longitude of the Tie Point, or None if the user chooses to exit.
    Note: The Tie Point is crucial as it sets the reference for all subsequent geographical calculations.
    """
    # Prompt user for preferred coordinate format
    coordinate_format = get_tie_point_coordinate_format()
    
    if coordinate_format == "1":    # Handling Decimal Degrees format
        # Get latitude in Decimal Degrees; return None if user exits
        lat = get_coordinate_in_dd_or_dms(coordinate_format, "latitude")
        if lat is None:  # User chose to exit
            return None, None
        # Get longitude in Decimal Degrees; return None if user exits
        lon = get_coordinate_in_dd_or_dms(coordinate_format, "longitude")
        if lon is None:  # User chose to exit
            return None, None

    elif coordinate_format == "2":  # Handling Degrees, Minutes, and Seconds format
        # Similar handling for DMS format goes here
        lat = get_coordinate_in_dd_or_dms(coordinate_format, "latitude")
        if lat is None:  # User chose to exit
            return None, None
        lon = get_coordinate_in_dd_or_dms(coordinate_format, "longitude")
        if lon is None:  # User chose to exit
            return None, None

    elif coordinate_format == "3":  # Exit to Main Menu
        return None, None

    else:
        # Handle invalid choice and return to main menu
        print("Invalid choice. Returning to main menu.")
        return None, None
    
    # Return the gathered latitude and longitude
    return lat, lon


def get_coordinate_format_only():
    """
    Prompt the user to select a coordinate format for entering coordinates.

    This function provides the user with options to choose the format for entering coordinates,
    including Decimal Degrees (DD) and Degrees, Minutes, and Seconds (DMS).

    Returns:
    - str: The chosen coordinate format by the user.
    """
    while True:
        # Continuously prompt user until a valid format choice is made
        # Displaying coordinate format options to the user
        print("\n\n\n------------- Polygon Point Coordinate Format Selection------------- ")
        print("___________________________________________________________________________________")
        print("\nChoose the coordinate format for your Polygon, which serves as the description")
        # Additional print statements explaining the significance of each format
        print("for plotting your polygon using Metes and Bounds. This method involves")
        print("sequential bearings and distances or azimuths to outline the polygon or")
        print("to define a central monument as a reference for construction.")
        print("\nSelect DD (Decimal Degrees) for a straightforward angle measurement")
        print("ranging from 0° to 360°, ideal for azimuths.")
        print("\nSelect DMS (Degrees Minutes Seconds) For traditional directional bearings")
        print("(ie: South 45° 03' 12\" East').")
        print("\nPlease ensure the chosen format aligns with your source data for accuracy.")
        print("___________________________________________________________________________________")
        print("1. Decimal Degrees (DD)")
        print("2. Degrees, Minutes, Seconds (DMS)")
        print("3. Exit to Main Menu")
        choice = input("Enter your choice (1/2/3): ")  # User input for coordinate format choice
        # Validate and return the user's choice
        if choice in ["1", "2", "3"]:
            return choice
        print("Invalid choice. Please enter 1, 2 or 3.")


def get_tie_point_coordinate_format():
    """
    Ask the user to specify the coordinate format for the tie point.

    The tie point serves as the initial reference for plotting polygons using Metes and Bounds. 
    This function guides the user to choose between Decimal Degrees (DD) and Degrees, Minutes, and Seconds (DMS).
    Returns the user's choice as a string ("1" for DD, "2" for DMS).
    """
    
    # Displaying tie point coordinate format options to the user
    print("\n\n\n--------------- Tie Point Coordinate Format Selection ---------------")
    print("_____________________________________________________________________")
    print("\nChoose the format for your Tie Point, which serves as the initial reference")
    # Additional print statements explaining the significance of each format
    print("for plotting your polygon using Metes and Bounds. This method involves")
    print("sequential bearings and distances or azimuths to outline the polygon or")
    print("to define a central monument as a reference for construction.")
    print("\nSelect DD (Decimal Degrees) for a straightforward angle measurement")
    print("ranging from 0° to 360°, ideal for azimuths. For traditional directional")
    print("bearings such as 'South 45° 03' 12\" East', opt for DMS (Degrees Minutes Seconds).")
    print("\nPlease ensure the chosen format aligns with your source data for accuracy.")
    print("_____________________________________________________________________")
    
    # Capturing user input for Tie Point coordinates format
    choice = input("Enter Tie Point coordinates format (1 for DD, 2 for DMS, 3 for Main Menu): ")
    while choice not in ["1", "2", "3"]:
        print("Invalid choice. Please select 1 for DD, 2 for DMS or 3 for Main Menu.")
        choice = input("Enter Tie Point coordinates format (1 for DD, 2 for DMS, 3 for Main Menu): ")
    return choice


def get_no_tie_point_coordinates():
    """
    Prompt the user to specify and input the starting coordinates for the initial point of the polygon
    without using a tie point. 

    The user can input in either Decimal Degrees (DD) or Degrees, Minutes, Seconds (DMS). 
    This is crucial for establishing the initial reference point of the polygon in the absence of a tie point.
    Returns:
    - tuple: The coordinates in decimal degrees as a tuple (latitude, longitude), or
             (None, None) if the user decides to exit.
    """

    # Displaying instructions for entering the starting coordinates of the polygon
    print("\n----------------- Initial Polygon Point Coordinates -----------------")
    print("_____________________________________________________________________")
    print("\nPlease enter the starting coordinates for your polygon.")
    # Additional print statements with detailed explanations of each format
    print("Choose the format and enter the coordinates:")
    print("  - Decimal Degrees (DD) e.g., 35.0283° N, 103.2585° W")
    print("  - Degrees, Minutes, Seconds (DMS) e.g., 35° 1' 42.20\" N, 103° 15' 30.65\" W")
    print("This will establish the initial point of your polygon.")
    print("_____________________________________________________________________")

    # Ask for the coordinate format
    coordinate_format_choice = input("Select the coordinate format (1 for DD, 2 for DMS, 'exit' to cancel): ").strip().lower()
    if coordinate_format_choice == 'exit':
        return None, None  # Exit if user chooses to

    # Validate the user's format choice and reprompt if necessary
    while coordinate_format_choice not in ["1", "2"]:
        print("Invalid choice. Please enter '1' for Decimal Degrees, '2' for Degrees, Minutes, Seconds, or 'exit' to cancel.")
        coordinate_format_choice = input("Select the coordinate format (1 for DD, 2 for DMS, 'exit' to cancel): ").strip().lower()
        if coordinate_format_choice == 'exit':
            return None, None  # Exit if user chooses to

    # Prompt for the actual coordinates based on the chosen format
    if coordinate_format_choice == "1":
        # Get Decimal Degrees
        latitude = get_coordinate_in_dd_or_dms("1", "latitude")
        longitude = get_coordinate_in_dd_or_dms("1", "longitude")
    elif coordinate_format_choice == "2":
        # Get Degrees, Minutes, Seconds
        latitude = get_coordinate_in_dd_or_dms("2", "latitude")
        longitude = get_coordinate_in_dd_or_dms("2", "longitude")

    return latitude, longitude


def ask_use_same_format_for_all():
    """
    Prompt the user to decide if they want to use the same coordinate format for all computed points in the application.

    This decision is important for maintaining consistency in the representation of geographic data throughout the application.
    Returns:
    - bool: True if the user wants to use the same format, False otherwise.
    """
    while True:
        # Asking user to decide on using the same format for all points
        decision = input("Do you want to use this format for all computed points? (yes/no): ").strip().lower()
        if decision == 'yes':
            return True  # Return True if user chooses 'yes'
        elif decision == 'no':
            return False  # Return False if user chooses 'no'
        # Handling invalid user input
        print("Invalid choice. Please enter 'yes' or 'no'.")


def get_computation_method():
    """
    Prompt user to select the computation method for determining subsequent GPS coordinates.

    The available methods are:
    1) Karney's Method: Accurate method for geodesic calculations.
    2) Vincenty's Method: Traditional method for calculating distances and bearings.
    3) Spherical Model: Simplified model, less accurate but faster.
    4) Average all models/methods: Combines results from all methods for a balanced approach.
    Returns:
    - int: User's choice of computation method.
    """
    while True:
        try:
            # Displaying computation method choices and handling user input
            print("Choose a method:")
            print("1) Karney's Method")
            print("2) Vincenty's Method")
            print("3) Spherical Model")
            print("4) Average all models/methods")
            choice = int(input("Enter choice (1/2/3/4): "))
            if choice not in [1, 2, 3, 4]:
                raise ValueError("Invalid choice. Please select 1, 2, 3, or 4.")
            return choice  # Return the user's choice
        except ValueError as e:
            # Handling invalid user input
            print(e)


def get_num_points_to_compute():
    """
    Prompt the user to input the number of points to compute for forming a polygon. 
    This function ensures that the number of points entered is appropriate for forming a closed polygon.
    Note: For polygons, an additional point is required to return to the origin, completing the shape.
    For instance, a four-sided polygon (like a square) needs 5 points in total for closure.
    If the initial point serves as a Monument/Placemark, it's not counted in the total number of points.

    Returns:
        int: The number of points the user wishes to compute, excluding the Monument/Placemark if it's used as such.
    """
    while True:
        try:
            num_points = int(input("Enter the number of points to compute for the polygon:\n"
                                   "- Include an extra point for returning to the origin.\n"
                                   "- Exclude the initial point if it's used as a Monument/Placemark.\n"
                                   "- A valid polygon requires at least 4 points (3+1 for the origin).\n\n"
                                   "Number of points: "))
            if num_points >= 3:  # At least 3 points are needed to form a polygon
                return num_points  # Return the number of points
            else:
                # Inform the user if the entered number is less than the minimum required
                print("A polygon must have at least 3 points, excluding the Monument/Placemark. Please enter a valid number.")
        except ValueError:
            # Handle invalid numeric input
            print("Invalid input. Please enter a valid number.")


def get_bearing_and_distance(coordinate_format):
    """
    Prompt the user for bearing and distance based on the given coordinate format.

    This function asks the user to input bearing and distance. The bearing input is parsed
    based on the provided coordinate format (e.g., "DD" for Decimal Degrees). The distance
    is expected in feet and converted to a float. The function handles invalid inputs
    by prompting the user again until valid inputs are received.

    Parameters:
    - coordinate_format (str): The format of the coordinates (e.g., "DD" for Decimal Degrees).

    Returns:
    - tuple: A tuple containing the bearing (in degrees) and distance (in feet),
      or (None, None) if the user chooses to exit.
    """
    while True:
        try:
            bearing = parse_dd_or_dms(coordinate_format)  # Parse bearing based on the coordinate format
            if bearing is None:
                return None, None  # User chooses to exit

            # Prompt for distance in feet and replace any commas for proper float conversion
            distance = float(input("Enter distance in feet: ").replace(',', ''))
            return bearing, distance

        except ValueError as e:
            # Handle invalid input and prompt the user to re-enter values
            print("Invalid input. Please enter valid values for bearing and distance.")
            continue


def get_export_decision():
    """
    Prompt the user to decide whether to export the polygon to a KML file or Data File.

    This function asks the user a yes/no question about exporting the generated polygon.
    The user's response is converted to lowercase and compared to 'yes' to determine the decision.

    Returns:
    - bool: True if the user decides to export (answers 'yes'), False otherwise.
    """
    return input("\n\nDo you want to export the polygon to a KML file or Data File? (yes/no): ").lower() == 'yes'


def get_add_point_decision():
    """
    Prompt the user to decide whether to add more points to the polygon.

    This function asks the user a yes/no question about adding more points to the polygon.
    The user's response is converted to lowercase for consistent comparison.

    Returns:
    - bool: True if the user wants to add more points (answers 'yes'), False otherwise.
    """
    return input("Would you like to enter another point before closing the polygon? (yes/no): ").strip().lower()


def get_file_type_choice():
    """
    Prompt the user to choose a file type for saving data.

    This function asks the user to select between saving data as a KML file, a Data file, 
    a GeoJSON file, or all formats. The user response is converted to uppercase for consistent processing.

    Returns:
    - str: The user's choice as 'K' for KML, 'D' for Data File, 'G' for GeoJSON, or 'B' for All.
    """
    while True:
        choice = input("Would you like to save as (K)ML, (D)ata File, (G)eoJSON, or (A)ll? ").upper()
        if choice in ['K', 'D', 'G', 'A']:
            return choice
        print("Invalid choice. Please enter K, D, G, or A.")


def polygon_main_menu():
    """
    Displays main menu options for geometric polygon creation.

    Offers the user options to start creating a polygon either by specifying a Tie Point or by directly 
    entering the first point's coordinates. The menu also provides an option to return to the main menu. 
    It primarily facilitates the initial step of polygon creation.

    Returns:
        str: The user's selected method for initiating polygon creation.
    """
    print("\n\n\n------------------ Create Custom Geometric Polygon ------------------")
    print("_____________________________________________________________________")
    print("\nThis menu allows you to create a KML or JSON file for polygons")
    print("using common bearings, distances or metes and bounds commonly used")
    print("in land descriptions.  You can begin with a Tie Point or specify a")
    print("set of starting coordinates for your polygon.")
    print("_____________________________________________________________________")
    print("\nChoose an option:")
    print("1) Use a Tie Point")
    print("2) Specify the first point of the polygon (COMING SOON)")
    print("3) Exit to Main Menu")
    return input("Enter your choice (1/2/3): ")


def tie_point_menu():
    """
    Presents options related to using or defining a Tie Point for polygon creation.

    This menu allows the user to decide whether to use the initial point as a Monument/Placemark, 
    find and place the first point of the polygon, or exit to the Main Menu.

    Returns:
    - str: The user's choice regarding the Tie Point.
    """
    print("\nChoose an option:")
    print("1) Use initial point as Monument/Placemark")
    print("2) Find and place the first point of the polygon")
    print("3) Exit to Main Menu")
    choice = input("Enter your choice (1/2/3): ").strip()
    while choice not in ["1", "2", "3"]:
        print("Invalid choice. Please select 1, 2 or 3.")
        choice = input("Enter your choice (1/2/3): ").strip()
    return choice