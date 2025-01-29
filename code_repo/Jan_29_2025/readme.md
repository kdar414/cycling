**Segmentation**

<ins>WORKING IN JUPYTER NOTEBOOK IN segmentation-Copy3</ins>

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
![Screen Shot 2025-01-29 at 09 19 31](https://github.com/user-attachments/assets/f8a2c47c-c8fa-4147-9156-4088a8f8d1e0)


- Testing out the code from hacky hour: <ins>SegGDFFromGraph</ins>
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

<ins>Cumulative Segmentation</ins>
- Running the code, there was an issue with using the group attribute as 'name' but I am pretty sure that this is what I should use based on previous use. I couldn't find a direct mention of it.
- The code used is:
```
def CumulativeSegmentation(w_graph, group_attribute, segment_length, distance_args):
    # Initialize a dictionary to store edges by road name
    edges_by_road = {}

    # Open a file to log the debug output
    with open("segmentation_log.txt", "w") as log_file: #output is printed to this file
        # Iterate through each edge in the graph
        for u, v, data in w_graph.edges(data=True):
            group_value = data[group_attribute]
            
            if isinstance(group_value, list):
                group_value = ', '.join(group_value)
            
            # Log the data to the file
            log_file.write(f"Data for edge ({u}, {v}): {group_value}, Type: {type(group_value)}\n")
            
            if group_value not in edges_by_road:
                edges_by_road[group_value] = []
            
            edges_by_road[group_value].append((u, v, 0))

    # Return the edges grouped by road
    return edges_by_road

# get subgraphs from grouping attribute
    #   assumes this grouping attribute has already processed unconnected duplicates
    all_subgraphs = [nx.MultiDiGraph(w_graph.edge_subgraph(edges_by_road[name]).copy()).to_undirected() for name in edges_by_road]

    road_segment_groups = {}
    for subgraph in all_subgraphs:

        edge_list = list(subgraph.edges(data=True))

        # sort edges in DFS order
        edge_list.sort(key=lambda e: e[2]['order'], reverse=False)  # this 'order' should be a variable

        # iterate over edges, grouping based on conditions described above
        edge_groups = []
        this_group = []
        for i, edge in enumerate(edge_list):

            current_edge = edge
            # if this is not the last edge in a group
            if i != len(edge_list) - 1:
                # get next edge in list (as this is in order, it is consecutive)
                next_edge = edge_list[i + 1]
                # check if next edge is connected to current (based on node values)
                next_connected = False

                
                for n in current_edge[0:2]:
                    if n in next_edge:
                        next_connected = True
                        # save current end node as one that is connected to the current edge from the next edge
                        cur_endnode = n
                if not next_connected:
                    # end group
                    this_group.append(current_edge)
                    edge_groups.append(this_group)
                    this_group = []
                # check if intersection (2) or road ends (1)
                elif w_graph.degree(cur_endnode) > 2 or w_graph.degree(cur_endnode) == 1:
                    # end group
                    this_group.append(current_edge)
                    edge_groups.append(this_group)
                    this_group = []  
                else:
                    # add edge to group, continue group
                    this_group.append(current_edge)

                
            else:
                # end group
                this_group.append(current_edge)
                edge_groups.append(this_group)

        road_segment_groups[edge_list[0][2]['custom_ref']] = edge_groups

    # I am quite sure that the next two code blocks make each other redundant, and I can do it in one
    #   - fix this in future
    # assign identifier based on road segment group
    for ref, edgegroups in road_segment_groups.items():
        edgegroup_id = 0
        for group in edgegroups:
            for edge in group:
                w_graph[edge[0]][edge[1]][0]['edgegroup_id'] = edgegroup_id
            edgegroup_id += 1

    # sort edges into dict by edge group identifier
    edges_by_road = {}
    for u, v, data in w_graph.edges(data=True):
        cur_ref = data[group_attribute]
        cur_edgegroup = data['edgegroup_id']
        if cur_ref in edges_by_road:
            if cur_edgegroup in edges_by_road[cur_ref]:
                edges_by_road[cur_ref][cur_edgegroup].append((u, v, 0, data))
            else:
                edges_by_road[cur_ref][cur_edgegroup] = []
                edges_by_road[cur_ref][cur_edgegroup].append((u, v, 0, data))
        else:
            edges_by_road[cur_ref] = {}
            edges_by_road[cur_ref][cur_edgegroup] = []
            edges_by_road[cur_ref][cur_edgegroup].append((u, v, 0, data))

    # second step: spatial segmentation based on groups created above
    #   similar to original approach but with notable differences:
    #       - when remaining length is less than segment length, save this length (residual)
    #       - make the next segment shorter (- residual length), and give it the same identifier as previous
    #       - this involves lots of checks on u/v geometry from current/next node pair
    nodes = w_graph.nodes(data=True)
    for ref, edgegroups in edges_by_road.items():
        seg_order = 0

        # sort edgegroups by key (which itself is sorted)
        edgegroups = dict(sorted(edgegroups.items(), reverse=False))

        for edgegroup in edgegroups:
            
            # get current group, sort by order
            cur_group = edges_by_road[ref][edgegroup]     
            cur_group.sort(key=lambda e: e[3]['order'], reverse=False)

            # segmentation happens here
            residual_len = 0
            residual = False
            seg_num = 0
            seg_pos_index = 0
            first_edge = True
            
            for i, (u, v, k, data) in enumerate(cur_group):
                
                u_x, u_y = nodes[u]['x'], nodes[u]['y']
                v_x, v_y = nodes[v]['x'], nodes[v]['y']
                    
                if residual:
                    if residual_x == u_x:
                        x1, x2, y1, y2 = UVtoXYs(u_x, u_y, v_x, v_y, 'uv')
                    else:
                        x1, x2, y1, y2 = UVtoXYs(u_x, u_y, v_x, v_y, 'vu')
                else:
                    if first_edge:
                        first_edge = False
                        # if there is more than one edge in the group
                        if len(cur_group) > 1:
                            
                            next_edge = cur_group[i + 1]
                            next_u, next_v = next_edge[0], next_edge[1]
                            
                            # fixed bug here 
                            if next_u == u or u == next_v:
                                x1, x2, y1, y2 = UVtoXYs(u_x, u_y, v_x, v_y, 'vu')
                            else:

                                x1, x2, y1, y2 = UVtoXYs(u_x, u_y, v_x, v_y, 'uv')
                        
                        # if there is only one edge in the group
                        else:
                            # if this is not the first group in the road
                            if edgegroup != 0:

                                prev_group = edges_by_road[ref][edgegroup - 1]
                                #print(prev_group[-1][3]['order'], cur_group[0][3]['order'])
                                v_cons, u_cons = w_graph.edges(v), w_graph.edges(u)

                                prev_group_nodata = [i[0:2] for i in prev_group]

                                prev_group.sort(key=lambda e: e[3]['order'], reverse=False)

                                if prev_group[-1][0:2] in v_cons:
                                    x1, x2, y1, y2 = UVtoXYs(u_x, u_y, v_x, v_y, 'vu')
                                elif prev_group[-1][0:2] in u_cons:
                                    x1, x2, y1, y2 = UVtoXYs(u_x, u_y, v_x, v_y, 'uv')
                                else:
                                    x1, x2, y1, y2 = UVtoXYs(u_x, u_y, v_x, v_y, 'n')
                            else:
                                # take northernmost node
                                x1, x2, y1, y2 = UVtoXYs(u_x, u_y, v_x, v_y, 'n')   
                    else:
                        print('this edge case is when there is no residual and it moves straight on to a next edge. need to handle')

                    seg_num += 1
                    seg_order += 1
                    seg_pos_index = 0
                    cur_seg_len = 0
                
                segments = []

                d = DistanceBetweenXYPairs((x1, y1), (x2, y2), distance_args)

                already_done = False
                # if there is residual distance to include from last edge
                if residual:
                    # if the length of the edge is greater than the residual length
                    if d < residual_len:
                        
                        # save segment info
                        cur_seg_id, cur_seg_uid, cur_seg_grp = GetSegIDs(data['way_number'], seg_num, seg_pos_index, edgegroup, data['order'])
                        segments.append([(x1, y1), (x2, y2), cur_seg_id, cur_seg_uid, cur_seg_grp, seg_order, edgegroup, d])

                        # extras
                        residual = True
                        residual_x, residual_y = x2, y2
                        residual_len = round(residual_len - d, distance_args['decimals'])
                        already_done = True
                        seg_pos_index += 1

                    # if the length of the edge is less than the residual length
                    else:
                        # will this work if the residual is longer than the u->v distance?
                        # no - there will have to be 'nested'/cumulative residual calculations
                        t = residual_len / d

                        end_x, end_y = (((1 - t) * x1 + t * x2), ((1 - t) * y1 + t * y2))
                        cur_seg_len = DistanceBetweenXYPairs((x1, y1), (end_x, end_y), distance_args)
                        
                        # seg info
                        cur_seg_id, cur_seg_uid, cur_seg_grp = GetSegIDs(data['way_number'], seg_num, seg_pos_index, edgegroup, data['order'])
                        segments.append([(x1, y1), (end_x, end_y), cur_seg_id, cur_seg_uid, cur_seg_grp, seg_order, edgegroup, cur_seg_len])

                        # reset
                        d = d - cur_seg_len
                        x1, y1 = end_x, end_y
                        residual = False
                        seg_num += 1
                        seg_order += 1
                        seg_pos_index = 0
                        #print(d, cur_seg_len)

                # while the remaining distance in the edge is longer than the segment length
                while d > segment_length:
                
                    t = segment_length / d
                    end_x, end_y = (((1 - t) * x1 + t * x2), ((1 - t) * y1 + t * y2))
                    cur_seg_len = DistanceBetweenXYPairs((x1, y1), (end_x, end_y), distance_args)

                    # save segment info
                    cur_seg_id, cur_seg_uid, cur_seg_grp = GetSegIDs(data['way_number'], seg_num, seg_pos_index, edgegroup, data['order'])
                    segments.append([(x1, y1), (end_x, end_y), cur_seg_id, cur_seg_uid, cur_seg_grp, seg_order, edgegroup, cur_seg_len])
                    
                    # reset segment values
                    seg_num += 1
                    seg_order += 1
                    #seg_pos_index = 0
                    d = DistanceBetweenXYPairs((x2, y2), (end_x, end_y), distance_args)
                    x1, y1 = end_x, end_y
                    
                else:
                    if not already_done:
                        cur_seg_len = DistanceBetweenXYPairs((x1, y1), (x2, y2), distance_args)
                    
                        # save segment info
                        cur_seg_id, cur_seg_uid, cur_seg_grp = GetSegIDs(data['way_number'], seg_num, seg_pos_index, edgegroup, data['order'])
                        segments.append([(x1, y1), (x2, y2), cur_seg_id, cur_seg_uid, cur_seg_grp, seg_order, edgegroup, cur_seg_len])
                        
                        # extras
                        residual = True
                        seg_pos_index += 1
                        residual_len = round(segment_length - cur_seg_len, distance_args['decimals'])
                        residual_x, residual_y = x2, y2

                data['segments'] = segments
                data['edge_id'] = None
                data['direction'] = None
                data['order_on_road'] = data['order']

    return w_graph

distance_args_defined = { #following the structure from config.yml
    "unit": "m",
    "method": "hs",
    "decimals": 2} # don't put speech marks around 2 or it will be interpreted as a string and the round function will not function


cumulative_segmentation_graph = CumulativeSegmentation(graph_from_segments, 'name', 5, distance_args_defined)

```
- The output of this which says the data for each edge is stored in a file called segmentation_log.txt. This has been included in the folder of this file. 
- There is a **problem: cumulative_segmentation_graph is being returned as a dictionary not as a graph**
- I am trying to convert it to a graph: this is taking a long time and I am having issues with my computer freezing/the notebook tab crashing. Have created a new version because the old file was corrupt, it is located here: "/Users/kad/Desktop/cyclists/Kimberley/segmentation/jupyter/segmentation_3.ipynb"
- Ok some progress I think!
```
import networkx as nx
import logging

# Initialize a directed graph
GRAPH_cumulative_segmentation = nx.DiGraph()

# Loop through each road and add edges with attributes
for road, edges in cumulative_segmentation_graph.items():
    for start, end, road_name in edges:
        GRAPH_cumulative_segmentation.add_edge(start, end, road_name=road_name)
```
```
print("Sample nodes:", list(GRAPH_cumulative_segmentation.nodes)[:10])  
print("Sample edges:", list(GRAPH_cumulative_segmentation.edges(data=True))[:10])
```
![Screen Shot 2025-01-29 at 14 49 44](https://github.com/user-attachments/assets/265e36e7-ba78-4066-9cdb-24a2795885df)
**Ok there is a weird issue with road name being 0 for each because I have seen names in other data but under the label 'name' not 'road_name'**
```
import matplotlib.pyplot as plt

subgraph = GRAPH_cumulative_segmentation.subgraph(list(GRAPH_cumulative_segmentation.nodes)[:50])  # Subgraph with 50 nodes
nx.draw(subgraph, with_labels=True, node_size=50, font_size=8)
plt.show()
```
![download](https://github.com/user-attachments/assets/4092945e-b55e-4d98-806e-2937b70f8a2d)
