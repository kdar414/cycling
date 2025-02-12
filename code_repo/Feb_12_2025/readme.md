- It appears that the error in the graph network occurs during the conversion of Ordered_seg_graph to a gdf in the function def SegGDFFromGraph
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
                "seg_length": length,
                "osmid": data["osmid"],
                # Extract segment group from seg_uid (e.g., '2-0' -> group 2)
                "seg_group": seg_uid.split('-')[0] if '-' in seg_uid else seg_uid  
            })
    gdf = gpd.GeoDataFrame(rows, crs=4326)
    return gdf

Segment_gdf = SegGDFFromGraph(graph = Ordered_seg_graph)
```
- The Segment_gdf comes out as:
![image](https://github.com/user-attachments/assets/d2c4e693-7466-44bd-acbd-30029b68f6d9)
- I tried a different way of converting it to a gdf using
```
import momepy
nodes_gdf, edges_gdf = momepy.nx_to_gdf(Ordered_seg_graph)
edges_gdf.plot()
nodes_gdf.plot()

#On the same axis
fig, ax = plt.subplots(figsize=(10, 10))
edges_gdf.plot(ax=ax, color="black", linewidth=1)
nodes_gdf.plot(ax=ax, color="red", markersize=5)
plt.show()

```

| Edges       |  Nodes |
:-------------------------:|:-------------------------:
![image](https://github.com/user-attachments/assets/c2933c8a-5c37-4943-a31a-923fbe275832)|![image](https://github.com/user-attachments/assets/41e3bf24-e6fd-46f8-b086-57f909672905)

![image](https://github.com/user-attachments/assets/547d257b-7832-416f-b606-9247eba50b84)

- Once the Ordered_seg_graph is passed through this chunk (below) the errors in the network show up again.
```
# Validate Segment
# Checks that the u/v node geometry matches up with the first/last points in segment list
def ValidateSegment(graph, node_start, node_end, segments):
    node_start_info = graph.nodes[node_start]
    node_end_info = graph.nodes[node_end]

    node_start_loc = (node_start_info['x'], node_start_info['y'])
    node_end_loc = (node_end_info['x'], node_end_info['y'])

    start_at_start = segments[0][0] == node_start_loc
    start_at_end = segments[0][0] == node_end_loc

    end_at_start = segments[-1][1] == node_start_loc
    end_at_end = segments[-1][1] == node_end_loc

    if start_at_start and end_at_end:
        return 1
    elif start_at_end and end_at_start:
        return -1
    else:
        return 0


# Graph From Segments
# Create graph from lists of segments, ignoring previous graph geometry
def GraphFromSegments(segmented_graph, debug=False):

    out_graph = nx.MultiDiGraph()
    out_graph.graph['crs'] = 'epsg:4326'  # needed to do osmnx operations

    for u, v, data in list(segmented_graph.edges(data=True)):
        segments = data['segments']

        # ensure that segmetns are geometrically valid
        direction = ValidateSegment(segmented_graph, u, v, segments)
        # if the segments are not valid, skip this edge
        if direction == 0:
            if debug:
                print(f'Skipping edge {u} -> {v}')
            continue  # what does this do?

        # this code was written by David Wu, I need to check with them about it
        boundary_nodes = [None, u, v]
        intermediate_node_names = [f"SEGNODE_{seg_id}" for _, _, _, seg_id, *_ in segments[:-1]]
        node_list = [boundary_nodes[direction], *intermediate_node_names, boundary_nodes[-direction]]
        # add in start node, will overwrite if already exists
        out_graph.add_node(node_list[0], **segmented_graph.nodes[node_list[0]])

        for node_A, node_B, seg_info in zip(node_list[:-1], node_list[1:], segments):
            loc_A, loc_B, seg_order, seg_id, seg_len = seg_info

            edge_name = f'{node_A}-{node_B}'
            seg_uid = f"{data['osmid']}_{data['edge_id']}_{seg_order}"
            seg_id = f"{data['edge_id']}-{seg_order}"

            # add end node for each new segment
            out_graph.add_node(node_B, **segmented_graph.nodes.get(node_B, {'x': loc_B[0], 'y': loc_B[1]}))

            out_graph.add_edge(node_A, node_B, 0, seg_uid=seg_uid, seg_length=seg_len, seg_order=seg_order, 
                        edge_id=data['edge_id'], osmid=data['osmid'], seg_id=seg_id, 
                        name=data['name'] if 'name' in data else None)
            
    return out_graph
            
graph_from_segments = GraphFromSegments(Ordered_seg_graph, debug = True)
```
| Ordered_seg_graph      |  graph_from_segments |
:-------------------------:|:-------------------------:
![image](https://github.com/user-attachments/assets/3afa8ed3-667d-4721-affe-241422765c19)|![image](https://github.com/user-attachments/assets/6404ffb8-d2a7-483f-8690-1cb3406bf31b)
