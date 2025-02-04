- Working on segmentation - I have added the segment group using the shared number before the hyphen in seg_uid. This has fixed this error but the final code GetRideSegsGDF is producing an empty data frame.
- This is the fix for seg_group and it is present in Segment_gdf
```
# Segment GeoDataFrame From Graph
# THIS ONLY WORKS ON THE SEGMENTED GRAPH, NOT THE GRAPH PRODUCED FROM SEGMENTS
# creates geodataframe of segments from a (spatially segmented) networkx graph
def SegGDFFromGraph(graph:nx.MultiDiGraph):
    rows = []
    for index, (u, v, data) in enumerate(tqdm(graph.edges(data=True))):
        for start_xy, end_xy, seg_id, seg_uid, length in data['segments']:
            # Extract segment group from seg_uid (e.g., '2-0' -> group 2)
            seg_group = seg_uid.split('-')[0]  # The first part before the '-'
            
            # Append the relevant information into rows
            rows.append({
                "geometry": LineString([Point(start_xy), Point(end_xy)]),
                "seg_id": seg_id,
                "seg_uid": seg_uid,
                "seg_group": seg_group,  # Store the segment group
                "seg_length": length,
                "osmid": data["osmid"]
            })
    
    # Create GeoDataFrame from the rows with the correct CRS
    gdf = gpd.GeoDataFrame(rows, crs=4326)
    return gdf

# Generate the GeoDataFrame from the segmented graph
Segment_gdf = SegGDFFromGraph(graph=Ordered_seg_graph)

```
![Screen Shot 2025-02-05 at 10 01 48](https://github.com/user-attachments/assets/b1cb6ff5-cd60-47b5-84a9-0fddf51cf0a3)


- I am trying with Maike's data to see if the issue is just with unconnected nodes in the test data. 
