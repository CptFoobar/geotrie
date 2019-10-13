from shapely.geometry import Polygon
import json


class GeoDataPoint:
    def __init__(self, meta: dict = None, poly: Polygon = None):
        if meta is None:
            meta = dict()
        self.meta = meta
        self.poly = poly

    def set_meta(self, meta: dict):
        self.meta = meta

    def set_polygon(self, poly: Polygon):
        self.poly = poly

    def set(self, meta, poly):
        self.set_meta(meta)
        self.set_polygon(poly)

    def __str__(self):
        # return str({"meta": self.meta, "poly": self.poly.exterior.coords.xy})
        return str({"meta": self.meta, "n_vertices": len(self.poly.exterior.coords)})
