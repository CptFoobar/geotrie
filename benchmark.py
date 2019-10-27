import time
from typing import Type

from geopandas import GeoDataFrame
from shapely.geometry import Point

from spatialindex import SpatialIndex
import numpy as np
from tqdm import tqdm


class BenchmarkRunner(object):
    def __init__(self, name: str, description: str, iterations: int = int(1e4)):
        assert iterations > 1
        self.name = name
        self.description = description
        self._iterations = int(iterations)

    @property
    def iterations(self):
        return self._iterations

    @iterations.setter
    def iterations(self, i):
        self._iterations = i

    def __timeit(self, fn, *args, **kwargs):
        begin = time.time()
        for i in range(self.iterations):
            fn(*args, **kwargs)
        return time.time() - begin

    def __loop_cost(self):
        begin = time.time()
        for i in range(self.iterations):
            pass
        return time.time() - begin

    def timeit(self, fn, *args, **kwargs):
        lc = self.__loop_cost()
        runtime = self.__timeit(fn, *args, **kwargs)
        return runtime, runtime - lc


class BenchmarkSI(BenchmarkRunner):
    def __init__(self, name: str, description: str, iterations: int = 10, test_size: int = int(1e6)):
        super().__init__(name, description, iterations)
        self._dataset: GeoDataFrame = GeoDataFrame()
        self._si: Type[SpatialIndex] = Type[SpatialIndex]
        self._test_size = test_size
        self._rx = None
        self._ry = None

    def set_index(self, si: Type[SpatialIndex]):
        self._si = si

    def set_dataset(self, gpd: GeoDataFrame):
        self._dataset = gpd

    def __prepare_test_points(self):
        if self._dataset is None:
            raise ValueError("dataset is not set")
        max_bounds = self._dataset.bounds.max()
        min_bounds = self._dataset.bounds.min()

        max_lon = max_bounds["maxx"]
        max_lat = max_bounds["maxy"]
        min_lon = min_bounds["minx"]
        min_lat = min_bounds["miny"]
        self._rx = (max_lon - min_lon) * np.random.random(self._test_size) + min_lon
        self._ry = (max_lat - min_lat) * np.random.random(self._test_size) + min_lat

    def benchmark_build(self, *args, **kwargs):
        print('{}: running build {} times...'.format(self.name, self.iterations))
        times = np.array([])
        for i in tqdm(range(self.iterations)):
            total_runtime, _ = self.timeit(self._si(*args, **kwargs).build, self._dataset)
            times = np.append(times, total_runtime)
        return times.mean(), times.std()

    def benchmark_lookup(self, *args, **kwargs):
        print('{}: running {} lookups {} times...'.format(self.name, self._test_size, self.iterations))
        times = np.array([])
        idx = self._si(*args, **kwargs)
        idx.build(self._dataset)
        for i in tqdm(range(self.iterations)):
            self.__prepare_test_points()
            begin = time.time()
            for pt in tqdm(zip(self._rx, self._ry)):
                idx.lookup(Point(*pt))
            end = time.time()
            times = np.append(times, end - begin)
        return times.mean(), times.std()
