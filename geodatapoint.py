from shapely.geometry import Polygon, Point
from shapely.geometry.base import BaseGeometry

from basegeometrypoint import BaseGeometryPoint


class GeoDataPoint(BaseGeometryPoint):
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
        return str({"meta": self.meta, "n_vertices": len(self.poly.exterior.coords)})

    @property
    def bbox(self):
        return self.poly.bounds

    @property
    def centroid(self):
        return self.poly.centroid.coords[0]

    def contains(self, point: Point):
        return self.poly.contains(point)

    def intersects(self, geometry: BaseGeometryPoint):
        return self.poly.intersects(geometry)