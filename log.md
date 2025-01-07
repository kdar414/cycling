**06/12/24**

<ins>*MAPMATCHING*</ins>

- I have located Sophie's mapmatching information - she has tested a bunch of options and appears to have narrowed it down to <ins>ORSM and Leuvenmapmatching</ins>

  - Concerns about OSRM last linked to accuracy - the results are dependent on GPS accuracy. This can sometimes result in mapmatching to          the path not a road but cannot remove these as cycling can be on the path.
  - Concerns about Leuvenmapmatching related to difficulty of precise mapmatching.
  - **Overall leaning towards OSRM** but waiting for an issue associated with unnamed roads to be addressed.
  - Information accessed from **cycling-pollution-sophie/code/_old/code_notes.txt** and **code/_old/mapmatching_testing.py**
 
- I think the .lua file is related to docker but not entirely sure what is in it.
- I am going to set up the ORSM image in docker - to see if I can get it running.

**09/12/24**
<ins>*MAPMATCHING UPDATES*</ins>

- I have been trying to set up OSRM following this video ([https://www.youtube.com/watch?v=VQXlbqKArFk](url)) - I can get the example to work for the video (which shows you how to use the directing function rather than snapping function)
- I am trying to follow the video but route between two points in Auckland but I cannot get the code to use the map that I have downloaded.
    -  I have moved the new-zeland-latest.osm.pbf into the openrouteservice folder and have adjusted it in the config and docker file.
    -  This is the current issue I am dealing with ![Alt text]
    -  (relative%20path/to/img.jpg?raw=true "What I am stuck on at the moment")
![alt text](https://github.com/kdar414/cycling/blob/[branch]/image.jpg?raw=true)

**07/01/25**
The issue with not snapping to the cycle lane at the start of the day appears to have been addressed by changing the network in use. The previous issue was caused by using a map created with a car.lua, this current code references the map created using a bicycle.lua

 
| Map matching issue in the morning (car.lua likely)  | Adjustment - map matching produced now from code (bike.lua) |
| ------------- | ------------- |
| ![Map matching issue in the morning (car.lua likely)](https://github.com/user-attachments/assets/9ef6d4af-9ef9-47a4-9a40-bd65dbe292a8)  | ![Adjustment - map matching produced now from code (bike.lua)](https://github.com/user-attachments/assets/d0cb8ab9-6636-4744-8b3d-5c0832795abb)  |


**mapmatching_code_7_Jan.py** - contains the code that was working to do mapmatching on the date of the filename. The sudo docker at the start must be entered into terminal before running the code.

**html files** are the output maps showing the mapmatching - they contain:
  the date of creation
  an r value which stands for radius e.g. in this file route_map_osrm-docker_7_Jan_r10.html the radius was 10 meters

**08/01/25**

*Map matching*
- Running the mapmatching code from 07/01 using r = 50. Started running at 8 am - will see if it is successful
- Map matching from 07/01 improved success but with some issues with cyclist shown to be on the water near Hobson point.

*Segementation*
- Working on segmentation whilst mapmatching is running in the background.
- Looks like I need to use OSMnx to get a graph to put into graph_manipulation.py. 
