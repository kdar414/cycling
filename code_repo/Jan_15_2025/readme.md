**Segmentation**

- So the error is segments not found it edge

      - does this mean points are not being assigned to segments?
      - is it something about edge creation?
      - is it an error with ordersegment and changes as a consequence of errors?

- ok so ordered_seg_graph contains edges so seems the segement creation is the issue (nodes also exist)
- seg_pos_on_way is shown and custom_ref
- so there are segments in the data but an odd result of 'got 5 expected 8' for segments. (Expecting 8 pieces of data?)
- Ordered_seg_graph is the result of def OrderSegmentGraph which assigns an order to segments/graph edges
- each node in Ordered_seg_graph has: 2576926 (node/id?), y, x, streetcount
- each edge in Ordered_seg_graph has: 2576926, 4330750496, osmid, lanes, name, highway, maxspeed, oneway, reversed, length, from, to, geometry (linestring), northnode, bearing, direction, way_id, segments, edge_id, seg_pos_on_way, custom_ref
- I have continued and moved on to **ValidateSegment** and **GraphFromSegments**

         - produced graph_from_segs (graph). Format: (433075046, segnode, key): seg_uid, seglength, seg_order, edge_id, osmid, seg_id, name

- **def UVtoXYs** convert to xy based on input direction and after GetSegIDs but not input anything yet.
- Lots of errors with **def CumulativeSegmentation** with errors associated with hashable and ['order']

The code is not working correctly because the segment_GDF does not have some of the attributes e.g. edge_order so then the SegGDFFromGraph does not work and the Ordered_seg_graph does not contain all the attributes. Not sure why this is happening.

All the code can run after withou errors until CumulativeSegmentationGraph where 'order' is an issue in edge_list.sort. Presumably because order does not exist due to earlier error.
