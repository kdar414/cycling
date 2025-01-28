**Segmentation**
*ORDERED_SEG_GRAPH*
- This is a plot of the ordered_seg_graph: just to visualise the information in it
```
import folium
import networkx as nx
from shapely.geometry import LineString, Point

# Assuming your graph is stored in `G` (a NetworkX graph)
# And your graph uses 'geometry' attributes for edges

# Get the center of the graph to initialize the map
nodes = [data for _, data in Ordered_seg_graph.nodes(data=True)]
longitudes = [data['x'] for data in nodes]
latitudes = [data['y'] for data in nodes]
map_center = [sum(latitudes) / len(latitudes), sum(longitudes) / len(longitudes)]

# Create a Folium map
m = folium.Map(location=map_center, zoom_start=15, tiles="cartodbpositron")

# Plot edges
for u, v, data in Ordered_seg_graph.edges(data=True):
    if 'geometry' in data:  # If edge has a geometry attribute
        line = data['geometry']
        if isinstance(line, LineString):
            coords = [(y, x) for x, y in line.coords]  # Flip to lat/lon for Folium
            folium.PolyLine(coords, color="blue", weight=2).add_to(m)

# Plot nodes
for node, data in Ordered_seg_graph.nodes(data=True):
    folium.CircleMarker(
        location=(data['y'], data['x']),  # Latitude, Longitude
        radius=3,
        color="red",
        fill=True,
        fill_color="red",
        tooltip=f"Node: {node}"
    ).add_to(m)

# Display the map
m
```

- Testing out the code from hacky hour
```
# Segment GeoDataFrame From Graph
# THIS ONLY WORKS ON THE SEGMENTED GRAPH, NOT THE GRAPH PRODUCED FROM SEGMENTS
# creates geodataframe of segments from a (spatially segmented) networkx graph
from tqdm.auto import tqdm

def SegGDFFromGraph(graph:nx.MultiDiGraph):
    rows = []
    for index, (u, v, data) in enumerate(tqdm(graph.edges(data=True))):
        for start_xy, end_xy, seg_id, seg_uid, length in data['segments']:
            rows.append({
                "geometry": LineString([Point(start_xy), Point(end_xy)]),
                "seg_id": seg_id,
                "seg_uid": seg_uid,
                "seg_length": length
            })
    gdf = gpd.GeoDataFrame(rows, crs=4326)
    return gdf

Segment_gdf = SegGDFFromGraph(graph = Ordered_seg_graph)
```
- This produces gdf of 446769 rows x 4 columns (see below).
  
![Screen Shot 2025-01-29 at 08 29 49](https://github.com/user-attachments/assets/3939315f-540d-4880-805f-1841d9dc2adc)

