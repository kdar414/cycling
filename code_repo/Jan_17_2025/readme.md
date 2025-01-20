**Mapmatching**
- mapmatching started at 08:06 and finished 13:43 with r = 50
- Saved mapmatched r50 as pickle file (match_xy_tuples, filter_xy_tuples and all as csv in troubleshoot and saved as mapmatching_17_01_2025.py

**Segmentation**
- Still cannot find segments still - plotted the edges and mapmatched points and they overlap. I think this is an issue with the code. I am trying to work out if there is something missing.
- checking if coordinates exist in any edge: all say segment not found for (coord1, coord2).
- Ok so nothing can be linked but when a buffer is added the segments can be found. I am wondering if the issue is related to the mapmatched points I am using having a radius of 10 (not entirely syre that this is the issue.)
- Used the mapmatched points with r50 and the same issue arose.
- This is what I tried
    1) *Make gdf for edges*. Get the coordinates from 'track_id' in map_matched_tracks. Create gdf for non_matched points. Assigned crs 4326. I visualised this and shows edges with unpatched segments overlaying them. ![Screen Shot 2025-01-17 at 08 35 22](https://github.com/user-attachments/assets/782aa159-fe09-47c6-9b8b-010b6d49d062)
    2) Then I tried to find distance between edges and points but there was no output. I checked the validity of unmatched_segments_gdf -> all true.
    3) Tried plotting again after checking the crs of gdf_edges and unmatched_segments_gdf were same. Both '4326' but all still visualised as unmatched segments.
    4) Checked if the coordinates of matched points exist in any edge and they did not. "Segment not found for (lat, long).
    5) Checked the start and end for each edge -> all successfully identified.
    6) *Tried to add a buffer* of 1e-4 (adjusting the match radius) and plotted it and then **segments were found** for all. Seems that the buffer is necessary but I do not understand why the buffer is needed when the points have been mapmatched.
  
