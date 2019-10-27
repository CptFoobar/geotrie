import time


class BenchmarkRunner:
    def __init__(self, name: str, description: str, iterations: int = int(1e4)):
        assert iterations > 1
        self.name = name
        self.description = description
        self._iterations = iterations
        self._dataset = None

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
        return begin - time.time()

    def timeit(self, fn, *args, **kwargs):
        lc = self.__loop_cost()
        runtime = self.__timeit(fn, *args, **kwargs)
        print(runtime, lc, runtime - lc)

