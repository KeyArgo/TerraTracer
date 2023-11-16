## Alpha Stage Notice
**Please note:** TerraTracer is currently in its alpha stages of development. This means the software is still under active development and may contain bugs. We are aware of these issues and are actively working to resolve them. Users are encouraged to provide feedback and report any issues, as this will greatly aid in the development process and help us move towards a stable release.

# TerraTracer: Streamlined Geospatial Mapping & Claim Staking

## About TerraTracer

TerraTracer is a powerful and versatile geolocation tool that empowers users to calculate precise coordinates with ease. It's designed to cater to a wide array of geospatial needs - from hikers mapping their trails, land mappers outlining property boundaries, drone enthusiasts plotting flight paths, to rockhounds marking their finds, or anyone in need of pinpointing a specific location.

With TerraTracer, you can create custom geometric polygons, define individual placemarks based on coordinate inputs, and even convert your data to KML for visualization in applications like Google Earth. Its intuitive interface and robust backend ensure that your geolocation data is both accurate and useful for a variety of applications.

## Features

- **Custom Geometric Polygons**: Create shapes and patterns, delineate boundaries, and designate zones for various planning purposes.
- **Placemark Creation**: Input coordinates to define and mark specific points of interest on the map.
- **KML Conversion**: Transform your JSON-formatted geolocation data into KML files for use with mapping tools.
- **User-Friendly Interface**: Navigate through the functionality of the program with an easy-to-use menu system.
- **Versatile Application**: Whether for professional land surveying or personal outdoor activities, TerraTracer is adaptable to suit your requirements.

## Getting Started

### Prerequisites

To use TerraTracer, you'll need to have Python installed on your system. TerraTracer is built to run with Python 3.6 or higher.

### Installation

1. **Clone the repository**

   Start by cloning the TerraTracer repository to your local machine using:

```bash
   git clone https://github.com/KeyArgo/TerraTracer.git
   cd TerraTracer
```

2. **Install dependencies**
    
    TerraTracer relies on a few external libraries to function correctly. You can install these using the provided `requirements.txt` file:
    
    ```bash
    pip install -r requirements.txt
    ```
    

### Usage

To start using TerraTracer, run the `main_program.py` script in your terminal:

```bash
python main_program.py
```

Follow the on-screen prompts to select the operation you wish to perform. You can create polygons, placemarks, or convert JSON data to KML format.

### Example

After running TerraTracer, you might see a menu like this:

```markdown
#########################
      TerraTracer       
#########################

1. Create Custom Geometric Polygons
   - Create mining claims based on land certificates.

2. Create Placemarks
   - Define individual placemarks based on coordinate inputs.

3. Convert JSON File to KML - COMING SOON
   - Convert a previously saved JSON data file into a KML format for visualization in tools like Google Earth.

X. Exit
   - Terminate the program.
```

Simply enter your choice and follow the subsequent prompts to carry out your geolocation tasks.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.
