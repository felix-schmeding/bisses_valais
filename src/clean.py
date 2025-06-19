import pandas as pd
import shapely
from shapely.ops import nearest_points
from shapely.geometry import Point
import geopandas as gpd
import os
import json

import src.section as section

# needs to be updated by main script
# alternatively pass to functions individually, but as it is supposed to be constant it can be a global variables
generic_json = {}


def clean_list_json(bisse_dict, couche_select, bisse_line, path_save, save_shp=False):
    """processes all the data that is listed in the couche of the dictionnary

    Args:
        bisse_dict (_type_): _description_
        path_bisse (_type_): _description_
        bisse_line (_type_): _description_
        path_save (_type_): _description_
        save_shp (bool, optional): if cleaned data is saved to shapefile or not. Defaults to False. (not implemented yet)
    """

    json_for_plot = {}
    for key, data in bisse_dict[couche_select].items():
        if data["raw"] == "":
            print(f"Skipping {key} as no data is available")
            continue

        load_path = os.path.normpath(os.path.join(bisse_dict["data_path"], data["raw"]))

        raw_shp = gpd.read_file(load_path).to_crs("EPSG:2056")  # to swiss projection

        # need to access generic json
        type_donnee = generic_json[couche_select][key]["type_donnee"]
        if type_donnee == "point":
            clean_df = clean_snap_pointvalue(raw_shp, bisse_line)
        elif type_donnee == "section":
            # ! if needed select col names here
            clean_df = clean_sections(raw_shp, bisse_line)
            # ! need to take 'prio' into account
            clean_df = section.create_sections(clean_df, prio="fin_debut")
        elif type_donnee == "surface":
            # load also the shapefile with the point data
            # so no need to process the point data, one new data for each surface value even if linked to same point value
            # save as point data
            link = generic_json[couche_select][key]["lien"]  # liste: ["couche", "key"]
            link_path = os.path.normpath(
                os.path.join(
                    bisse_dict["data_path"], bisse_dict[link[0]][link[1]]["raw"]
                )
            )
            link_shp = gpd.read_file(link_path).to_crs(
                "EPSG:2056"
            )  # to swiss projection
            # ! it is assumed that the link is a point data
            link_df = clean_snap_pointvalue(link_shp, bisse_line)

            raw_shp["surface"] = raw_shp.geometry.area  # Make sure CRS is in meters!
            col = generic_json[couche_select][key]["col"]
            # ! it is assumed first col is categorical, second numeric
            raw_shp.loc[:, col[1]] = raw_shp.loc[:, col[1]].apply(
                pd.to_numeric, errors="coerce"
            )

            # Step 2: Group by valve and crop type
            summary = (
                raw_shp.drop(columns=["geometry"])  # drop geometry
                .groupby(["link_id", col[0]])  # group by type
                .agg("sum")
                .reset_index()
            )

            # Step 5: Merge with valve GeoDataFrame (preserving valve geometry)
            clean_df = link_df.filter(["id", "dist_m"]).merge(
                summary, left_on="id", right_on="link_id", how="left"
            )

            # Optional: drop extra column
            clean_df = clean_df.drop(columns="link_id")

            # print("Surface not implemented yet")
        elif type_donnee == "unique":
            print("Val unique not implemented yet")

        file_path = os.path.join(
            os.path.normpath(path_save), generic_json[couche_select][key]["nom_indice"]
        )

        if not os.path.exists(file_path):
            os.makedirs(file_path)

        file_name = os.path.join(file_path, key + ".csv")

        # ! need to create dict, can be long and messy as it is only used to plot automaticcally later
        # json_for_plot[key] = {
        #     "nom_indice": generic_json[couche_select][key]["nom_indice"],
        #     "type_donnee": generic_json[couche_select][key]["type_donnee"],
        #     "format_donnee": generic_json[couche_select][key]["format_donnee"],
        #     "path": file_name,
        # }
        # # !or
        # copy all info from generic
        json_for_plot[key] = {k: v for k, v in generic_json[couche_select][key].items()}
        # add the path to the csv file
        json_for_plot[key]["path"] = file_name

        clean_df.to_csv(file_name)

    results_json = json.dumps(json_for_plot, indent=2)

    with open(os.path.join(path_save, "plot.json"), "w") as file:
        file.write(results_json)


def clean_snap_pointvalue(meas_gdf, line):
    # * projecting points onto line
    # save initial geometry if needed later
    meas_gdf["geometry_raw"] = shapely.get_coordinates(meas_gdf["geometry"]).tolist()
    meas_gdf = meas_gdf.set_geometry(nearest_points(line, meas_gdf.geometry)[0])

    # creating column with distance from start
    meas_gdf = meas_gdf.assign(
        dist_m=lambda x: shapely.line_locate_point(line, x.geometry)
    )
    # only concerns start and end points
    meas_gdf = meas_gdf.drop_duplicates(
        subset=["dist_m"], keep="last"
    )  #! last because the added points are at the end of meas_df
    meas_gdf = meas_gdf.sort_values(by=["dist_m"]).reset_index(drop=True)

    # ! drop les points qui sont plus loin que X mètres du tracé
    return meas_gdf


def clean_sections(meas_gdf, line, columns_sec=["val_av", "val_ap"]):
    """
    Adjusts start and end point

    Args:
        meas_gdf (GeoDataFrame): GeoDataFrame with Point geometries.
        line (LineString): The reference line.

    Returns:
        GeoDataFrame: Cleaned GeoDataFrame with start and end point.
    """

    df_new = (
        meas_gdf.dropna(subset=columns_sec, how="all").copy().reset_index(drop=True)
    )

    if len(columns_sec) == 2:  # that means val before and val after
        filter = df_new[columns_sec[0]].isna()  # .any(axis=1)
        df_new.loc[filter, columns_sec[0]] = df_new.loc[filter, columns_sec[1]]
        filter = df_new[columns_sec[1]].isna()  # .any(axis=1)
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
    start_end_df.loc[start_idx, columns_sec[1]] = df_new.loc[
        start_idx, columns_sec[0]
    ]  # in theory val after is val before
    start_end_df.loc[start_idx, "geometry"] = start_point

    start_end_df.loc[end_idx, columns_sec[0]] = df_new.loc[end_idx, columns_sec[1]]
    start_end_df.loc[end_idx, columns_sec[1]] = None
    start_end_df.loc[end_idx, "geometry"] = end_point

    # don't sort yet because we handle duplicates later and need start/end at the end of df
    df_new = gpd.GeoDataFrame(
        pd.concat([df_new, start_end_df], ignore_index=True), crs=df_new.crs
    ).drop(columns=["dist_to_start", "dist_to_end"])

    # return df_new
    return clean_snap_pointvalue(df_new, line)
