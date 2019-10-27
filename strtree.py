from abc import ABC
from typing import List, Union

from shapely.geometry import Point, Polygon

from geodatapoint import GeoDataPoint
from basegeometrypoint import BaseGeometryPoint

from math import ceil, sqrt


class RTreeNode(BaseGeometryPoint):
    def __init__(self, entries: List[BaseGeometryPoint], mbr: (float, float, float, float)):
        self.entries = entries
        self.mbr = mbr
        poly_coords = [(mbr[0], mbr[1]), (mbr[0], mbr[3]), (mbr[2], mbr[3]), (mbr[2], mbr[1])]
        self._mbr_poly = Polygon(poly_coords)

    def search(self, point: Point) -> List[GeoDataPoint]:
        if self.is_empty:
            return []

        if not self._mbr_poly.contains(point):
            return []

        containers = []
        for e in self.entries:
            if e.contains(point):
                if isinstance(e, RTreeNode):
                    containers.extend(e.search(point))
                else:
                    containers.append(e)

        return containers

    def contains(self, point: Point):
        return self._mbr_poly.contains(point)

    @classmethod
    def empty_node(cls):
        return RTreeNode([], (0.0, 0.0, 0.0, 0.0))

    @property
    def is_empty(self):
        return len(self.entries) == 0

    @property
    def bbox(self):
        return self.mbr

    @property
    def centroid(self):
        raise NotImplementedError("centroid of RTreeNode is not implemented")


class STRTree:
    def __init__(self, node_capacity: int = 10):
        self._node_capacity = node_capacity
        self._root: RTreeNode = None
        self._total_polygons = 0

    @staticmethod
    def __pack_node(cls, level: List[BaseGeometryPoint]):
        level_len = len(level)
        if level_len == 1:
            return RTreeNode(level, level[0].bbox)
        min_lon, min_lat, max_lon, max_lat = level[0].bbox
        for entry in level:
            e_min_lon, e_min_lat, e_max_lon, e_max_lat = entry.bbox
            min_lon = min(min_lon, e_min_lon)
            min_lat = min(min_lat, e_min_lat)
            max_lon = max(max_lon, e_max_lon)
            max_lat = max(max_lat, e_max_lat)
        return RTreeNode(level, (min_lon, min_lat, max_lon, max_lat))

    def __pack_level(self, level: List[BaseGeometryPoint]) -> RTreeNode:
        level_len = len(level)

        if level_len == 0:
            return RTreeNode.empty_node()

        if len(level) < self._node_capacity:
            return self.__pack_node(self, level)

        level.sort(key=lambda pt: pt.bbox[0] + pt.bbox[2])

        node_count = ceil(level_len / self._node_capacity)
        slice_count = ceil(sqrt(node_count))
        slice_capacity = slice_count * self._node_capacity
        next_level = []
        i = 0
        while True:
            if i >= level_len:
                break
            slice_end = min(level_len, i + slice_capacity)
            level[i:slice_end].sort(key=lambda pt: pt.bbox[1] + pt.bbox[3])
            while i < slice_end:
                pack_end = min(level_len, i + self._node_capacity)
                next_level.append(self.__pack_node(self, level[i:pack_end]))
                i = pack_end

        return self.__pack_level(next_level)

    def build(self, polygons: List[GeoDataPoint]):
        self._total_polygons = len(polygons)
        self._root = self.__pack_level(polygons)

    def search(self, point: Point) -> List[GeoDataPoint]:
        return self._root.search(point)


