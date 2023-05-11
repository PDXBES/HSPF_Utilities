import geopandas as gpd
import pandas as pd
from rasterstats import zonal_stats
import fiona
import os
import shapely
from matplotlib import pyplot as plt
from PyQt5.QtWidgets import QApplication
from common.file_dialog import App
import sys

print(os.environ['PROJ_LIB'])
app = QApplication(sys.argv)
ex = App("EMGAATSGDB")
input_gdb = ex.model_file_path
model_directory = os.path.dirname(input_gdb)

sim_directory = model_directory + "\\sim"
hspf_directory = model_directory + "\\sim\\Hspf"
swmm_directory = model_directory + "\\sim\\SWMM"
overlay_gpk = model_directory +"\\overlay.gpkg"

overlay_file = hspf_directory + "\\HSPFOverlay.csv"
explicit_areas_file = swmm_directory + "\\explicit_areas_hspf.csv"
lumped_areas_file = swmm_directory + "\\swmm.hspf.csv"
#explicit_areas_unique_outlets_file = swmm_directory + "\\explicit_areas_unique_outlets_hspf.csv"
area_list = fiona.listlayers(input_gdb)

area_layer = "Areas"
directors_layer = "Directors"
nodes_layer = "Nodes"
links_layer = "Links"

raster = r'V:\HydroModHSPF\gis\tiff\OverlayWest_4_10_23.tif'

# df areas
areas = gpd.read_file(input_gdb, layer=area_layer)
nodes = gpd.read_file(input_gdb, layer=nodes_layer)
links = gpd.read_file(input_gdb, layer=links_layer)

# df directors
directors = gpd.read_file(input_gdb, layer=directors_layer)
storm_directors = directors[directors['director_type'] == 'Storm']
storm_directors = storm_directors[storm_directors['director_code'] != 'SEP']
storm_directors_area_ids = storm_directors['area_id'].values
unique_storm_directors_area_ids = set(storm_directors_area_ids)

# df lumped areas
lumped_areas = areas[areas['area_type'] == 'LUMP']
lumped_areas.to_file(overlay_gpk, layer='lumped_areas', driver="GPKG")
# df bldg strt parking areas
bldg_prkg_strt_areas = areas[areas['area_type'].isin(['BLDG', 'PRKG', 'STRT'])]

# explict areas
explicit_areas = bldg_prkg_strt_areas[bldg_prkg_strt_areas.area_id.isin(unique_storm_directors_area_ids)]
if not explicit_areas.empty:
    explicit_areas.to_file(overlay_gpk, layer='explicit_areas', driver="GPKG")

# subtract bldg strt parking areas from lumped areas
if not lumped_areas.empty and not explicit_areas.empty:
    cut = gpd.GeoDataFrame(geometry=gpd.GeoSeries(shapely.ops.unary_union(explicit_areas.geometry)), crs=explicit_areas.crs)
    cut.to_file(overlay_gpk, layer='cut', driver="GPKG")
    lumped_areas = gpd.overlay(lumped_areas, cut, how='difference')
    lumped_areas.to_file(overlay_gpk, layer='lumped_areas_erased', driver="GPKG")
    # lumped_areas.plot(color = 'red')
    # plt.show()

# all areas
if not lumped_areas.empty and not explicit_areas.empty:
    all_areas = lumped_areas.append(explicit_areas).reset_index(drop=True)
elif not lumped_areas.empty:
    all_areas = lumped_areas
elif not explicit_areas.empty:
    all_areas = explicit_areas
else:
    print('No Areas')
    quit()
all_areas.to_file(overlay_gpk, layer='all_areas', driver="GPKG")
all_areas_valid = all_areas[all_areas.geometry.is_valid]
all_areas_valid.to_file(overlay_gpk, layer='all_areas_valid', driver="GPKG")

zs = zonal_stats(vectors=all_areas['geometry'], raster=raster, categorical=True)
stats = pd.DataFrame(zs).fillna(0) #One column per raster category, and pixel count as value
stats = stats.set_index(all_areas.area_name).transpose()
stats.index = stats.index.set_names("LABEL")
stats = stats.reset_index()
stats.to_csv(overlay_file)


#TODO should adjust the areas to match the area after the explicit areas are cut out total aree=total area cut
#TODO suro ifwo agwo areas multiplied by total area cut/total are original

if not lumped_areas.empty:
    storm_directors_lumped_areas_no_node_names = storm_directors.merge(lumped_areas, how='left', on='area_id', suffixes=["", "_lumped_areas"]).dropna(subset=['area_name']).reset_index()
    storm_directors_lumped_areas = storm_directors_lumped_areas_no_node_names.merge(nodes, how='left', left_on='to_node_id',right_on='node_id', suffixes=['','_nodes'])

    storm_directors_lumped_areas = storm_directors_lumped_areas[['area_name', 'director_code', 'node_name', 'area_sqft', 'area_sqft_lumped_areas']]

    unique_area_name_node_name_combinations = storm_directors_lumped_areas.groupby(['area_name', 'node_name']).first().reset_index()[['area_name', 'node_name', 'area_sqft_lumped_areas']]
    unique_area_name_node_name_combinations = unique_area_name_node_name_combinations.rename(columns={'area_sqft_lumped_areas': 'area_sqft'})

    storm_directors_lumped_areas_agwo = storm_directors_lumped_areas.director_code.isin(['HAG', 'HAL'])
    storm_directors_lumped_areas_ifwo = storm_directors_lumped_areas.director_code.isin(['HIF', 'HSI', 'HAL'])
    storm_directors_lumped_areas_suro = storm_directors_lumped_areas.director_code.isin(['HSU', 'HSI', 'HAL'])
    storm_directors_lumped_areas_agwo_df = pd.DataFrame(storm_directors_lumped_areas[storm_directors_lumped_areas_agwo].groupby(['area_name', 'node_name'])['area_sqft'].sum())
    storm_directors_lumped_areas_ifwo_df = pd.DataFrame(storm_directors_lumped_areas[storm_directors_lumped_areas_ifwo].groupby(['area_name', 'node_name'])['area_sqft'].sum())
    storm_directors_lumped_areas_suro_df = pd.DataFrame(storm_directors_lumped_areas[storm_directors_lumped_areas_suro].groupby(['area_name', 'node_name'])['area_sqft'].sum())
    storm_directors_lumped_areas_agwo_df.reset_index(inplace=True)
    storm_directors_lumped_areas_ifwo_df.reset_index(inplace=True)
    storm_directors_lumped_areas_suro_df.reset_index(inplace=True)

    unique_area_name_node_name_combinations_with_suro = unique_area_name_node_name_combinations.merge(storm_directors_lumped_areas_suro_df, how='left', on=['area_name', 'node_name'], suffixes=["", "_suro"])
    unique_area_name_node_name_combinations_with_suro_ifwo = unique_area_name_node_name_combinations_with_suro.merge(storm_directors_lumped_areas_ifwo_df, how='left',  on=['area_name', 'node_name'],
                                                suffixes=["", "_ifwo"])
    unique_area_name_node_name_combinations_with_suro_ifwo_agwo = unique_area_name_node_name_combinations_with_suro_ifwo.merge(storm_directors_lumped_areas_agwo_df, how='left',  on=['area_name', 'node_name'],
                                                suffixes=["", "_agwo"])

    lumped_areas_with_suro_ifwo_agwo = unique_area_name_node_name_combinations_with_suro_ifwo_agwo[['area_name', 'node_name', 'area_sqft', 'area_sqft_suro' , 'area_sqft_ifwo', 'area_sqft_agwo']].dropna(how='all', subset=['area_sqft_suro' , 'area_sqft_ifwo', 'area_sqft_agwo']).sort_values(by=['area_name', 'area_sqft_suro'])
    final_lumped_areas = lumped_areas_with_suro_ifwo_agwo.fillna(0)
    final_lumped_areas = final_lumped_areas.rename(columns={'area_name': 'AreaName', 'node_name': 'NodeName', 'area_sqft': 'TotalArea', 'area_sqft_suro': 'SuroArea', 'area_sqft_ifwo': 'IfwoArea', 'area_sqft_agwo': 'AgwoArea'})
    final_lumped_areas.to_csv(lumped_areas_file, index=False)
    pass

if not explicit_areas.empty:
    storm_directors_explicit_areas = storm_directors.merge(explicit_areas, how='left', on='area_id', suffixes=["", "_explicit_area"]).dropna(subset=['area_name']).reset_index()
    storm_directors_explicit_areas_agwo = storm_directors_explicit_areas.director_code.isin(['HAG', 'HAL'])
    storm_directors_explicit_areas_ifwo = storm_directors_explicit_areas.director_code.isin(['HIF', 'HSI', 'HAL'])
    storm_directors_explicit_areas_suro = storm_directors_explicit_areas.director_code.isin(['HSU', 'HSI', 'HAL'])
    storm_directors_explicit_areas_emgaats = storm_directors_explicit_areas.director_code.isin(['DSI', 'CON', 'DSV', 'DRY', 'ECO', 'RNG'])
    storm_directors_explicit_areas_to_links = ~storm_directors_explicit_areas['to_link_id'].isna()
    storm_directors_explicit_areas_to_nodes = ~storm_directors_explicit_areas['to_node_id'].isna()

    storm_directors_explicit_areas['agwo_area'] = storm_directors_explicit_areas[storm_directors_explicit_areas_agwo]['area_sqft']
    storm_directors_explicit_areas['ifwo_area'] = storm_directors_explicit_areas[storm_directors_explicit_areas_ifwo]['area_sqft']
    storm_directors_explicit_areas['suro_area'] = storm_directors_explicit_areas[storm_directors_explicit_areas_suro]['area_sqft']

    storm_directors_explicit_areas = storm_directors_explicit_areas.merge(nodes, how='left',
                                                                                      left_on=['to_node_id'],
                                                                                      right_on=['node_id'])

    if not links.empty and not storm_directors_explicit_areas[storm_directors_explicit_areas_to_links].empty:
        storm_directors_explicit_areas = storm_directors_explicit_areas.merge(links, how='left', left_on=['to_link_id'], right_on=['link_id'])
        storm_directors_explicit_areas = storm_directors_explicit_areas.merge(nodes, how='left', left_on=['us_node_id'],
                                                             right_on=['node_id'], suffixes=["", "_links"])
        storm_directors_explicit_areas["node_name"].fillna(storm_directors_explicit_areas["node_name_links"], inplace=True)

    storm_directors_explicit_areas['emgaats_outlet'] = storm_directors_explicit_areas[storm_directors_explicit_areas_emgaats]['node_name']
    storm_directors_explicit_areas['agwo_outlet'] = storm_directors_explicit_areas[storm_directors_explicit_areas_agwo]['node_name']
    storm_directors_explicit_areas['ifwo_outlet'] = storm_directors_explicit_areas[storm_directors_explicit_areas_ifwo]['node_name']
    storm_directors_explicit_areas['suro_outlet'] = storm_directors_explicit_areas[storm_directors_explicit_areas_suro]['node_name']

    explicit_stormwater_directors_data = storm_directors_explicit_areas.itertuples()
    explicit_stormwater_directors = []
    for explicit_stormwater_director_data in explicit_stormwater_directors_data:
        explicit_stormwater_director = {
                                       "suro_outlet": None,
                                       "ifwo_outlet": None,
                                       "agwo_outlet": None,
                                       "area_name": None,
                                       "area": None,
                                       "area_factor": None,
                                       # "suro_area_sqft": None,
                                       # "ifwo_area_sqft": None,
                                       # "agwo_area_sqft": None,
                                       "con_area_sqft": 0,
                                       "dsi_area_sqft": 0,
                                       "dsv_area_sqft": 0,
                                       "dry_area_sqft": 0,
                                       "eco_area_sqft": 0,
                                       "rng_area_sqft": 0,
                                       }
        if explicit_stormwater_director_data.director_code not in (['HAG', 'HAL', 'HIF', 'HSI', 'HSU', 'SEP']):
            if explicit_stormwater_director_data.director_code in ("CON", "DSI"):
                explicit_stormwater_director["suro_outlet"] = explicit_stormwater_director_data.emgaats_outlet
                explicit_stormwater_director["ifwo_outlet"] = explicit_stormwater_director_data.emgaats_outlet
            else:
                explicit_stormwater_director["suro_outlet"] = explicit_stormwater_director_data.suro_outlet
                explicit_stormwater_director["ifwo_outlet"] = explicit_stormwater_director_data.ifwo_outlet
            explicit_stormwater_director["agwo_outlet"] = explicit_stormwater_director_data.agwo_outlet

            explicit_stormwater_director["area_name"] = explicit_stormwater_director_data.area_name
            explicit_stormwater_director["area"] = explicit_stormwater_director_data.area_sqft_explicit_area
            explicit_stormwater_director["area_factor"] = explicit_stormwater_director_data.area_factor
            # if explicit_stormwater_director_data.director_code in ("CON", "DSI", "DSI", "DSV", "DRY", "ECO"):
            #     explicit_stormwater_director["suro_area_sqft"] = explicit_stormwater_director_data.area_sqft
            #     explicit_stormwater_director["ifwo_area_sqft"] = explicit_stormwater_director_data.area_sqft
            #     explicit_stormwater_director["agwo_area_sqft"] = explicit_stormwater_director_data.area_sqft
            # else:
            #     explicit_stormwater_director["suro_area_sqft"] = explicit_stormwater_director_data.suro_area
            #     explicit_stormwater_director["ifwo_area_sqft"] = explicit_stormwater_director_data.ifwo_area
            #     explicit_stormwater_director["agwo_area_sqft"] = explicit_stormwater_director_data.agwo_area
            if explicit_stormwater_director_data.director_code == "CON":
                explicit_stormwater_director["con_area_sqft"] = explicit_stormwater_director_data.area_sqft
            elif explicit_stormwater_director_data.director_code == "DSI":
                explicit_stormwater_director["dsi_area_sqft"] = explicit_stormwater_director_data.area_sqft
            elif explicit_stormwater_director_data.director_code == "DSV":
                explicit_stormwater_director["dsv_area_sqft"] = explicit_stormwater_director_data.area_sqft
            elif explicit_stormwater_director_data.director_code == "DRY":
                explicit_stormwater_director["dry_area_sqft"] = explicit_stormwater_director_data.area_sqft
            elif explicit_stormwater_director_data.director_code == "ECO":
                explicit_stormwater_director["eco_area_sqft"] = explicit_stormwater_director_data.area_sqft
            elif explicit_stormwater_director_data.director_code == "RNG":
                explicit_stormwater_director["rng_area_sqft"] = explicit_stormwater_director_data.area_sqft
            else:
                if explicit_stormwater_director_data.director_type is not None:
                    print("Director Code not supported: " + explicit_stormwater_director_data.director_code)
                else:
                    print("Director Code of null not supported.")
            explicit_stormwater_directors.append(explicit_stormwater_director)
    explicit_stormwater_directors_df = pd.DataFrame(explicit_stormwater_directors)
    explicit_stormwater_directors_df.to_csv(explicit_areas_file)