**Segmentation**
- Everything up to GetSegsAlongTrack appears to be working. Starting today by changing the data source to Maike's Cycle Route 23/11/23 to test code. Using a copy of the notebook called segmentation_30_01_2025-usingcyclingdata to do the testing.
- Code appears to work with the cycling data added.
- Plotted some information about the haversine distances as well


- Struggling with the code below at the moment

```
def GetSegsAlongTracks(tracks:dict, graph:nx.Graph, max_pathlength:int=10, remove_duplicates:bool=True, debug=True,
                        filter_isolate_branches:bool=True):

    track_segs = defaultdict(dict)

    #nns = []
    import importlib
    importlib.reload(ox)
    for filename, track in tracks.items():
        # get nearest nodes of every point in track
        #   in order to perform ox queries, the graph must meet certain requirements (eg. CRS)
        #   IMPORTANT: the source code of ox has been edited to make this work:
        #       -edited line 58 of utils_graph 
        #       -commented out this line
        #       -this is necessary as ox needs multindexes of int (osmid). momepy creates nodes with index (x, y)
        #       -with this line removed, ox does not mess with the index and the conversion can happen
        #       -restart your IDE after editing source code if it does not work
        nn = ox.nearest_nodes(graph, track['x'], track['y'])
        #nn = ox.nearest_edges(graph, track['x'], track['y'])
        '''for i in nn:
            nns.append(i)'''

        # get shortest path between pairs of nearest nodes to track
        all_sps = []
        end_points = []
        for i, n in enumerate(nn):
            if 0 < i < len(nn) - 1:
                try:
                    sp = nx.shortest_path(graph, n, nn[i + 1])
                    # check shortest path is less than a maximum (to avoid bridging between missing edges)
                    if len(sp) <= max_pathlength:
                        all_sps.extend(sp)
                    else:
                        end_points.append(nn[i + 1])
                except nx.NetworkXNoPath:
                    if debug:
                        print(f'Path could not be found between nodes {n} and {nn[i + 1]}')
        
        # remove duplicated nodes in paths
        if remove_duplicates:
            all_sps = list(dict.fromkeys(all_sps))

        track_segs[filename]['sp_list'] = all_sps
        track_segs[filename]['sp_graph'] = nx.MultiGraph(graph.subgraph(all_sps))
        track_segs[filename]['end_points'] = end_points

        
        if filter_isolate_branches:
            nodes_to_rm = []
            for u, v, data in list(track_segs[filename]['sp_graph'].edges(data=True)):
                #print(track_segs[filename]['sp_graph'].degree(u))
                if track_segs[filename]['sp_graph'].degree(u) == 1:
                    if track_segs[filename]['sp_graph'].degree(v) > 2: 
                        nodes_to_rm.append(u)
                        #track_segs[filename]['sp_graph'].remove_node(u)
          
                if track_segs[filename]['sp_graph'].degree(v) == 1:
                    if track_segs[filename]['sp_graph'].degree(u) > 2:
                        nodes_to_rm.append(v)
                        #track_segs[filename]['sp_graph'].remove_node(v)
                        #track_segs[filename]['sp_graph'].remove_edge(u, v)

            track_segs[filename]['sp_graph'].remove_nodes_from(nodes_to_rm)

    return track_segs

segments_along_track = GetSegsAlongTracks(cycle_tracks, SEG_GDF_GRAPH)
```
