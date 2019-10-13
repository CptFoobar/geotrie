from geopandas import GeoDataFrame
from shapely.geometry import Polygon, Point
from shapely.geometry import shape
from geodatapoint import GeoDataPoint
from geotrie import GeoTrie
import geohash_hilbert as ghh
from typing import List, Iterable
from collections import deque


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
    def __init__(self, gh_len: int):
        self.gh_len = gh_len
        self.gt = GeoTrie(gh_len)

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

    def __gh_intersecting(self, poly: Polygon) -> List[str]:
        centroid = poly.centroid
        gh = ghh.encode(*(centroid.coords[0]), precision=self.gh_len)
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

            nextLevel = list(ghh.neighbours(node).values())
            # print('got {} nbrs'.format(len(nextLevel)))
            # input()
            for nbr in nextLevel:
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

    def lookup(self, point: Point):
        gh = ghh.encode(*(point.coords[0]), precision=self.gh_len)
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
