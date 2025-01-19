# %%
import requests
from shapely.geometry import Point
import copy
import time
import os
import geopandas as gpd
import csv

# %%
'''
sudo docker run -t -i -p 5000:5000 -v "/Users/kad/osrm-docker:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/new-zealand-latest.osrm --max-matching-size 20000
'''

# %%
import pandas as pd

gps = pd.read_csv('/Users/kad/Desktop/cyclists/chloes_files/Trips with data/Maike/23-11-2023/mgat-Uoa-TamakiDrive-Uoa_23-11-2023-gps_1.csv')
gps_cleaned = gps.dropna(axis=1)  #removing columns with NA
coordinates_gps = gps_cleaned[["LONGITUDE","LATITUDE"]].apply(tuple, axis=1)
#coordinates_gps = gps_cleaned.apply(tuple, axis=1)
#gps_track = coordinates_gps.to_dict()
# Create a dictionary for the single track with the coordinates
gps_track_dict = {
    "track_id": {
        "filter_xy_tuple":list(coordinates_gps)
    }
}

print(gps_track_dict)  # This is the format you need to pass to MapMatchTracks

# %%

# Open Source Routing Machine Map Matcher
#   -calls local OSRM server match API
#   -converts track geometry to query format
#   -local server must be running for this to function
def MapMatcher(track:dict, xy_col:str='filter_xy_tuple', host:str='http://127.0.0.1:5000', 
                invalid_value:any=-9999, debug:bool=False, config_suffix:str='', 
                radius_m:int=5, out_prefix:str='match_', debug_mode:str='full'):
    geom_string = ''
    radius_string = '&radiuses='

    # format x and y into string for query
    #   can probably do this in one line
    count = 1
    for x, y in track[xy_col]:
        # final substring in sequence has no semicolon 
        if count == len(track[xy_col]):
            geom_string += f'{x},{y}{config_suffix}{radius_string}'
        else:
            geom_string += f'{x},{y};'
            radius_string += str(radius_m) + ';'
        count += 1

    # format query
    query = f'{host}/match/v1/bike/{geom_string}'
    if debug and debug_mode == 'full':
        print('Executing query: ', query)
    start_time = time.time()

    # execute request
    try:
        query_result = requests.get(query).json()

        match_points = query_result['tracepoints']
        matches = {
            f'{out_prefix}xy_tuple': [],
            f'{out_prefix}geometry': [],
            f'{out_prefix}roadname': [],
            f'{out_prefix}distance': []
        }

        nomatch_count = 0

        for point in match_points:
            try:
                # point keys, alternatives_count, waypoint_index, matchings_index, location, name, distance, hint
                x, y = point['location'][0], point['location'][1] # do I need to write this twice
                matches[f'{out_prefix}xy_tuple'].append((x, y))
                matches[f'{out_prefix}roadname'].append(point['name'])
                matches[f'{out_prefix}distance'].append(point['distance'])
                matches[f'{out_prefix}geometry'].append(Point(x, y))
                
            except Exception as e:
                nomatch_count += 1

                # could loop this, but not much advantage given I don't want to loop above
                matches[f'{out_prefix}xy_tuple'].append(invalid_value)
                matches[f'{out_prefix}geometry'].append(invalid_value)
                matches[f'{out_prefix}roadname'].append(invalid_value)
                matches[f'{out_prefix}distance'].append(invalid_value)
        if debug:
            total_time = round(time.time() - start_time, 1)
            points_per_second = round(len(match_points) / total_time, 1)
            # what is going on with this f string? am I missing something? for the life of me can't figure out why im getting a syntax error
            # print(f'matched {len(match_points)} of {track['xy_tuple']} source points')
            print(f'Matched {str(len(match_points) - nomatch_count)} of {str(len(match_points))} source '
                    f'points ({str(nomatch_count)} invalid points) in {str(total_time)}s '
                    f'({str(points_per_second)} points per second)')

            debug_data = {
                'query_result': query_result,
                'total_time': total_time, 
                'points_per_second': points_per_second,
                'total_points': len(match_points),
                'invalid_points': nomatch_count
            }
            return matches, debug_data
    
        else:
            return matches
    except:
        raise ConnectionError('Request failed. Is the docker image running?')


# Map Match Tracks
# runs MapMatcher on the track dictionary
# debug mode needs work
def MapMatchTracks(tracks:dict, radius_m:int=5, annotations:bool=True, steps:bool=False, 
                    geometries:str='geojson', debug:bool=False, nomatch_val:any=-9999, 
                    remove_invalids:bool=False, out_prefix:str='match_', in_prefix:str='filter_',
                    debug_mode:str='full'):

    w_tracks = copy.deepcopy(tracks)

    # build suffix for osrm (convert parameters to the syntax osrm requires)
    steps_str = 'true' if steps else 'false'
    config_suffix = f'?annotations=nodes&steps={steps_str}&geometries={geometries}&overview=full'
    xy_col = f'{in_prefix}xy_tuple'

    # match each track
    for name, track in w_tracks.items():
        if debug:
            print(f'Map matching track: "{name}"')
            match_results, debug_data = MapMatcher(track, radius_m=radius_m, invalid_value=nomatch_val,
                                                     debug=True, config_suffix=config_suffix, out_prefix=out_prefix,
                                                     xy_col=xy_col, debug_mode=debug_mode)
        else:
            match_results = MapMatcher(track, radius_m=radius_m, invalid_value=nomatch_val, debug=False, 
                                        config_suffix=config_suffix, out_prefix=out_prefix, xy_col=xy_col)

        track[f'{out_prefix}xy_tuple'] = match_results[f'{out_prefix}xy_tuple'].copy()
        track[f'{out_prefix}geometry'] = match_results[f'{out_prefix}geometry'].copy()
        track[f'{out_prefix}roadname'] = match_results[f'{out_prefix}roadname'].copy()
        track[f'{out_prefix}distance'] = match_results[f'{out_prefix}distance'].copy()

        # remove values that could not be matched
        if remove_invalids:
            track[f'{out_prefix}datetime'] = (track[f'{in_prefix}datetime']).copy()

            invalid_indices = [index for index, value in enumerate(track[f'{out_prefix}xy_tuple']) if value == nomatch_val]

            for i in sorted(invalid_indices, reverse=True):
                # this assumes index is accurate 
                del track[f'{out_prefix}datetime'][i]
                del track[f'{out_prefix}xy_tuple'][i]
                del track[f'{out_prefix}geometry'][i]
                del track[f'{out_prefix}roadname'][i]
                del track[f'{out_prefix}distance'][i]
    
    if debug:
        return w_tracks, debug_data
    else:
        return w_tracks
    
# Call the MapMatchTracks function with the single track
matched_tracks = MapMatchTracks(
    tracks=gps_track_dict,        # The dictionary with the single track
    radius_m=50,          # Match radius in meters
    debug=True,          # Enable debug mode for detailed output
    nomatch_val=-9999,   # Value for unmatched points
    out_prefix="match_", # Prefix for output keys
    in_prefix="filter_"  # Prefix for input keys
)

# Print the matched track results
print(matched_tracks)


# %% Creating a dictionary of the results
# Extract track_id and its associated data
matched_tracks_dict = matched_tracks[0]
track_id = matched_tracks_dict['track_id']
filter_xy_tuple = track_id['filter_xy_tuple']  # Example of accessing filter_xy_tuple
match_xy_tuple = track_id['match_xy_tuple']

# %%

gdf = pd.DataFrame(match_xy_tuple)
gdf.rename(columns = {0:'matched_longitude', 1:'matched_latitude'}, inplace = True)
gdf_filter = pd.DataFrame.from_dict(filter_xy_tuple)
gdf_filter.rename(columns = {0:'original_longitude', 1:'original_latitude'}, inplace = True)
gdf_all = pd.DataFrame.from_dict(matched_tracks_dict)


coordinates = gdf.join(gdf_filter, how = 'outer')

gdf.to_csv('/Users/kad/Desktop/cyclists/Kimberley/segmentation/troubleshoot/matched_xy_r50.csv')
gdf_filter.to_csv('/Users/kad/Desktop/cyclists/Kimberley/segmentation/troubleshoot/filter_xy_r50.csv')
gdf_all.to_csv('/Users/kad/Desktop/cyclists/Kimberley/segmentation/troubleshoot/mapmatched_r50.csv')
# %% Exporting the dictionary so it can be used for segmentation
import pickle
with open('/Users/kad/Desktop/cyclists/Kimberley/segmentation/troubleshoot/matched_dict_tracksMaike_23-11-23_r50', 'wb') as file:
    pickle.dump(matched_tracks_dict, file)


# %%
# Save Tracks
# save processed tracks as something we can read later on
#   - csv columns need to be constant so that we can mess with them consistently (averages)
def SaveTracks(tracks:dict, out_folder:str, suffix:str, in_prefix:str='match_', 
                out_crs:str='EPSG:4326', out_format:str='csv', 
                csv_cols=['datetime', 'geometry', 'x', 'y', 'no2', 'seg_id'], 
                gpkg_cols:list=['null'], fix_nofolder:bool=True):

    if fix_nofolder:
        if not os.path.isdir(out_folder):
            os.makedirs(out_folder)

    for name, track in tracks.items():     

        if out_format == 'gpkg':
            w_track = {key: track[key] for key in gpkg_cols}
            gdf = gpd.GeoDataFrame(w_track, geometry=f'{in_prefix}geometry', crs='EPSG:4326')

            if not out_crs == 'EPSG:4326':
                gdf = gdf.to_crs(out_crs)
            
            filename = out_folder + os.path.basename(name).strip('.gpx').strip('.csv') + suffix + '.gpkg'
            gdf.to_file(filename, driver='GPKG', crs=out_crs)

        elif out_format == 'csv':
            filename = out_folder + os.path.basename(name).strip('.gpx').strip('.csv') + suffix + '.csv'

            if not os.path.isfile(filename):
                header = ['fid'] + csv_cols
                with open(filename, 'w', encoding='UTF8', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(header)

                    for i in range(len(track[f'{in_prefix}datetime'])):
                        row = [i]
                        for col in csv_cols:
                            if col == 'x':
                                row_val = track[f'{in_prefix}xy_tuple'][i][0]
                            elif col == 'y':
                                row_val = track[f'{in_prefix}xy_tuple'][i][1]
                            else:
                                row_val = track[f'{in_prefix}{col}'][i]
                            row.append(row_val)
                            
                        writer.writerow(row)
            else:
                print(f'File "{filename}" already exists')

matched_tracks

saved = SaveTracks(tracks = matched_tracks_dict, out_folder = '/Users/kad/Desktop/cyclists/Kimberley/segmentation/troubleshoot' , suffix = 'matched_23_11_23',
                csv_cols=['datetime', 'geometry', 'x', 'y', 'no2', 'seg_id'])
# %%
