- Meeting with Sila re: error with segmentation. She suggested using 1) the segment start/end points in the segmentation code, 2) get equation of straight line of a segment and test midpoint and 3) get mapmatched points and then extract the network based on that.
- I have tested 1) and 2) without success - same error appears (I updated Sila and will attend HackyHour)

**Hacky Hour Help**
-  print(f'Segments not found in edge: {u}, {v}') is masking the true error *ValueError: not enough values to unpack (expected 8, got 5)*
-  sample segments:
[[(174.7830541, -36.9313286), (174.78300376292134, -36.93130854382022), 0, '1-0', 5.0], [(174.78300376292134, -36.93130854382022), (174.7829645, -36.9312929), 1, '1-1', 3.9]] note the 5 elements
- this originates in the SegmentEdges function, which defines this structure:
segment = [start_geom, end_geom, cur_seg_id, cur_seg_uid, cur_seg_len] perhaps the segment list data structure used to be different, but without a git commit log there's no way of telling
-anyway, adjusting: for start_xy, end_xy, seg_id, seg_uid, seg_grp, seg_order, edge_grp, length in data['segments']: to: for start_xy, end_xy, seg_id, seg_uid, length in data['segments']:
- you'll then need to comment out the lines that reference those deleted variables (edited)
- Also consider using tqdm , particularly for those longer running cells notfound_val:any='not available' - it's more memory efficient to use pd.NA or None instead of the string "not available"
-  Segment GeoDataFrame From Graph
 THIS ONLY WORKS ON THE SEGMENTED GRAPH, NOT THE GRAPH PRODUCED FROM SEGMENTS creates geodataframe of segments from a (spatially segmented) networkx graph
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
