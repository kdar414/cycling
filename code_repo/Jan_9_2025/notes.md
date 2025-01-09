**Mapmatching**

- map matching is running on orsm caller with r= 100 - started at 08:12 am and finished at ______

- I have been trying to visualise and compare the mapmatched and the raw gps coordinates
  
- Something I learnt - the output contains the original (*filter_xy_tuple*) and matched coordinates (*match_xy_tuple*).

- Here are some observations:
      - extracting the coordinates from the json/csv is proving difficult
              - the json structure is wrong - might be because I downloaded it from github
              - The first 1000 coordinates for each dictionary (filter_xy_tuple, match_xy_tuple etc) 
              - I manually copied the match_xy_tuple from the csv file via bash
                      - *cat /Users/kad/Desktop/cyclists/Kimberley/mapmatching/osrm_caller/matched_tracks080125.csv*
                            - This allows all the data to be accessed and gets around the issue of only 1000 records being shown and everything else hidden behind ellipses (I checked that the length of the original matched the length of matched tuples"
              - I saved the match tuples as **match_xy_tuple.txt**

- The structure of the output is track_id_coordinates
                                        |__ filter_xy_tuple
                                        |__ match_xy_tuple (etc)

- Ok so once I extracted the match_xy_tuple I created a gdf with the matched and raw gps data and then created points for the raw and matched data.
- I have plotted the data on a map (*map_output.html*) - **blue is the original gps and red the mapmatched points**
  
![Example of mapmatch output](https://github.com/user-attachments/assets/44bf5fe9-3a71-4f9d-928e-2a8a04287181)

