The issue with not snapping to the cycle lane at the start of the day appears to have been addressed by changing the network in use. The previous issue was caused by using a map created with a car.lua, this current code references the map created using a bicycle.lua

 
| Map matching issue in the morning (car.lua likely)  | Adjustment - map matching produced now from code (bike.lua) |
| ------------- | ------------- |
| ![Map matching issue in the morning (car.lua likely)](https://github.com/user-attachments/assets/9ef6d4af-9ef9-47a4-9a40-bd65dbe292a8)  | ![Adjustment - map matching produced now from code (bike.lua)](https://github.com/user-attachments/assets/d0cb8ab9-6636-4744-8b3d-5c0832795abb)  |


**mapmatching_code_7_Jan.py** - contains the code that was working to do mapmatching on the date of the filename. The sudo docker at the start must be entered into terminal before running the code.

**html files** are the output maps showing the mapmatching - they contain:
  the date of creation
  an r value which stands for radius e.g. in this file route_map_osrm-docker_7_Jan_r10.html the radius was 10 meters

