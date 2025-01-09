**Mapmatching**
- The code has worked today with a radius of 50 m but took 6.5 hours to run one gps file
- It looks more accurate, i.e. there is less bounce, but there are some changes along Tamaki drive compared to r=10 from 07/01. Where it used to snap to the cycle path now it is on the road. Not sure if the person cycled on the road or cycle path thought.
- I am wondering if timestamps should be included in the mapmatching
- I tried using the osrm_caller.py from Sophie to mapmatch as well,
        - I have only done it for r=5 and not mapped it. The results have been saved in as a csv and json called *matched_tracks080125.csv(.json)* I have also added this to the folder to have a look at.
          - **I would like to map these results to see if there are differences associated with code**.
- I want to create a dataframe from the output to compare the original gps coordinates with the map matched ones and then calculate the distance between them to see if this is affecting the mapmatching location (e.g. at Tamaki drvie between the road and cycle lane match)
          - currently struggling to extract the output from the query into a df because there are multiple dictionaries within the output
  
| Index  | Original_coords |  Mapmatched_coords  | Distance_euclidean |
| ------------- | ------------- |------------- | ------------- |
|  |  | |  |    

**Segmentation**
- First look at segmenting the network after talking to Sila on Tuesday.
- This uses osmnx in python
- Sophie has segmenting functions in graph_manipulation.py.
- I have run the first part of this to create the graphml file.
          - I think this files contains nodes and edges for the area of interest using bbox to create a graph from the osm map
          - I have run two
                  - 1) Small bbox near uni
                  - 2) Larger bbox covering most of Auckland
- The osmnx package has recently been updated to version 2.0.0 (Nov 2024) - this affects the ox.graph_from_bbox function. I have downgraded to version 1.9.4 which runs the code Sophie wrote and provides depreciation warnings should it be better to update the code.
- Next step is to run through the next functions on segmentation until the first two of three types have been achieved.
- *Should I make the graph for Auckland all at once or should I do it as I process different gps trajectories?*

**Notes from the day**
- Road network = system of road segments and intersections. These are 'natural graphs' because the intersections are nodes and road segments are edges.
- Road segements have properties such as speed limit, road class, length, curvature
- Road network combines all of the segments, intersection and attributes. Some attributes are missing such as lane number, bear in mind that some things may be missing. 
