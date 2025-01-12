
# %%
from haversine import haversine as hs
from scipy.spatial.distance import euclidean as euclidean
import pyproj
from shapely.geometry import Point, LineString
import time
import copy
import osmnx as ox
from datetime import datetime
import geopandas as gpd
import networkx as nx
import momepy as mp
from collections import defaultdict




# %%
#Checking that version 1.9.4 is installed. Newer versions cannot run this code as some have depreciated
ox.__version__

# %%
#ORIGINAL CODE FROM SOPHIE - Testing on small part of auckland
def OSMDownloader(bbox:dict, filter:str='', retain_all:bool=True, simplify:bool=False, debug:bool=False, 
                    log_file:str='/Users/kad/Desktop/cyclists/Kimberley/segmentation/graph_stats.csv',
                    useful_way_tags:list=ox.settings.useful_tags_way, return_directed:bool=False):
    if debug: 
        start = time.time()

    # TEST THIS
    ox.settings.useful_tags_way = useful_way_tags
    #ox.config(useful_tags_way=useful_way_tags)
    
    # will use osm graphs for now. can be converted to gdf. retains road name
    osm_graph = ox.graph_from_bbox(north=bbox['max_y'],
        south=bbox['min_y'], east=bbox['max_x'], west=bbox['min_x'],
        custom_filter=filter, retain_all=retain_all, simplify=simplify)

    if debug:
        print(f'Downloaded OSM graph in {round(time.time() - start, 1)}s')

    # save graph info for future reference
    now = datetime.now()
    min_x, min_y, max_x, max_y, name = bbox['min_x'], bbox['min_y'], bbox['max_x'], bbox['max_y'], bbox['name']
    csv_row = (f'\n{datetime.now()},{name},{min_x},{min_y},{max_x},'
                f'{max_y},{len(osm_graph.nodes)},{len(osm_graph.edges)},')
    with open(log_file, 'a') as fd:
        fd.write(csv_row)

    # I think we always want undirected, but here just in case
    if not return_directed:
        osm_graph = ox.get_undirected(osm_graph)
    
    return osm_graph

# Example bounding box for Auckland CBD area (using your coordinates)
bbox = {
    'min_x': 174.769975,  # Minimum longitude
    'min_y': -36.856088,  # Minimum latitude
    'max_x': 174.773988,  # Maximum longitude
    'max_y': -36.850245,  # Maximum latitude
    'name': 'Auckland CBD' # Name of the area
}

# Call the OSMDownloader function
graph = OSMDownloader(
    bbox=bbox,
    filter="['highway']",  # You can adjust the filter as needed
    retain_all=True,
    simplify=True,
    debug=True,
    log_file='/Users/kad/Desktop/cyclists/Kimberley/segmentation/graph_stats.csv',
    return_directed=False
)

# Print graph statistics
print(f"Graph nodes: {len(graph.nodes)}, edges: {len(graph.edges)}")

# Save the graph to a file
ox.save_graphml(graph, filepath='/Users/kad/Desktop/cyclists/Kimberley/segmentation/osm_graph.graphml')
print("Graph saved to osm_graph.graphml")

ox.plot_graph(graph)

# %%

# %% 
# XY Tuples to Points
# creates a list of Shapely Point objects from a list of xytuples
def XYsToPoints(xy_tuples:list):
    point_list = []
    for x, y in xy_tuples:
        point_list.append(Point(x, y))
    return point_list


# Getting the coordinates of the nodes - the distance between them drives segementation (pg 6-8 Sophie's Paper)

nodes, edges = ox.graph_to_gdfs(graph)
#looping throught the nodes gdf and extracting the coordinates as tuples
node_xy_tuples = [(x,y) for x,y in zip(nodes['x'], nodes['y'])]

#converting the tupules to points by calling the XYsToPoints function
node_tuples = XYsToPoints(xy_tuples= node_xy_tuples)

# %%
# Distances From XY List
# calculates haversine distances from previous to current point in a list of tuples
def DistancesFromXYList(xy_tuples:list, distance_args:dict, first_val:any=0):
    distances = [first_val]

    for previous, current in zip(xy_tuples, xy_tuples[1:]):
        #distance = hs((previous[1], previous[0]), (current[1], current[0]), unit=unit)
        distance = DistanceBetweenXYPairs(previous, current, distance_args)
        distances.append(round(distance, distance_args['decimals']))

    return distances

# Distance Between XY Pairs
# calculate distance between two xy points, giving projected or haversine option
def DistanceBetweenXYPairs(xy1:tuple, xy2:tuple, distance_args:dict):

    if distance_args['method'] == 'hs':
        # remember haversine input is order y, x
        dist = hs((xy1[1], xy1[0]), (xy2[1], xy2[0]), unit=distance_args['unit'])

    elif distance_args['method'] == 'proj':
        p = pyproj.Proj(distance_args['epsg'])

        xy1 = p(xy1[0], xy1[1])
        xy2 = p(xy2[0], xy2[1])

        # unit will be whatever the proj unit is
        dist = euclidean(xy1, xy2)
    
    return round(dist, distance_args['decimals'])

distance_args_defined = { #following the structure from config.yml
    "unit": "m",
    "method": "hs",
    "decimals": 2} # don't put speech marks around 2 or it will be interpreted as a string and the round function will not function

haversine_distances = DistancesFromXYList(xy_tuples=node_xy_tuples, distance_args= distance_args_defined)

# %%
# Add Midpoints From Cutoff
# creates new xy tuples between points that have a distance greater than a specified cutoff

# Assuming that src_distances are the distances between points

def AddMidPointsFromCutoff(src_distances:list, src_xytuples:list, cutoff:int):
    
    output_xytuples = []

    for index, distance in enumerate(src_distances):
        # calculate midpoint if distance between points is greater than cutoff
        if distance > cutoff:
            cur_geom = src_xytuples[index]
            prv_geom = src_xytuples[index - 1]

            # midpoint formula (basic linear algebra)
            interpolated_x = (prv_geom[0] + cur_geom[0]) / 2
            interpolated_y = (prv_geom[1] + cur_geom[1]) / 2

            output_xytuples.append((interpolated_x, interpolated_y))

        # make sure to add back the non-interpolated points
        output_xytuples.append(src_xytuples[index])

    return output_xytuples

midpoints = AddMidPointsFromCutoff(src_distances = haversine_distances, src_xytuples = node_xy_tuples, cutoff = 10)
# %%
# Get Edge Directions
# defines analysis direction of ways in a network
#   - finds northernmost node, then calculates bearing from that node to other
#   - if bearing is positive, assign one direction, if negative assign another
def GetEdgeDirections(cur_graph:nx.MultiDiGraph, undirected:bool=True, labels:list=['A', 'B'], 
                        return_colours:bool=False, colours:list=['blue', 'green'], 
                        debug:bool=False, identifier:str='osmid'):
    
    w_graph = copy.deepcopy(cur_graph)  # never work on source graph

    if debug:
        start = time.time()
    
    geodesic = pyproj.Geod(ellps='WGS84')  # used for bearing calculation

    # needs testing on both. default to be undirected
    if undirected:
        w_graph = w_graph.to_undirected()

    nodes = w_graph.nodes(data=True)
    way_id = 0  # simple enumeration for way id
    label_colours = []  # colours are useful when opening in a GIS for rule-based styles

    # iterate over edges with data. apply changes directly to data dict of graph
    for u, v, data in w_graph.edges(data=True):
        # save xy values for u and v nodes of way
        u_x, u_y = nodes[u]['x'], nodes[u]['y']
        v_x, v_y = nodes[v]['x'], nodes[v]['y']

        # get northernmost node simply by the highest u latitude value
        #   then calculate bearing to figure out direction
        if u_y > v_y:
            north_node = 'u'
            fwd_azimuth, bwd_azimuth, dist = geodesic.inv(u_x, u_y, v_x, v_y)
        else:  # both if v < u AND if u = v
            north_node = 'v'
            fwd_azimuth, bwd_azimuth, dist = geodesic.inv(v_x, v_y, u_x, u_y)
        
        # if the forward azimuth is positive, set to direction A, otherwise B
        if int(fwd_azimuth) > 0:
            direction = 'A'
            label_colours.append(colours[0])
        else:
            direction = 'B'
            label_colours.append(colours[1])

        data['north_node'] = north_node
        data['bearing'] = int(fwd_azimuth)
        data['direction'] = direction
        data['way_id'] = way_id if identifier == 'custom' else data['osmid']
        
        way_id += 1

    if debug:
        print(f'Calculated direction for {len(w_graph.edges)} ways in {round(time.time() - start, 1)}s')
    
    if return_colours:
        return w_graph, label_colours
    else:
        return w_graph

    
edge_directions = GetEdgeDirections(cur_graph = graph, undirected = True, labels=['A','B'], return_colours = False, colours = ['blue', 'green'], debug = False)
# %%
def CreateSegUID(way_uid, edge_order, position_in_edge):
    # do I want this to be an int? probably so I can order
    seg_uid = f'{way_uid}_{edge_order}_{position_in_edge}'
    return seg_uid