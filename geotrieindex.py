from datetime import datetime
from geopandas import GeoDataFrame
from shapely.geometry import Polygon, Point
from shapely.geometry import shape

from spatialindex import SpatialIndex
from geodatapoint import GeoDataPoint
from geotrie import GeoTrie
from typing import List, Iterable, Union
from collections import deque
import geohash_hilbert as ghh
import numpy as np


class FifoQueue(object):
    def __init__(self):
        self.__q = deque()

    def push(self, item):
        return self.__q.append(item)

    def pop(self):
        return self.__q.popleft()

    def clear(self):
        return self.__q.clear()

    def size(self):
        return len(self.__q)

    def empty(self):
        return self.size() == 0

    def __str__(self):
        return str(list(self.__q))


class GeoTrieIndex(SpatialIndex):
    """A geospatial index that using GeoTries as underlying data structure"""

    '''
    Two overlap discovery algorithms are provided:
    SUBSAMPLE_GRID: Divides bounding box of given polygon into a grid and maps select points in the grid as geohashes
    NEIGHBOUR_BFS: Performs BFS search on centroid of given polygon till it keeps finding neighbours that intersect
    TOP_DOWN: Performs a top-down search of overlapping grids, starting from largest geohash(es) that contain polygon 
    '''
    SUBSAMPLE_GRID = 1
    NEIGHBOUR_BFS = 2
    TOP_DOWN = 3

    _BASE64 = (
        '0123456789'  # noqa: E262    #   10    0x30 - 0x39
        '@'  # +  1    0x40
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'  # + 26    0x41 - 0x5A
        '_'  # +  1    0x5F
        'abcdefghijklmnopqrstuvwxyz'  # + 26    0x61 - 0x7A
    )  # = 64    0x30 - 0x7A

    def __init__(self, gh_len: int, scan_algorithm=SUBSAMPLE_GRID):
        self.gh_len = gh_len
        self.gt = None
        self.scan_algorithm = scan_algorithm

    def __gh_encode(self, lon, lat):
        return ghh.encode(lon, lat, precision=self.gh_len)

    @classmethod
    def __gh_intersects_poly(cls, gh: str, poly: Polygon):
        node_poly = shape(ghh.rectangle(gh)["geometry"])
        return node_poly.intersects(poly)

    @classmethod
    def __gh_contains_poly(cls, gh: str, poly: Polygon):
        node_poly = shape(ghh.rectangle(gh)["geometry"])
        return node_poly.contains(poly)

    @classmethod
    def __get_children(cls, parent: str) -> List[str]:
        return [parent + child for child in cls._BASE64]

    def __neighbour_bfs(self, poly: Polygon, precision) -> List[str]:
        centroid = poly.centroid
        gh = ghh.encode(*(centroid.coords[0]), precision=precision)
        overlaps = []
        q1 = FifoQueue()
        q1.push(gh)
        q2 = FifoQueue()
        visited = dict()
        discovered = dict()
        level_active = False

        while not q1.empty():
            node = q1.pop()
            if node not in visited.keys():
                visited[node] = True
                discovered[node] = True
                node_poly = shape(ghh.rectangle(node)["geometry"])
                if node_poly.intersects(poly):
                    overlaps.append(node)
                    level_active = True

            next_level = list(ghh.neighbours(node).values())
            for nbr in next_level:
                if nbr not in discovered.keys():
                    discovered[nbr] = True
                    q2.push(nbr)
            if q1.empty() and level_active:
                level_active = False
                q2, q1 = q1, q2

        return overlaps

    # TODO: Make this a generator
    def __matrix_geohashes(self, poly) -> List:
        precision_box = ghh.rectangle(''.join(["0" for _ in range(self.gh_len)]))["bbox"]
        grid_intercept = min(abs(precision_box[0] - precision_box[2]), abs(precision_box[1] - precision_box[3]))
        poly_bbox = poly.bounds
        subsamples = set()
        for lon in np.arange(poly_bbox[0], poly_bbox[2] + grid_intercept, grid_intercept):
            for lat in np.arange(poly_bbox[1], poly_bbox[3] + grid_intercept, grid_intercept):
                subsamples.add(self.__gh_encode(lon, lat))
        return list(subsamples)

    def __subsample_grid(self, poly: Polygon) -> List[str]:
        subsamples = self.__matrix_geohashes(poly)
        overlaps = []
        for gh in subsamples:
            if self.__gh_intersects_poly(gh, poly):
                overlaps.append(gh)
        return overlaps

    def __search_gh_box(self, poly: Polygon, prefix: str) -> List[str]:
        # Check if geohash of required length intersects polygon. if so, it is part of the solution
        if len(prefix) == self.gh_len:
            return [prefix] if self.__gh_intersects_poly(prefix, poly) else []

        # If prefix doesn't intersect polygon, none of its children will.
        if not self.__gh_intersects_poly(prefix, poly):
            return []

        intersects = []
        children = self.__get_children(prefix)
        # Recurse on all children
        for child in children:
            intersects.extend(self.__search_gh_box(poly, child))
        return intersects

    def __smallest_container(self, poly: Polygon) -> Union[str, None]:
        centroid_coords = poly.centroid.coords[0]
        gh_centroid = self.__gh_encode(*centroid_coords)
        i = 0
        while not self.__gh_contains_poly(gh_centroid, poly):
            i += 1
            if i == self.gh_len:
                return None
            gh_centroid = ghh.encode(*centroid_coords, precision=self.gh_len - i)
        return gh_centroid

    def __top_down_search(self, poly: Polygon) -> List[str]:
        # find top level geohashes intersecting polygon
        smallest_gh = self.__smallest_container(poly)
        if smallest_gh is None:
            top_level = self.__neighbour_bfs(poly, 1)
        else:
            top_level = [smallest_gh]
        overlaps = []
        for tgh in top_level:
            overlaps.extend(self.__search_gh_box(poly, tgh))
        return overlaps

    # TODO: return {geohash, polygon}
    def __gh_intersecting(self, poly: Polygon) -> List[str]:
        if self.scan_algorithm == self.SUBSAMPLE_GRID:
            return self.__subsample_grid(poly)
        elif self.scan_algorithm == self.NEIGHBOUR_BFS:
            return self.__neighbour_bfs(poly, self.gh_len)
        elif self.scan_algorithm == self.TOP_DOWN:
            return self.__top_down_search(poly)
        else:
            raise Exception("Invalid scan algorithm")

    def build(self, geo_df: GeoDataFrame):
        self.gt = GeoTrie(self.gh_len)
        df_columns = list(geo_df.columns)
        for i, row in geo_df.iterrows():
            polygons: List[Polygon] = row["geometry"].geoms
            # TODO: Check for non-polygon entries
            for poly in polygons:
                meta = {column: row[column] for column in list(filter(lambda x: x != "geometry", df_columns))}
                gdp = GeoDataPoint(meta, poly)
                geos = self.__gh_intersecting(poly)
                for gh in geos:
                    self.gt.insert(gh, gdp)

    def lookup(self, point: Point):
        if self.gt is None:
            raise ValueError("index is not built")
        gh = self.__gh_encode(*(point.coords[0]))
        candidates = self.gt.search(gh)
        containers = []
        for c in candidates:
            if c.poly.contains(point):
                containers.append(c)
        return containers

    def gh_boxes(self, gh):
        return self.gt.search(gh)

    def show(self, long_format=False):
        if self.gt is None:
            raise ValueError("index is not built")

        def print_formatted(trie_dict: dict):
            for k, v in trie_dict.items():
                if long_format:
                    print(k, "->", ', '.join([str(i) for i in v]))
                else:
                    print(k, "->", len(v))

        print("walking...")
        self.gt.walk(print_formatted)
