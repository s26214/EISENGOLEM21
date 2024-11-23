import json
import random
import numpy as np
from poliastro.bodies import Earth
from poliastro.twobody import Orbit
from astropy import units as u
from astropy.time import Time

# Constants
NUM_DEBRIS = 100  # Number of debris objects
SIMULATION_TIME_SPAN = 24 * 3600  # 24 hours in seconds
STEP_SIZE = 60  # Time step in seconds (1 minute for smoother motion)
SEED = 42  # Random seed for reproducibility

# Set random seed for reproducibility
random.seed(SEED)

def generate_random_orbit():
    """Generate a random orbit for a debris object."""
    a = random.uniform(7000, 7500) * u.km  # Semi-major axis
    ecc = random.uniform(0.0, 0.1) * u.one  # Eccentricity
    inc = random.uniform(0, 180) * u.deg  # Inclination
    raan = random.uniform(0, 360) * u.deg  # RAAN
    argp = random.uniform(0, 360) * u.deg  # Argument of Periapsis
    nu = random.uniform(0, 360) * u.deg  # True anomaly
    return Orbit.from_classical(Earth, a, ecc, inc, raan, argp, nu)

def propagate_orbit(orbit, timespan, step):
    """Propagate orbit and return CZML-compatible positions over time."""
    time_intervals = np.arange(0, timespan, step) * u.s
    positions = []
    epoch = Time.now()
    for dt in time_intervals:
        state = orbit.propagate(dt)
        cartesian = state.rv()[0]  # Get Cartesian position
        positions.append({
            "time": (epoch + dt).isot,
            "position": cartesian.to_value(u.m).tolist()
        })
    return epoch.isot, positions

# Construct CZML
czml = []

# Add document packet (required for CZML files)
czml.append({
    "id": "document",
    "name": "Debris Simulation",
    "version": "1.0",
})
satellite_orbit = Orbit.from_classical(
    Earth,
    7000 * u.km,  # Semi-major axis
    0.01 * u.one,  # Eccentricity
    45 * u.deg,  # Inclination
    0 * u.deg,  # RAAN
    0 * u.deg,  
    0 * u.deg,  
)
satellite_epoch, satellite_positions_with_time = propagate_orbit(
    satellite_orbit, SIMULATION_TIME_SPAN, STEP_SIZE
)

# Convert satellite positions to CZML-compatible format
satellite_cartesian_positions = []
for pos in satellite_positions_with_time:
    time_offset = (Time(pos["time"]) - Time(satellite_epoch)).sec /10
    satellite_cartesian_positions.extend([time_offset] + pos["position"])

# Create a satellite packet
satellite_packet = {
    "id": "Satellite-1",
    "position": {
        "interpolationAlgorithm": "LAGRANGE",
        "interpolationDegree": 5,
        "referenceFrame": "INERTIAL",
        "epoch": satellite_epoch,
        "cartesian": satellite_cartesian_positions,
    },
    "label": {
            "text": f"Satelite",
            "font": "12pt Helvetica",
            "fillColor": {"rgba": [255, 255, 255, 255]},  # White text
            "outlineColor": {"rgba": [0, 0, 0, 255]},  # Black outline
            "outlineWidth": 2,
            "show": True,
            "horizontalOrigin": "CENTER",
            "verticalOrigin": "BOTTOM",
            "pixelOffset": {"cartesian2": [0, -20]},  # Offset label below object
        },
    "path": {
        "show": True,
        "leadTime": 0,
        "trailTime": SIMULATION_TIME_SPAN,
        "width": 2,
        "material": {
            "solidColor": {
                "color": {"rgba": [255, 0, 0, 255]}  # Red line
            }
        }
    }
}
czml.append(satellite_packet)

# Generate debris packets
for i in range(NUM_DEBRIS):
    orbit = generate_random_orbit()

    speed_factor = random.uniform(0.5, 2.0)  # Speeds between 0.5x and 2.0x normal speed

    epoch, positions_with_time = propagate_orbit(orbit, SIMULATION_TIME_SPAN, STEP_SIZE/speed_factor)
    
    # Convert positions to CZML-compatible format
    cartesian_positions = []
    for pos in positions_with_time:
        time_offset = (Time(pos["time"]) - Time(epoch)).sec / 10
        cartesian_positions.extend([time_offset] + pos["position"])

    # Create a debris packet
    debris_packet = {
        "id": f"{i}",
        "position": {
            "interpolationAlgorithm": "LAGRANGE",
            "interpolationDegree": 5,
            "referenceFrame": "INERTIAL",
            "epoch": epoch,
            "cartesian": cartesian_positions,
        },
        "label": {
            "text": f"{i}",
            "font": "12pt Helvetica",
            "fillColor": {"rgba": [255, 255, 255, 255]},  # White text
            "outlineColor": {"rgba": [0, 0, 0, 255]},  # Black outline
            "outlineWidth": 2,
            "show": True,
            "horizontalOrigin": "CENTER",
            "verticalOrigin": "BOTTOM",
            "pixelOffset": {"cartesian2": [0, -20]},  # Offset label below object
        },
        "model": {
            "gltf": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/main/2.0/AnimatedCube/glTF/AnimatedCube.gltf",
            "scale": 0.5,  # Adjust to make the object smaller
            "minimumPixelSize": 32,
            "maximumScale": 200,
            "show": True
        },
    }
    czml.append(debris_packet)

# Write CZML to file
output_file = "czml_data/simple.czml"
with open(output_file, "w") as f:
    json.dump(czml, f, indent=2)  # Serialize the document

print(f"CZML file saved to {output_file}.")
