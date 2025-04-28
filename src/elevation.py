import rasterio
import os
import pandas as pd
import numpy as np

# return a pandaframe, with dist_m as the distance from start and 'elevation the elevation at that distance from start
def get_elevation_profile(bisse_line, dem_folder="data/swissALTI3D", num_points=600, smooth=True):
    points, distances = interpolate_points(bisse_line, num_points=num_points)  

    # * this can be optimised
    dem_lookup = build_dem_lookup(dem_folder)
    # Extract elevation for each point using the lookup table
    elevations = [get_elevation(p, dem_lookup) for p in points]
    if smooth:
        elevations = smooth_moving_avg_and_force_down(elevations, window=9)
    # dictionary of lists 
    dict_profile = {'dist_m': distances, 'elevation': elevations} 
    
    return pd.DataFrame(dict_profile)

def smooth_moving_avg_and_force_down(elev, window=5):
    smooth = pd.Series(elev).rolling(window=window, center=True, min_periods=1).mean()
    for i in range(1, len(smooth)):
        if smooth[i] > smooth[i - 1]:
            smooth[i] = smooth[i - 1]
    return smooth.values

# Function to generate equidistant points along the line
def interpolate_points(line, num_points=100):
    distances = np.linspace(0, line.length, num_points)
    points = [line.interpolate(d) for d in distances]
    return points, distances  # Also return distances

# Step 1: Build a lookup table for DEM tile bounds
def build_dem_lookup(dem_folder):
    lookup = {}
    dem_files = [os.path.join(dem_folder, f) for f in os.listdir(dem_folder) if f.endswith('.tif')]
    
    for dem_path in dem_files:
        with rasterio.open(dem_path) as src:
            bounds = src.bounds  # Get (left, bottom, right, top)
            lookup[(bounds.left, bounds.bottom, bounds.right, bounds.top)] = dem_path

    return lookup


# Step 2: Function to find the correct DEM tile using the lookup table
def get_dem_file(point, lookup):
    """Returns the correct DEM file for a given point based on precomputed bounds."""
    x, y = float(point.x), float(point.y)
    for (left, bottom, right, top), filepath in lookup.items():
        #print(left, bottom, right, top)
        if left <= x <= right and bottom <= y <= top:
            return filepath
    print('will return non')
    return None  # Return None if no DEM tile contains the point

# Step 3: Function to extract elevation from the correct DEM file
# * could be optimised when grouping all points of one tile
def get_elevation(point, lookup):
    """Finds the correct DEM tile using the lookup table and extracts elevation."""
    dem_file = get_dem_file(point, lookup)
    if dem_file:
        with rasterio.open(dem_file) as src:
            return list(src.sample([(point.x, point.y)]))[0][0]
    return np.nan  # Return NaN if no valid DEM file is found
