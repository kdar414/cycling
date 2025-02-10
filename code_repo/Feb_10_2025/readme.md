**Starting notes** 
- Segmentation code appears to work for the ngapipi data, next step is to interpolate
- Need to join the mapmatched data with the pollution data at some point but not sure when it is best to do so.
- Going to progress with the test data for now (ngapipi) and once this is working try with the cycling data

**Joining pollution and mapmatched data**
- Need to join mapmatched points and pollution data, not sure the best way to go about this. Think is needs to be in a dictionary form similar to the output of the mapmatched nested dictionary.
- Have the mapmatched data as a dictionary, with filter_xy_tuple (unmatched coordinates), use this to join to the pollution data?
- Should I be merging before or after the mapmatching process
- Looking into the pollution data in Maike 23/11/23
  * vaisala : collects CO<sub>2</sub> (ppm) and TGAS (<sup>o</sup>C). The log interval is 5 seconds
  * ptrack : collects concentration of ultrafine particles. The log interval is 1 second
  * atmotube : collects temperature, humidity, PM 1, 2.5 and 10. The log interval is 1 second.
  * GPS : collects location. The log interval is 1 second.


**Interpolation**
- The code chunks for voronoi, IDW and kriging all appear to work on the test data (ngapipi) and with artificial NO<sub>2</sub> data.
  * voronoi assigned neighbouring NO<sub>2</sub>
  * IDW appears to be working
  * Kriging assigns the same pollution value to all the rows
 


![Voronoi_output](https://github.com/user-attachments/assets/feada67c-496c-4032-b777-eee2e52bd92d) ![IDW output](https://github.com/user-attachments/assets/7a937d71-cb92-413c-9f8e-b4bfb985afbf) ![Kriging output](https://github.com/user-attachments/assets/a9d6abae-691d-4112-9a6e-bcaca78dfd50) ![All interpolation output](https://github.com/user-attachments/assets/dd8ecc8c-6ee9-4700-8917-106c267e0308)



  

- No spatial information is associated with the results at the moment but the index and seg_group are shared with other dataframes.
- Testing on IDW_NO2 for now because the "all" table (from the last function) has 3 million rows and the kriging has double contained in the centroids data.
- When plotting the IDW an error is visualised, although the code runs the points are no longer mapmatched to anything (see below).

![Screen Shot 2025-02-10 at 13 27 52](https://github.com/user-attachments/assets/ae07dcad-51ea-489b-b2db-aa7e9898c997)

- I think that this is related to the centroid functions:
```
import geopandas as gpd
import copy
from shapely.geometry import Point, LineString

def GetLineCentroids(segments: gpd.GeoDataFrame, return_shapely: bool = False,
                     return_gdf: bool = True):
    start_points = []
    end_points = []
    centroids = []
    seg_uids = list(segments['seg_uid'])

    for geom in segments['geometry']:
        if isinstance(geom, LineString) and len(geom.coords) > 1:
            start, end = Point(geom.coords[0]), Point(geom.coords[-1])  # Properly fetch first & last coordinate
        else:
            continue  # Skip invalid geometries

        centroid = geom.centroid

        start_points.append(start if return_shapely else (start.x, start.y))
        end_points.append(end if return_shapely else (end.x, end.y))
        centroids.append(centroid if return_shapely else (centroid.x, centroid.y))

    if return_gdf:
        w_segs = copy.deepcopy(segments)
        w_segs['centroid'] = centroids
        return w_segs
    else:
        return seg_uids, start_points, end_points, centroids

# Assuming `ride_segments` is defined as a GeoDataFrame
Line_centroids = GetLineCentroids(ride_segments)

```
and/or 

```
def GetLineStringCentroids(segments:gpd.GeoDataFrame):
    w_segs = copy.deepcopy(segments)

    w_segs['line_string_centroid'] = w_segs.interpolate(0.5, normalized=True)

    return w_segs

Line_string_centroids = GetLineStringCentroids(Line_centroids)
```

- I tested the original coordinates that the centroids are based on (looking back at how *ride_segments* was created and plotted the ngapipi data. The mapmatched (match_xy_tuple) is correctly matched so somewhere along the way something is going on. I am going to try and create a new geometry column based on the match_xy_tuple data and feed that into the centroids to see if it makes a difference.

  ![mapmatched coordinates plotted](https://github.com/user-attachments/assets/cfd82082-aa05-4134-b566-d9650c0bccce)

- Also investigated what **tracksegs_gdf** actually refers to:
  * It is associated with [cnt_attr]: this is the centroid column
  * The column appears in both **def GetLineCentroids** and **def GetLineStringCentroids** so both may need to be tested to work out which one is needed for the interpolation techniques.


**Segmentation**
- I am also trying to the run the **def GetGraph** function using 'topologic' to see if it will complete. Likely the better output to use for the interpolation.
- Once done the code to create the new geometry column as discussed will run and I can test the centroids again to see if they have worked better or not. 
