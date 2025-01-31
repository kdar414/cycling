**Segmentation**
- Issue with converting segment GDF to graph which appears to affect the GetSegsAlongTrack code
- The GDF to graph has issues renamin the index 'osmid'
- Trying to use osmid column and maybe set that as index or key.

<ins>SEG_GDF_GRAPH</ins>
- nodes have tuples (long/lat) representing location
- edges connecting pairs of nodes and each edge is represented by a tuple ((start_node_coordinates), (end_node_coordinates), distance). Edge contains geometry, seg_id, seg_uid, seg_length, osmid, length.
- Error seems to stem from all_sps being an empty list in GetSegsAlongTrack so there may be an error with nearest node identigication, path generation or graph structure.
- Adjusting the data to include more than the midpoint, have included all the ngapipi test data to eliminate this as a potential cause of the error.
- *Going back to square one*: using the original GetSegsAlongTrack function with ngapipi road and segment_gdf.
- First error is
```
Key error : ['x']
```
- Need to direct the code to 'match_xy_tuple' [line 12]
- there are then an error of must pass list_like as 'names'. Error is from ox.nearest_node and how nodes are processed by osmnx, specifically with renaming the index of the node.
- Checked that all of the nodes are valid coordinates and they are
- Checking the projection, all EPSG:4326
- The error message pins the error to gdf_nodes.index = gdf_nodes.index.rename("osmid") trying to check if the index is multi or single level.
- Asked at **hacky hour slack** and they said that it is a multi level index and provided an alternative.

- This is what I am using now for those two functions
```
def SegGDFToGraph(segments_gdf: gpd.GeoDataFrame):
   
    seg_graph = mp.gdf_to_nx(segments_gdf)
    seg_graph.graph['crs'] = 'epsg:4326'
    
    for node in seg_graph.nodes(data=True):
        node[1]['x'] = node[0][0]
        node[1]['y'] = node[0][1]
        
    seg_graph = nx.convert_node_labels_to_integers(seg_graph)
    
    return seg_graph.to_undirected()


SEG_GDF_GRAPH = SegGDFToGraph(Segment_gdf)
```

Then

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


segments_along_track = GetSegsAlongTracks(ngapipi_data, SEG_GDF_GRAPH)
```

- At the moment there is an output of:
```
Path could not be found between nodes 1738 and 0
Path could not be found between nodes 0 and 1748
Path could not be found between nodes 1748 and 44
```
![problematic nodes](https://github.com/user-attachments/assets/b553734b-8c28-4898-8e10-82d747217326)
![download (1)](https://github.com/user-attachments/assets/2dfd391d-aabc-4a32-8124-f46817526bcb)

- Have moved onto topological segmentation - the function appears to work at the moment
![download (2)](https://github.com/user-attachments/assets/cd4b9f4c-80d6-446a-b7d3-f33aec0c501d)
![download (3)](https://github.com/user-attachments/assets/d0b33e42-1a02-425e-8081-72b0a5e4d697)
![download (4)](https://github.com/user-attachments/assets/a258c2de-ad36-40d4-82a6-fe23efcdae5f)


