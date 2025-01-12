# [Map-matching for cycling travel data in urban area](https://ietresearch.onlinelibrary.wiley.com/doi/pdfdirect/10.1049/itr2.12567)

## Abstract
- Bike friendly policies are being adopted in lines with increasing sustainability: GPS trajectors are a vital data resource
- Mapmatching helps to deal with errors of GPS data as a preprocessing step
- There can be errors associated with accurately selecting the best-mapped route based on:
  - GPS malfunction
  - ambiguity for road network for cyclists
  - inaccuracies in publically accessible streetmaps 
- These issues can be compounded in urban environments with high buildings and complex road networks.
- It is necessary to have a reliable classification of road availability for cyclists and a map-matching scoring system.

## Introduction
- This study uses OSM data
- BBBike for OSM data extraction
- Map-matching quality influenced by GPS drift and building disturbances
- There are few algorithms dedicated to bike map-matching, the majority focused on driving.
- Most methods use information on OSM which labels the roads as bike suitable or not.

## Background
- Mapmatching is broadly classified into three types; 1) geometric, 2) topological & 3) advanced algorithms
- *Geometric methods*: match GPS records to the newarst network elements (nodes or edges) based on distance. Accuracy heavily relies on precision of GPS data.
- *Topological methods*: Analyse sequences of GPS records and the network's connectivity.
- *Advanced methods*: integrate geometric and topological approaches such as Hidden Markov Models (HMMs)
    - HMMs: model the road segment to be mapped in the network as a state. The state probability indicating the liklihood of observing the provided GPS record under the condition that the bicyle is on the corresponding segment.
 - Cyclists can use a mix of routes mixing car, pedestrian and cycle lanes making it more difficult to determine the route a cyclist has taken.
