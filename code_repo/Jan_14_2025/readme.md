**Meeting with Sila**
- Questions:
    - Should segmentation be run on all of Aucklnd or run each time for each cycle route. **Run segementation for all of Auckland so that the segments remain the same across the analysis**
    - Is there a specific radius for mapmatching (tested r= 10,20,50). **See other papers who use the same algorithm for cycling/car, other than that 50 seems good**.
 
- If SegUID does not work we can try to work around it: let Sila know if Sophie does not reply by Friday.
- Once segmented and mapmatched - should make box plots for different routes and segments. Number of dates we have data we have and timeseries figures of pollution through the day can be produced.

|   | Columns should be time in s |
| ------------- | ------------- |
| Rows should be the segment  | Number of repeats  |

- Can work on mapmatching the rest of the cycles even if segmentation not prepared. 

**Segmentation**
- So for now I am skipping the **CreateSegUid** -> have contacted Sophie (let Sila know if no reply by Friday)
- def **SimplePointsToSegs**(segments_gdf:gpd, tracks:dict, in_prefix:str = 'match', debug:bool=False)
      - This function assigns points to a segment based on a simple spatial join
          - input tracks as dictionaries and convert within function
          - segment input as gdf -> have used graph_to_gdfs with nodes and node-geometry as false. If true it does not become a gdf (it is tuple) and cannot be plot.
    - Use graph_gdf.explore() to plot all of the edges
    - The segments are called graph_gdf
    - The tracks are map_matched points -> made a test of tracks using r=10, trying pickle module to dump dictionary (in OSRM_caller, map_matching) and then reopen later for segmentation.
          - This file is then imported in the graph_maipulation.py and used as the tracks dictionary for **SimplePointsToSegs**.

- def **GetTerminatingNodes**(graph, return_data = False, debug = False, order_by_north = True)
      - input **graph** which is the working segmented/network multiGraph
      - This outputs a list called terminating_nodes. I believe this is a list of nodes at the end of a segment e.g. cul de sac

- def **RemoveEdgesWithoutAttribute**(graph, attribute, debug, remove_isolates)
      - This removes certain edges and nodes which do not have a certain specified attribute
      - Recommended setting debug = True to show the number of nodes and edges removed from the graph.
      - Output is another graph called "removed_no_attributes_graph" (at the moment it is tested to remove those without geometry). *So from now on I think this graph should be used for functions needing a graph*.

- def **OrderSegmentGraph**(cur_graph: nx.MultiDiGraph, out_attribute = 'seg_pos_on_way', group_attribute = 'name', debug = 'False', add_numbering = False).
      - This section was mentioned in Sophie's paper: I recognise the deep search
      = So this function calls : RemoveedgesWithougAttribute and GetTerminatingNodes.
      - produces seg_pos_on_way (is this edge_order or position_in_edge from SegUID?)
      - some issues with the code which I have tried to correct
          - if data[group_atribute] in edges_by_road: gave the error unhashable type:list. This suggests that this is a list and so it needs to be changes to a string or tuple. I converted it to a tuple **group_value = tuple(group_value)**
      - Also custom_ref= list(subgraph.edges(data=True)[0][2]['name]+'_'+str(i): with the error "Type Error: can only conatenate list (not str) to list". Fixed this by changing the edge data at index [2] before concatenation (linking together). **custom_ref = str(list(subgraph.edges(data=True)[0][2].get('name','no_name')) + '_' + str(i). (NEED TO CHECK IF THE OUTPUT MAKES SENSE).

- next is def **SegGDFFromGraph**(graph:nx.MultiDiGraph, segment_length:int,colouts:list=['blue','red'], notfound_val: any = 'not available')
      - This needs a segmented graph not a graph from segments -> which one is the segmented graph? nx.MultiDiGraph may be a clue.
      - **Current Issue**: The output says that segments not found in edge. Seems like segments are missing from ordered seg graph so likley issue in that part of the code.
          
