**Mapmatching**
- The code has worked today with a radius of 50 m but took 6.5 hours to run one gps file
- It looks more accurate, i.e. there is less bounce, but there are some changes along Tamaki drive compared to r=10 from 07/01. Where it used to snap to the cycle path now it is on the road. Not sure if the person cycled on the road or cycle path thought.
- I am wondering if timestamps should be included in the mapmatching
- I tried using the osrm_caller.py from Sophie to mapmatch as well,
        - I have only done it for r=5 and not mapped it. The results have been saved in as a csv and json called *matched_tracks080125.csv(.json)*. **I would like to map these results to see if there are differences associated with code**.
  
   
