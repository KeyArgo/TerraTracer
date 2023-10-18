# TerraTracer

TerraTracer is a versatile geolocation tool designed to calculate precise coordinates based on user-defined starting points, bearings, and distances. Whether you're a hiker, land mapper, drone enthusiast, rockhound, or just need to pinpoint a location, TerraTracer offers accurate location data tailored to your needs.

## Introduction

TerraTracer simplifies geolocation by providing various methods for calculating coordinates. Choose the method that suits your needs for accurate results.

## Geolocation Methods and Accuracy

Choose from multiple geolocation methods:

### Spherical Model:

* **Explanation**: Approximates Earth as a perfect sphere. Uses trigonometric equations to calculate new latitude and longitude.
* **Pros**: Fast and computationally less intensive.
* **Cons**: Less accurate over long distances due to Earth's oblate spheroid shape.

### Vincenty's Method:

* **Explanation**: Uses ellipsoidal surface equations. Accounts for Earth's flattening for higher accuracy.
* **Pros**: More accurate over most locations, especially long distances.
* **Cons**: Might not converge near the poles.

### Karney's Method:

* **Explanation**: An enhanced method over Vincenty's. Uses a series expansion for calculations.
* **Pros**: Faster, more accurate, and always converges.
* **Cons**: More computationally intensive than the spherical model.

### Average Methods:

* **Explanation**: Averages coordinates from all three methods for a potentially balanced result.
* **Pros**: Might mitigate individual method limitations.
* **Cons**: No guarantee of improved accuracy in all scenarios.

For everyday use, consider using the Spherical Model, while Vincenty's and Karney's Methods are suitable for professional applications.

## Installation

### Prerequisites

Ensure you have the following libraries installed:

* geopy
* geographiclib

You can install them using pip:

```bash
pip install geopy geographiclib
```

### Steps

1. Clone the repository:

```bash
git clone https://github.com/KeyArgo/TerraTracer.git
```

2. Navigate to the directory:

```bash
cd TerraTracer
```

## Usage

Run TerraTracer:

```bash
python TerraTracer_v0.1.py
```

Follow on-screen prompts to input starting coordinates, choose the geolocation method, and specify points.

TerraTracer will display the calculated coordinates for each point.

## Features

* Multiple geolocation methods: Karney's, Vincenty's, and Spherical.
* Option to average all methods for diverse accuracy.
* Intuitive interface and prompts.
* Versatility for a range of outdoor and planning needs.

## Contributing

Contributions to TerraTracer are welcome! Here's how you can get started:

* Open an issue to report bugs or suggest enhancements.
* Submit a pull request with your code contributions.

Please check our Contribution Guidelines for more details.

## License

TerraTracer is licensed under the MIT License.
