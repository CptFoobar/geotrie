from geopandas import GeoDataFrame
from shapely.geometry import Point, Polygon
from typing import List

from geodatapoint import GeoDataPoint
from spatialindex import SpatialIndex
from strtree import STRTree


class STRTreeIndex(SpatialIndex):
    def __init__(self, node_capacity: int = 10):
        self.node_capacity = node_capacity
        self.strtree = STRTree(node_capacity)

    def build(self, geo_df: GeoDataFrame):
        gdp_list = []
        df_columns = list(geo_df.columns)
        for i, row in geo_df.iterrows():
            polygons: List[Polygon] = []
            if isinstance(row["geometry"], Polygon):
                polygons = [row["geometry"]]
            else:
                polygons = row["geometry"].geoms
            # TODO: Check for non-polygon entries
            for poly in polygons:
                meta = {column: row[column] for column in list(filter(lambda x: x != "geometry", df_columns))}
                gdp_list.append(GeoDataPoint(meta, poly))
        self.strtree.build(gdp_list)

    def lookup(self, p: Point):
        return self.strtree.search(p)

    def show(self):
        raise NotImplementedError("show is not implemented for STRTreeIndex")
