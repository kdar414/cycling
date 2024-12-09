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
    -  This is the current issue I am dealing with ![What I am stuck on at the moment](https://github.com/kdar414/cycling/blob/images/issue_9_DEC.png)
          - The specific line that I am unsure about is **Update the file /home/ors/files/example-heidelberg.test.pbf with /heidelberg.test.pbf** 

- I decided to double check what happens when I put this into the browser http://localhost:8080/ors/v2/directions/driving-car?&start=174.862094,-36.849295&end=174.768500,-36.853737
    - This is what I was testing earlier to give directions from 17 Clarendon Road to the Science Building and ... **IT WORKS!**![Screen Shot 2024-12-09 at 13 10 36](https://github.com/user-attachments/assets/50abdbbc-c778-4093-b541-cc908a2c1a25)

- Next thing to do now is try and use the snap feature which attaches GPS points to roads (not sure if it does paths but we will find out!
      
