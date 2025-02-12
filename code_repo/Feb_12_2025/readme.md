- It appears that the error in the graph network occurs during the conversion of Ordered_seg_graph to a gdf in the function def SegGDFFromGraph
- The Segment_gdf comes out as:
![image](https://github.com/user-attachments/assets/d2c4e693-7466-44bd-acbd-30029b68f6d9)
- I tried a different way of converting it to a gdf using
```
import momepy
nodes_gdf, edges_gdf = momepy.nx_to_gdf(Ordered_seg_graph)
edges_gdf.plot()
nodes_gdf.plot()

#On the same axis
fig, ax = plt.subplots(figsize=(10, 10))
edges_gdf.plot(ax=ax, color="black", linewidth=1)
nodes_gdf.plot(ax=ax, color="red", markersize=5)
plt.show()

```

| Edges       |  Nodes |
:-------------------------:|:-------------------------:
![image](https://github.com/user-attachments/assets/c2933c8a-5c37-4943-a31a-923fbe275832)|![image](https://github.com/user-attachments/assets/41e3bf24-e6fd-46f8-b086-57f909672905)

![image](https://github.com/user-attachments/assets/547d257b-7832-416f-b606-9247eba50b84)
