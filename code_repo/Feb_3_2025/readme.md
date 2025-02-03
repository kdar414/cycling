**Segmentation**
- Working on the last functions of segmentation

```
import os
import sys
sys.path.append('/Users/kad/Desktop/cyclists/sophie/cycling-pollution-sophie-main/code/research_code/')  # Adjust this path
import utilities
import sweat


def GetGraph(graph_path, segment_length, segment_method, area_name, distance_args, include_footpaths, debug, 
            way_group_attribute, edge_rmattr=False):
    
    # linestring gdf path is a function of the original graph path, not created in config. perhaps that should be changed
    graph_ls_dir = graph_path.split('.')[0] + '_multipart.gpkg'

    if not os.path.exists(graph_path):
        filter = utilities.bike_withfootpaths if include_footpaths else utilities.custom_bikefilter
        #bbox = utils.GetBboxFromTracks(matched_tracks, name='domain AOI', xy_col=f'{FILTER_PREFIX}xy_tuple')
        if area_name == 'domain':
            bbox = utilities.domain_bbox
        elif area_name == 'innercentral':
            bbox = utilities.innercentral_bbox
        elif area_name == 'allakl':
            bbox = utilities.aklregion_bbox

        graph = OSMDownloader(bbox, filter=filter, debug=debug)

        if segment_method == 'edge':
            # filter, direct, segment graph
            if edge_rmattr:
                graph_withattribution = RemoveEdgesWithoutAttribute(graph, way_group_attribute, debug=debug)
                graph_withsegdirection = GetEdgeDirections(graph_withattribution, debug=debug)
                graph_segmented = SegmentEdges(graph_withsegdirection, segment_length,
                                            'interpolate', debug=debug, distance_args=distance_args)
                segment_graph = GraphFromSegments(graph_segmented, debug=debug)
                segment_graph_ordered = OrderSegmentGraph(segment_graph, group_attribute=way_group_attribute, debug=debug)
                segments_gdf = ox.graph_to_gdfs(segment_graph_ordered, nodes=False)

            else:
                graph_withsegdirection = GetEdgeDirections(graph, debug=debug)
                graph_segmented = SegmentEdges(graph_withsegdirection, segment_length,
                                            'interpolate', debug=debug, distance_args=distance_args)
                segment_graph = GraphFromSegments(graph_segmented, debug=debug)
                segments_gdf = ox.graph_to_gdfs(segment_graph, nodes=False)
            
            # create and order new graph based on segments on previous graph
            

           
            # convert graph to gdf
            

        elif segment_method == 'namedtopologic':

            graph_ordered = OrderSegmentGraph(graph, out_attribute='order', add_numbering=True)

            # for some reason some edges are not being assigned a custom_ref
            #   very minor (2 edges in innercentral bbox of 34800 edges)
            #   still something to consider. worth noting those 2 edges had identical osmids
            
            graph_ordered_clean = RemoveEdgesWithoutAttribute(graph_ordered, 'custom_ref')

            # segment cumulatively, save as gdf
            graph_seg_name = CumulativeSegmentation(graph_ordered_clean, 'custom_ref', segment_length, distance_args)
            
            # this works! pretty cool. read code_notes on 12/06/23 for bug description
            graph_seg_namedtopo = TopologicCumulativeSegmentation(graph_seg_name, distance_args, segment_length)
            segments_gdf = SegGDFFromGraph(graph_seg_namedtopo, segment_length)
        
        elif segment_method == 'topologic':
            graph_segmented = TopologicCumulativeSegmentation(graph, distance_args, segment_length)
            segments_gdf = SegGDFFromGraph(graph_segmented, segment_length)

        segments_gdf.to_file(graph_path, driver='GPKG', crs='EPSG:4326')

    else:    
        segments_gdf = gpd.read_file(graph_path).to_crs('EPSG:4326')

    # handle linestring creation. does not apply to edge segmentation method
    if segment_method != 'edge':
        if not os.path.exists(graph_ls_dir):
            segments_ls_gdf = utilities.LineGDFtoLineStringGDF(segments_gdf, segment_method=segment_method)
            segments_ls_gdf.to_file(graph_ls_dir, driver='GPKG', crs='EPSG:4326')
        else:
            segments_ls_gdf = gpd.read_file(graph_ls_dir).to_crs('EPSG:4326')

        return segments_gdf, segments_ls_gdf

    # edge segmentation returns None for linestring gdf
    else:
        return segments_gdf, None
    
get_graph = GetGraph(
    graph_path='/Users/kad/Desktop/cyclists/Kimberley/segmentation/jupyter/topologicgraph.gpkg',  # Ensure it's a file, not a directory
    segment_length=5, 
    segment_method='topologic', 
    area_name='allakl', 
    distance_args=distance_args_defined, 
    include_footpaths=True,  # Assuming this is meant to be True or False
    debug=True, 
    way_group_attribute='name'  # Replace 'name' with the actual attribute you're grouping by
)

```
- Running code above, taking a long time to run

- <ins>Next steps require the use of seg_group to sort/aggregated/mapped. There is not seg_id because that was causing issues earlier, need to work out how to add this or an alternative as it is also required for interpolation</ins>

- I am concerned about when I should join the mapmatched points with the pollution data
- Also create the matrix of metadata.
