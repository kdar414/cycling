**Troubleshooting segmentation**
- segmentation.ipynb is where I am working (needed a break from looking at visualstudio!)

##### 1) **def OSMDownloaderfunction**: works to download small area of Auckland.
- output is networkxMultigraph called osm_graph
- saves as osm_graph.graphml

##### 2) **def XYsToPoints**: currently input the tuples/nodes of the osm_graph
- not sure if this is what goes in here, or if is is mapmatched tuples
- it requeires xy_tuples so I am thinking it is mapmatched
- *Brief sidetrack to mapmatching* : I have made a test mapmatched route (r = 5). Made it into a list and have imported the matched_xy_tuple to Jupyter Notebook and produced points called node_tuples.

##### 3) **def DistancesfromXYList** and **DistancebetweenXYPairs**
- together as the former requires the latter to run
- useed the node_xy_tuples and distance args (from config file)
- calcuates haversine distance which is a list

##### 4) **def AddMidPointsFromCutoff**
- input haversine distances from src_distance (what is src? apparently it means source)
- input node_xy_tuples for src_tuples
- produces midpoints which is a list of midpoints

##### 5) **def GetEdgeDirections**
- input graph: I used osm_graph (this is the only graph file so far)
- produces edge-directions:

      - multigraph with 3050 nodes and 4485 edges
      - networkx.classes.multigraph.MultiGraph
