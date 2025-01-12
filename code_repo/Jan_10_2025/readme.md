**Segmentation**

- Graphml created
- Next bit of code is xytuples(?) - what do I use for this?
- Working with a small area around uni to start with *"osm-graph.graphml"* - visualisation of this shows nodes and edges

<p align="center">
    <img width="300" src="https://github.com/user-attachments/assets/6e2d22a8-b385-4eb4-b094-af28d8d9145d" alt="visualisation of graphml for area near uni">
</p>

- *GRAPH ML NOTES*
    - Graphs contain edges and nodes
          - nodes = entities
          - edges = connections between nodes
    - GraphML (ML = machine learning) : focuses on obtaining features based on graphs and developing algorithms based on graph structure.
    - Use the nodes and edges to work out patterns/relationships in the graph. It looks at interconnected rather than linear systems.
    - Graph ML can be used to classify nodes, make predictions on missing links between nodes and classify graphs.
 
- Is xy_tuples a list of coordinates for the nodes in the network? then convert to points?
      - Ok so extracted nodes from the graphml and stored as a geodataframe
            - Then using code converted them to tuple -> then converted them to points
  
- Next is **DistancesFromXYList** -> need to inout xy_tuples, distance_args and references **DistanceBetweenXYPairs**
      - Struggling with distance_args which is a dictionary - not sure how to use this or what to use.
      - ok so distance_args were defined in the config.yml files. I have defined this in the script based on what was in the config file:
            - "unit" : "m"
            - "method" : "hs"
            - "decimals" : 2 (this cannot be in "" because the number is required for rounding. If "" then it is read as a string not int).

- Next is **AddMidPointsFromCutoff** -> line 103 of graph_manipulation.py
      - what are src distances? -> these are the distances between points
      - src_xytuple -> these are from the previous function in the code
      - The output of this is a list of coordinates of nodes
            - where the distances exceed the cutoff new noes are created. These are currently based on a cutoff of 10.

- Next is **GetEdgeDirections** -> defines analysis direction of ways in a network
      - gets northernmost node adn calculates bearing from that node to anotehr
      - then assigns a direction based on the value of the value (i.e. positive/negative)
      - GetEdgeDirections(cur_graph:nx.MultiDiGraph, undirected: bool = True, labels: list = ['A','B'], return_colours: bool = False, colours: list = ['blue','green'], debug: bool=False, identifier: str = 'osmid')
            - the graph must be the graphml -> the graph is already a networkx.classes.multigraph.MultiDiGraph (from type(graph))
      - So each has been assigned the output for each edge:
            - northernmost node: u or v (these are mentioned in Sophie's paper)
            - Bearing: Positive or negative value
            - Direction: A or B (A for positive bearing, B for negative bearing)
            - WayID: long identifier (not sure what this is may just be a unique identifier)

- next is def **CreateSedUID(way_uid, edge_order, positive_in_edge)**
      - Assume that the way_uid is from the previous function **GetEdgeDirections**
