from geopandas import GeoDataFrame
from shapely.geometry import Point


class SpatialIndex:
    """Base class for spatial index"""

    def build(self, gdf: GeoDataFrame):
        raise NotImplementedError("build index is not implemented")

    def lookup(self, p: Point):
        raise NotImplementedError("lookup index is not implemented")

    def show(self):
        raise NotImplementedError("show index is not implemented")
