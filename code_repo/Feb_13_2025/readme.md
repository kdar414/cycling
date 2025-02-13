- Issue seems to arise between Ordered_seg_graph being created and graph_from_segments being created.
- Results in nodes no longer having coordinates after running this code:

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


def GraphFromSegments(segmented_graph, debug=False):
    out_graph = nx.MultiDiGraph()
    out_graph.graph['crs'] = 'epsg:4326'  # needed to do osmnx operations
    
    for u, v, data in list(segmented_graph.edges(data=True)):
        segments = data['segments']

        # Validate the direction of the segment
        direction = ValidateSegment(segmented_graph, u, v, segments)

        # Skip invalid edges (direction 0 indicates invalid)
        if direction == 0:
            continue

        # Define boundary nodes and intermediate node names for the segment
        boundary_nodes = [None, u, v]
        intermediate_node_names = [f"SEGNODE_{seg_id}" for _, _, _, seg_id, *_ in segments[:-1]]
        node_list = [boundary_nodes[direction], *intermediate_node_names, boundary_nodes[-direction]]

        # Add nodes and edges for the segments
        for node_A, node_B, seg_info in zip(node_list[:-1], node_list[1:], segments):
            loc_A, loc_B, seg_order, seg_id, seg_len = seg_info

            # Add nodes to the graph with coordinates if missing
            if node_B not in out_graph.nodes:
                out_graph.add_node(node_B, x=loc_B[0], y=loc_B[1])  # Ensure coordinates are added

            # Add edges to the graph
            out_graph.add_edge(node_A, node_B, 0, seg_uid=f"{data['osmid']}_{data['edge_id']}_{seg_order}", 
                               seg_length=seg_len, seg_order=seg_order, edge_id=data['edge_id'], osmid=data['osmid'], 
                               seg_id=seg_id, name=data.get('name', None))

    return out_graph

# Create graph from segments
graph_from_segments = GraphFromSegments(Ordered_seg_graph, debug=True)

# Ensure all nodes have coordinates before plotting
for node, data in graph_from_segments.nodes(data=True):
    if 'x' not in data or 'y' not in data:
        print(f"Node {node} is missing coordinates!")

        

# Plot the graph again
ox.plot_graph(graph_from_segments)



```

```
Node 25842600 is missing coordinates!
Node 624924293 is missing coordinates!
Node 2978511005 is missing coordinates!
Node 25842611 is missing coordinates!
Node 25842621 is missing coordinates!
Node 25842623 is missing coordinates!
Node 25842637 is missing coordinates!
Node 1837230500 is missing coordinates!
Node 25842633 is missing coordinates!
Node 25842631 is missing coordinates!
Node 25842682 is missing coordinates!
Node 11245109187 is missing coordinates!
Node 25842649 is missing coordinates!
Node 25842651 is missing coordinates!
Node 25842659 is missing coordinates!
Node 1192154171 is missing coordinates!
Node 25842656 is missing coordinates!
Node 25842705 is missing coordinates!
Node 36499169 is missing coordinates!
Node 25842736 is missing coordinates!
Node 10206386582 is missing coordinates!
Node 10206386603 is missing coordinates!
Node 25842738 is missing coordinates!
Node 36499176 is missing coordinates!
Node 6926206903 is missing coordinates!
Node 7957507707 is missing coordinates!
Node 259288158 is missing coordinates!
Node 25885492 is missing coordinates!
Node 10605307059 is missing coordinates!
Node 260734405 is missing coordinates!
Node 7957507704 is missing coordinates!
Node 3577917167 is missing coordinates!
Node 6225173402 is missing coordinates!
Node 635565513 is missing coordinates!
Node 635565527 is missing coordinates!
Node 635565534 is missing coordinates!
Node 635565548 is missing coordinates!
Node 2978511860 is missing coordinates!
Node 10580998538 is missing coordinates!
Node 955593309 is missing coordinates!
Node 1417329273 is missing coordinates!
Node 10580998518 is missing coordinates!
Node 2978448691 is missing coordinates!
Node 10580998496 is missing coordinates!
Node 7824666892 is missing coordinates!
Node 10580998520 is missing coordinates!
Node 7824617784 is missing coordinates!
Node 3353606077 is missing coordinates!
Node 3801751510 is missing coordinates!
Node 11414415695 is missing coordinates!
Node 7824666888 is missing coordinates!
Node 7824666889 is missing coordinates!
Node 10580998539 is missing coordinates!
Node 10581003856 is missing coordinates!
Node 10581003855 is missing coordinates!
Node 8985401548 is missing coordinates!
Node 7957507712 is missing coordinates!
Node 10774464397 is missing coordinates!
Node 10206386563 is missing coordinates!
Node 11091165597 is missing coordinates!
Node 11091165603 is missing coordinates!
Node 10581003853 is missing coordinates!

```
- I have spent a few hours on this and I have not been able to make any more progress. I have posted on the hackyhour slack channel so hopefully that will help to resolve the issue.
- Whilst I am waiting, I am going to try a section of the network that looks ok, using *Maike/06-12-2023/mgat-Uoa-kroad-Uoa_06-12-23-gps_1.csv*. Need to mapmatch this and then go through segmentation process.
