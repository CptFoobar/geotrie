from geopandas import GeoDataFrame
from shapely.geometry import Point, Polygon


class SpatialIndex(object):
    """Base class for spatial index"""

    def build(self, gdf: GeoDataFrame):
        raise NotImplementedError("build index is not implemented")

    def lookup(self, p: Point):
        raise NotImplementedError("lookup is not implemented")

    def show(self):
        raise NotImplementedError("show is not implemented")

    def overlaps(self, p: Polygon):
        raise NotImplementedError("overlaps is not implemented")
