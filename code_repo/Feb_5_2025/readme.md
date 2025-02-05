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


- I am trying with Maike's data to see if the issue is just with unconnected nodes in the test data. Hitting issues here with the structure of the dictionary when the df is converted to a dictionary.
- Ok so I think I have made some progress with the last two functions
```
def GetSegsAlongTracks(tracks: dict, graph: nx.Graph, max_pathlength: int = 10, remove_duplicates: bool = True,
                       debug: bool = True, filter_isolate_branches: bool = True):
    track_segs = defaultdict(dict)

    # Reload the ox module to ensure any updates are reflected
    import importlib
    importlib.reload(ox)
    
    for filename, track in tracks.items():
        # Extract coordinates from the 'filter_xy_tuple' or 'match_xy_tuple'
        # Assuming you want to use 'filter_xy_tuple'
        coords = track['match_xy_tuple']
        
        # Get nearest nodes for each point in the track
        nn = [ox.nearest_nodes(graph, x, y) for x, y in coords]  # Extract x and y from each tuple
        
        all_sps = []
        end_points = []
        for i, n in enumerate(nn):
            if 0 < i < len(nn) - 1:
                try:
                    sp = nx.shortest_path(graph, n, nn[i + 1])
                    if len(sp) <= max_pathlength:
                        all_sps.extend(sp)
                    else:
                        end_points.append(nn[i + 1])
                except nx.NetworkXNoPath:
                    if debug:
                        print(f'Path could not be found between nodes {n} and {nn[i + 1]}')

        # Remove duplicated nodes in paths
        if remove_duplicates:
            all_sps = list(dict.fromkeys(all_sps))

        track_segs[filename]['sp_list'] = all_sps
        track_segs[filename]['sp_graph'] = nx.MultiGraph(graph.subgraph(all_sps))
        track_segs[filename]['end_points'] = end_points

        if filter_isolate_branches:
            nodes_to_rm = []
            for u, v, data in list(track_segs[filename]['sp_graph'].edges(data=True)):
                if track_segs[filename]['sp_graph'].degree(u) == 1:
                    if track_segs[filename]['sp_graph'].degree(v) > 2:
                        nodes_to_rm.append(u)

                if track_segs[filename]['sp_graph'].degree(v) == 1:
                    if track_segs[filename]['sp_graph'].degree(u) > 2:
                        nodes_to_rm.append(v)

            track_segs[filename]['sp_graph'].remove_nodes_from(nodes_to_rm)

    return track_segs


#segments_along_track2 = GetSegsAlongTracks(ngapipi_data, SEG_GDF_GRAPH)

# get the segments along a ride, given a matched GPX and a graph of the entire network
def GetRideSegsGDF(matched_gdf, matched_filename, network_graph, seg_multi_gdf, 
                   max_pathlength=40, group_attr='seg_group', multipart=True):
     
    track_segs = GetSegsAlongTracks({matched_filename: matched_gdf}, network_graph, max_pathlength)

    track_segs_graph = track_segs[matched_filename]['sp_graph']  # get shortest path graph

    # extract ids of segments passed along track, using the data of the shortest path graph
    track_seg_ids = [i[2][group_attr] for i in track_segs_graph.edges(data=True)]

    # get a geodataframe of the segments passed along the track
    track_segs_mp = seg_multi_gdf[seg_multi_gdf[group_attr].isin(track_seg_ids)]

    return track_segs_mp.reset_index(drop=True)

ride_segments = GetRideSegsGDF(ngapipi_gdf,'match_xy_tuple',SEG_GDF_GRAPH,Segment_gdf)
```
- This produces a gdf which is very similar to segment_gdf but it is called ride_segments
- The output (for the ngapipi data) is
![Screen Shot 2025-02-05 at 14 13 27](https://github.com/user-attachments/assets/ed4aadd8-9bc5-4d0c-8d29-93526902b76d)
