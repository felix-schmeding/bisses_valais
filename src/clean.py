import pandas as pd
import shapely
from shapely.ops import nearest_points
from shapely.geometry import Point
import geopandas as gpd
import os
import json

import src.section as section


def clean_list_json(list_dict, path_bisse, path_save, bisse_line, save_shp=False):
    json_for_plot = {}
    for key, data in list_dict.items():
        load_path = os.path.join(path_bisse, os.path.normpath(data['raw']))
        raw_shp = gpd.read_file(load_path).to_crs('EPSG:2056') # to swiss projection
        if data['type_donnee'] == 'point':
            clean_df = clean_snap_pointvalue(raw_shp, bisse_line)
        elif data['type_donnee'] == 'section':
            clean_df = clean_sections(raw_shp, bisse_line)
            #clean_df = clean_snap_pointvalue(clean_df, bisse_line)

            clean_df = section.create_sections(clean_df, prio='fin_debut')

        file_path = os.path.join(os.path.normpath(path_save), data['nom_indice'])
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        file_name = os.path.join(file_path, key +'.csv')

        # ! need to create dict
        json_for_plot[key] = {
            "nom_indice":data['nom_indice'],
            "type_donnee":data['type_donnee'],
            "format_donnee": data['format_donnee'],
            "path": file_name
        }

        clean_df.to_csv(file_name)
    
    results_json = json.dumps(json_for_plot, indent=2)

    with open(os.path.join(path_save, 'plot.json'), 'w') as file:
        file.write(results_json)



def clean_snap_pointvalue(meas_gdf, line):
    # * projecting points onto line
    # save initial geometry if needed later
    meas_gdf['geometry_raw'] = shapely.get_coordinates(meas_gdf['geometry']).tolist()
    meas_gdf = meas_gdf.set_geometry(nearest_points(line, meas_gdf.geometry)[0])

    # creating column with distance from start
    meas_gdf = meas_gdf.assign(dist_m = lambda x: shapely.line_locate_point(line, x.geometry))
    # only concerns start and end points
    meas_gdf = meas_gdf.drop_duplicates(subset=['dist_m'], keep='last') #! last because the added points are at the end of meas_df
    meas_gdf = meas_gdf.sort_values(by=['dist_m']).reset_index(drop=True)
    
    # ! drop les points qui sont plus loin que X mètres du tracé
    return meas_gdf

def  clean_sections(meas_gdf, line, columns_sec=['val_av', 'val_ap']):
    """
    Adjusts start and end point
    
    Args:
        meas_gdf (GeoDataFrame): GeoDataFrame with Point geometries.
        line (LineString): The reference line.
    
    Returns:
        GeoDataFrame: Cleaned GeoDataFrame with start and end point.
    """

    df_new = meas_gdf.dropna(subset=columns_sec, how='all').copy().reset_index(drop=True)

    if len(columns_sec) == 2: # that means val before and val after
        filter = df_new[columns_sec[0]].isna()#.any(axis=1)
        df_new.loc[filter, columns_sec[0]] = df_new.loc[filter, columns_sec[1]]
        filter = df_new[columns_sec[1]].isna()#.any(axis=1)
        df_new.loc[filter, columns_sec[1]] = df_new.loc[filter, columns_sec[0]]

    if not line.is_valid:
        raise ValueError("LineString geometry is invalid")
    
    # Get the start and end point of the LineString
    start_point = Point(line.coords[0])
    end_point = Point(line.coords[-1])
    
    # Find closest measurements to start and end
    # ! raw geometry 
    df_new["dist_to_start"] = df_new.geometry.distance(start_point)
    df_new["dist_to_end"] = df_new.geometry.distance(end_point)
    
    start_idx = df_new.loc[:, "dist_to_start"].idxmin()
    end_idx = df_new.loc[:, "dist_to_end"].idxmin()

    # place end point on line, with val before = val after of last measured point
    # same for start
    start_end_df = df_new.iloc[[start_idx, end_idx], :]

    # modify start and end
    # No need to check if valid data, if None it will be handled later
    # ! what if there is a non value entered ?
    start_end_df.loc[start_idx, columns_sec[0]] = None
    start_end_df.loc[start_idx, columns_sec[1]] = df_new.loc[start_idx, columns_sec[0]] # in theory val after is val before 
    start_end_df.loc[start_idx, 'geometry'] = start_point

    start_end_df.loc[end_idx, columns_sec[0]] = df_new.loc[end_idx, columns_sec[1]]
    start_end_df.loc[end_idx, columns_sec[1]] = None
    start_end_df.loc[end_idx, 'geometry'] = end_point

    # don't sort yet because we handle duplicates later and need start/end at the end of df
    df_new = gpd.GeoDataFrame(
         pd.concat([df_new, start_end_df], ignore_index=True), 
         crs=df_new.crs
         ).drop(columns=["dist_to_start", "dist_to_end"])

    #return df_new
    return clean_snap_pointvalue(df_new, line)