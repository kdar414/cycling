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
  
- sample edge attributes produces a list of: (e.g. for index 437)

      - (25773727, 540465689, {'osmid' : 763203, 'name' : 'Alberton Place', 'highway' : 'residential', 'maxspeed' : '50', 'oneway' : False, 'reversed' : False, 'length' : 2617, 'from' : 540465689, 'to' : 25773727, 'geometry' : <LINESTRING geometry ..... >, 'north_node' : 'u', 'bearing' : 176, 'direction' : 'A', 'way_id' : 76372033}).

##### 6) **def SegmentEdges**
- cur = current so cur_graph = current graph. So I used edge_directions (?). It is definently edge_directions because osm_graph has an error becuase it does not contain directions.
- output = segment_edges_graph:

        - networkx.classes.multigraph.MultiGraph
        - MultiGraph with 3050 nodes and 4485 edges

##### 7) **def SimplePointsToSegs**
- skipping at the moment becasue not needed by other functions later
- This joins a segments_gdf and a dictionary of tracks
- *where does the segments_gdf come from?*

##### 8) **def GetTerminatingNodes**
- input says graph not cur_graph so my options are a) osm_graph and b) segment_edges_graph
- same as **9) def RemoveEdgesWithoutAttributes**

##### 10) **def OrderSegmentGraph**
- 8 and 9 feed into this function. But this function (10) has the input of cur_graph.
- Input into this segment_edges_graph
- Output = Ordered_seg_graph

##### 11) **def SegGDFFromGraph**: needs to use segmented graph
- input says graph not cur_graph so I input osm_graph
- ok it says error processing edge (25769626, 4330750496): 'segments'
- switched the graph to Ordered_seg_graph
- There are three variations of this function
- 1) Original from Sophie which produces the output: "segments not found in edge: 25769626, 4330750496. This error occurs when Ordered_seg_graph and osm_graph are used.
  2) Adjusted to:
     
     a) error handle: to say Error processing edge({u},{v}:{e})

     b) Attribute retrieval
           - container['way_surface'].append(data['surface'] if  'surface' in data else notfound_val to container['way_surface'].append(data.get('surface', notfound_val)

     c) Colour assignment activated

     d) except has changes to: except Exception as e: Print (f'Error processing edge ({u},{v}):({e})
     The output shows Error processing edge (25769626, 4330750496): not enough values to unpack (expected 8, got 5)

  3) Adjusted (chatgpt) to

     a) Handle segments with 8 and 5 attributes

            8 = start_xy, end_xy, seg_id, seg_uid, seg_grp, seg_order, edge_grp, length

            5 = start_xy, end_xy, seg_id, seg_uid, seg_grp.

     - Missing attributes seg_order, edge_grp and length are assigned NaN. This runs but I think the missing attributes and causing errors later on.

- The output of version 3 is a gdf called segment_gdf with these columns

      - 1) way_name
      - 2) way_highway
      - 3) way_surface
      - 4) way_maxspeed
      - 5) way_number
      - 6) edgegroup_id
      - 7) edge_osmid
      - 8) edge_order
      - 9) geometry
      - 10) seg_uid
      - 11) seg_id
      - 12) seg_group
      - 13) seg_order
      - 14) seg_length
      - 15) seg_roundingerror
      - 16) colour

- There are missing values for some of the attributes.
     
