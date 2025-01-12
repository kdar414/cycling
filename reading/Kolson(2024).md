## Methods
### **Segmentation**
#### Creating segments
- Road network made up to a graph of edges and nodes. It may be made of multiple edges with different lengths depending on the layout.
- Algorithm checks the length of the edges on each road and adds nodes so that segments are all the wanted **length (l)**
- Edges that connect a simple graph are **node-to-node (u to v)**
- When defining a new node so that the segments have the same length the following equations are used:
		- where *p is a new point between u and v*, *x,y are node position* and *d is the distance between the nodes*. The new edge *x<sub>u</sub>,y<sub>u</sub> to x<sub>p</sub>,y<sub>p</sub>* is a spatial segment

<p align = "center"><img width = "300" src = "https://github.com/user-attachments/assets/aeaa42f7-832a-4af1-a45d-7eda4270f371" alt = "Equation1")</p>

- When this is applied to the whole network the edges will be as close to l as possible.

#### Edge grouping
- Two methods:
- Independent-edge segmentation (IES): segements are created along each edge independently. There are no forms of grouping and relationships between edges are not maintained.
  		- Grouped-edge segmentation (GES): edges are grouped by certain attributes and can span across mutiple edges. The networks are saves as linestring geometry.

- In segementation 
		- 1) Set of roads are converted to a graph. 
		- 2) The distance between the two nodes of the first edge is calculated. If the distance if less than *l* then a new node *p* is created.
				- the remaining distance between *p* and the next node is calculated.
						- if it is less than *l* then no new node is created.
						- if is it greater than *l* a new node is created.
		- 3) This is repeated until the final node is reached.

- In IES these steps are performed on every edge until the network is fully segmented resulting in segments that terminate at each node of the original network.

- In GES if the distances between nodes (*d*) is lower than *l*, the difference between *l* and *d* is used to calculate the length of the next node in the group.
		- This results in segments that can have several *u v* pairs.

- Grouped edges through topological continuity and road names
		- Topological (TGES): groups edges as continuous sets of non-intersecting edges.

				- This is determined by edges with degrees or the number of connected edges <=2

		- Named topological (NTGES): uses the same intersection rule but oders groups based on the position along a road, assuming that edges with the same street name belong to the same road
				- this requires that all the streets have street names which is not always the case for OSM

- Terminating segements at intersections is essential for comparison across studies: stops someone entering a pathwat partway down the length
	
		- does not accound for a trajectory starting partway down a segment

		- the order of edges along a road are segmented is achieved using a depth-first search: isolating grouped edges as a sub-graph traversed unti every edge is reached without back-tracking

				- the sequence of the final traversal is used as the order of segmentation.

<p align = 'center'><img width = 500 src = "https://github.com/user-attachments/assets/1f58d8a5-cc71-4b9a-b9a6-79a01138a9ee")</p>


**Interpolation**

#### Temporal interval modification

- Assess the impact of sensing frequency on pollution exposure and dosage: 
		- tested by reducing the number of points in the source data which mimics a lower sensing frequency.


#### Spatial interpolation

- Estimate pollutant values at unsampled locations
- Three methods:
		- **voronoi** (nearest-neighbour):
				- every segment centroid that falls within a polygon is assigned the pollutat value of that corresponding point

				- This can also be described as a spatial join with the *'nearest'* predicate. i.e. values that are not the nearest are ignored

				- Limitation in that you only select a single value (Xie *et al*., 2017)

		- **inverse distance weighting (IDW)**:
				- assigns a weight to a point where the weight decreases with increasing distance (based on Tobler's First Law) 

		- **kriging**
				- geostatistical method using the same formula as IDW but uses the weighting differently.

				- In kriging the sampled points are fitted to a curve to describe their natural variance
						- weights of estimations are based on the spatial arrangement (curve) of observations, rather than a model of nonvariant spatial autocorrelation as assumed with IDW.

#### Dosage model
- Exposure = concentation of a given polluatnt in the enviornment of a subject.
- Dosage = the amount of pollutant they are inhaling when taking into account their minute ventilation and the exposure duration (Dirks *et al.*, 2012)
- Dosage is more relevant for assessing physiological consequences of a polluted environment.
- For this study dosage is calculated as: (derived from Dirks et al (2012); Wang et al (2018))

d = l/v * c

- Uses time exposed and measured concentration *(c)* to calculated dosage *(d)*.
	- Where time exposed could be:
			- distance long a road segment *(l)*
			- travel speed or a time measurement *(v)*

- Dosage calculated as the number of particles inhaled are UFP counts


## Results
- Segmentation and interpolation methods affect the spatial distribution of the calculated dosage on different trajectories
- Temporal interval of pollutant data had a low impact on dosage calculations
- Spatial segment length had a larger impact - average dosage increased significantly with segment length

- Interpolating with kriging data to segments with Krigin consistently resulted in higher dosage and concentration values compared to voronoi and IDW

- Average particle concentrations varied with temporal interval, with t= 60s resulting in a much lower concentration compared to other intervals across all interpolation methods. 


## Discussion (just picked out some of the details)
- Temporal interval of pollutant data has a smaller impact on dosage and total concentration than choice of spatial segement length (non-linear)

- Interpolation method used for estimations significantly influences concentration and dosage metrics: all leading to different results
	- expected due to different underlying assumptions
	- Kriging: more consistent trends as a result of changing temporal and spatial segment lengths
			- likely to account for uncertainties in measurements

	- Voronoi: displays the least consistent trends likely to be more strongly influenced by outliers
	- IDW and kriging performed similarly, voronoi lower likely because it cannout account for spatial variance

- Dosage calculation here is highly dependent on spatial segement length and the temporal interval
	- model uses *l* as a numberator so the calculation cannot be accurately compared between different values of *l*.

- Erroneous map-matching: impacting on segmented network length. 
		- If a point is assigned to the wrong road segments are produced to this point which can increase the route length
