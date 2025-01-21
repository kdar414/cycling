**Mapmatching and Segmentation**
- The mapmatching is slightly off (~0.06m) likely due to **the number of decimal places** ![Screen Shot 2025-01-21 at 11 51 14](https://github.com/user-attachments/assets/5fcfdf71-bc2b-4042-b8dd-0b9eed71708d) (green is raw, pink is mapmatched and the lines are a clipped section of the road network)
- I have adjsuted this in the mapmatching code to have 50 or 100 decimal places and currently storing this as a csv.
- **New problem** the conversion of the match_xy_tuple to points in python is truncating the decimal places so the same issue in the segmentation will occur. Additionally when visualising this in QGIS it also limits the number of decimal places.
