# #sudo docker run -t -i -p 5000:5000 -v "/Users/kad/osrm-docker:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/new-zealand-latest.osrm --max-matching-size 20000
# %%
import requests
import folium
from folium import GeoJson
import numpy as np
import pandas as pd
#%%
gps = pd.read_csv('/Users/kad/Desktop/cyclists/chloes_files/Trips with data/Maike/23-11-2023/mgat-Uoa-TamakiDrive-Uoa_23-11-2023-gps_1.csv')
gps_cleaned = gps.dropna(axis=1)  #removing columns with NA
coordinates_gps = gps_cleaned[["LONGITUDE","LATITUDE"]].apply(tuple, axis=1)
coordinates_gps.to_numpy()
string = coordinates_gps.to_string()


# %%
# Coordinates (11 coordinates)

coordinates = ';'.join(f"{row['LONGITUDE']},{row['LATITUDE']}" for _, row in gps.iterrows())
#coordinates = "174.7685883,-36.8540765;174.768555,-36.8540118;174.7685912,-36.8540347;174.7685877,-36.8540245;174.7685877,-36.8540245;174.7685941,-36.8540278;174.7686042,-36.8540396;174.7685711,-36.8540424;174.7685698,-36.8540486;174.7685706,-36.8540635;174.768553,-36.8540589;174.7685624,-36.8540776"


# Set radiuses for each coordinate (same radius for all coordinates, repeated 11 times)
length_of_df = len(gps)
radiuses2 = ';'.join(['50'] * length_of_df)

#radiuses2 = "50;50;50;50;50;50;50;50;50;50;50;50"

params = {
    "steps": "true",              # Request steps
    "geometries": "geojson",      # Request geometry in GeoJSON
    "radiuses": radiuses2         # radius currently set to default which is 5 m
}

# Construct the full URL with the coordinates and parameters
url = "http://127.0.0.1:5000/match/v1/bicycle"
full_url = f"{url}/{coordinates}"

# Make the GET request
response = requests.get(full_url, params=params)

# Check if the response is successful
if response.status_code == 200:
    route_data = response.json()

    # Check if there are matchings in the response
    if "matchings" in route_data and route_data["matchings"]:
        # Extract route geometry (coordinates)
        route_geometry = route_data["matchings"][0]["geometry"]["coordinates"]
        
        # Create a folium map centered around the first coordinate
        map_center = [route_geometry[0][1], route_geometry[0][0]]  # [lat, lon]
        m = folium.Map(location=map_center, zoom_start=15)
        
        # Add the route geometry to the map as GeoJSON
        folium.GeoJson(route_data["matchings"][0]["geometry"]).add_to(m)
        
        # If there are steps, you can add them to the map as well
        if "legs" in route_data["matchings"][0]:
            for step in route_data["matchings"][0]["legs"][0]["steps"]:
                # Each step is a dictionary, we can extract the location from the step
                step_location = step.get("location")
                if step_location:
                    folium.Marker([step_location[1], step_location[0]], 
                                  popup=step.get("instruction")).add_to(m)

        # Save the map as an HTML file
        m.save("/Users/kad/osrm-docker/route_map_osrm_docker_50.html")
        print("Map has been saved as 'route_map_100.html'.")
    else:
        print("No matchings found in the response.")
else:
    print(f"Request failed with status code {response.status_code}")
    print(f"Response content: {response.text}")


print(route_data)
# %%
route_geometry_df = pd.DataFrame(route_geometry)


# Convert to the required format (list of tuples: [(lon1, lat1), (lon2, lat2), ...])
filter_xy_tuple = [(coord[0], coord[1]) for coord in route_geometry]

# Create the single_track dictionary
single_track = {"filter_xy_tuple": filter_xy_tuple}

# Print or use the single_track dictionary
print("Formatted single_track:", single_track)




# %%
import json

# Save single_track to a JSON file
with open("/Users/kad/osrm-docker/Maike_23_11_23_single_track.json", "w") as json_file:
    json.dump(single_track, json_file)

# %%
