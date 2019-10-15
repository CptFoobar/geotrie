from geopandas import GeoDataFrame
from shapely.geometry import Polygon, Point
from shapely.geometry import shape
from geodatapoint import GeoDataPoint
from geotrie import GeoTrie
from typing import List, Iterable
from collections import deque
import geohash_hilbert as ghh
import numpy as np


class FifoQueue:
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


class GeoTrieIndex:
    """A geospatial index that using GeoTries as underlying data structure"""

    '''
    Two overlap discovery algorithms are provided:
    SUBSAMPLE_GRID: Divides bounding box of given polygon into a grid and maps select points in the grid as geohashes
    NEIGHBOUR_BFS: Performs BFS search on centroid of given polygon till it keeps finding neighbours that intersect
    '''
    SUBSAMPLE_GRID = 1
    NEIGHBOUR_BFS = 2

    def __init__(self, gh_len: int, scan_algorithm=SUBSAMPLE_GRID):
        self.gh_len = gh_len
        self.gt = GeoTrie(gh_len)
        self.scan_algorithm = scan_algorithm

    def __gh_encode(self, lon, lat):
        return ghh.encode(lon, lat, precision=self.gh_len)

    def __neighbour_bfs(self, poly: Polygon) -> List[str]:
        centroid = poly.centroid
        gh = self.__gh_encode(*(centroid.coords[0]))
        overlaps = []
        q1 = FifoQueue()
        q1.push(gh)
        q2 = FifoQueue()
        visited = dict()
        discovered = dict()
        level_active = False

        while not q1.empty():
            node = q1.pop()
            # print('popped', node)
            if node not in visited.keys():
                # print('visiting', node)
                visited[node] = True
                discovered[node] = True
                node_poly = shape(ghh.rectangle(node)["geometry"])
                if node_poly.intersects(poly):
                    # print('node {} intersects poly'.format(node))
                    overlaps.append(node)
                    level_active = True

            next_level = list(ghh.neighbours(node).values())
            # print('got {} nbrs'.format(len(next_level)))
            # input()
            for nbr in next_level:
                # REVIEW: Redundant visited checks?
                if nbr not in discovered.keys():
                    # print('pushed nbr', nbr, 'not in', discovered.keys())
                    discovered[nbr] = True
                    q2.push(nbr)
            # print('q2', q2.size())
            if q1.empty() and level_active:
                # print("swapping")
                level_active = False
                q2, q1 = q1, q2

        return overlaps

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
            node_poly = shape(ghh.rectangle(gh)["geometry"])
            if node_poly.intersects(poly):
                overlaps.append(gh)
        return overlaps

    # TODO: return {geohash, polygon}
    def __gh_intersecting(self, poly: Polygon) -> List[str]:
        if self.scan_algorithm == self.SUBSAMPLE_GRID:
            return self.__subsample_grid(poly)
        else:
            return self.__neighbour_bfs(poly)

    def build(self, geo_df: GeoDataFrame):
        self.gt.clear()
        df_columns = list(geo_df.columns)
        for i, row in geo_df.iterrows():
            polygons: list[Polygon] = row["geometry"].geoms
            # print('processing row', i)
            # TODO: Check for non-polygon entries
            for poly in polygons:
                meta = {column: row[column] for column in list(filter(lambda x: x != "geometry", df_columns))}
                # print('meta', meta)
                # print('poly', poly)
                gdp = GeoDataPoint(meta, poly)
                geos = self.__gh_intersecting(poly)
                # print(geos)
                for gh in geos:
                    # print(gh)
                    self.gt.insert(gh, gdp)

    def lookup(self, point: Point):
        gh = self.__gh_encode(*(point.coords[0]))
        candidates = self.gt.search(gh)
        for c in candidates:
            if c.poly.contains(point):
                return [c]
        return []

    def gh_boxes(self, gh):
        return self.gt.search(gh)

    def show(self, long_format=False):
        def print_formatted(trie_dict: dict):
            for k, v in trie_dict.items():
                if long_format:
                    print(k, "->", ', '.join([str(i) for i in v]))
                else:
                    print(k, "->", len(v))
        print("walking...")
        self.gt.walk(print_formatted)
