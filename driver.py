import argparse

import geopandas as gpd
import os
import logging
import pandas as pd
from datetime import datetime
import numpy as np
from geopandas.sindex import SpatialIndex

from shapely.geometry import Point
from shapely.strtree import STRtree

from benchmark import BenchmarkSI
from geotrieindex import GeoTrieIndex

import time

from strtreeindex import STRTreeIndex


def current_milli_time():
    return int(round(time.time() * 1000))


def main():
    # TODO: Use logging
    parser = argparse.ArgumentParser(prog="GeoTrie Driver", description="Driver program for GeoTrie algorithm")
    parser.add_argument("-l", "--len-geohash", type=int, default=4,
                        help="length of geohash, between 1 and 10 (inclusive)")
    parser.add_argument("-i", "--input", help="path to input geojson", required=False)
    parser.add_argument("-s", "--sample", help="sample size", type=int, required=False)
    args = parser.parse_args()
    gh_len = args.len_geohash
    input_path = args.input
    sample_size = args.sample

    if gh_len <= 0 or gh_len > 10:
        logging.error("Unsupported geohash length: {}. Must be between 1 and 10.".format(gh_len))

    if not os.path.exists(input_path):
        logging.error("Invalid input file: No such file or directory: {}".format(input_path))
        return

    geojson = gpd.read_file(input_path)
    if sample_size is not None and sample_size > 0:
        input_data = geojson[:sample_size]
    else:
        input_data = geojson

    bm_results = []
    bm_columns = ['index_type', 'op', 'op_count', 'total_time_ms', 'ops_per_sec', 'remark']
    iters = 5
    test_size = int(1e6)

    b = BenchmarkSI("gti", "desc", test_size=test_size)
    b.set_index(GeoTrieIndex)
    b.set_dataset(input_data)
    b.iterations = iters
    build_bm = b.benchmark_build(gh_len=gh_len, scan_algorithm=GeoTrieIndex.SUBSAMPLE_GRID)
    print('build: {}ms ± {}ms'.format(build_bm[0] * 1e3, build_bm[1] * 1e3))
    lookup_bm = b.benchmark_lookup(gh_len=gh_len, scan_algorithm=GeoTrieIndex.SUBSAMPLE_GRID)
    print('lookup: {}ms ± {}ms'.format(lookup_bm[0] * 1e3, lookup_bm[1] * 1e3))

    bm_results.append(['geotrie', 'build', 1, build_bm[0] * 1e3, 1 / build_bm[0],
                       'gh_len={} scan_algorithm=SUBSAMPLE_GRID iterations={}'.format(gh_len, b.iterations)])
    bm_results.append(['geotrie', 'lookup', test_size, lookup_bm[0] * 1e3, test_size / lookup_bm[0],
                       'gh_len={} scan_algorithm=SUBSAMPLE_GRID iterations={}'.format(gh_len, b.iterations)])

    # b = BenchmarkSI("gti", "desc", test_size=test_size)
    # b.set_index(GeoTrieIndex)
    # b.set_dataset(input_data)
    # b.iterations = iters
    # build_bm = b.benchmark_build(gh_len=gh_len, scan_algorithm=GeoTrieIndex.NEIGHBOUR_BFS)
    # print('build: {}ms ± {}ms'.format(build_bm[0] * 1e3, build_bm[1] * 1e3))
    # lookup_bm = b.benchmark_lookup(gh_len=gh_len, scan_algorithm=GeoTrieIndex.NEIGHBOUR_BFS)
    # print('lookup: {}ms ± {}ms'.format(lookup_bm[0] * 1e3, lookup_bm[1] * 1e3))
    #
    # bm_results.append(['geotrie', 'build', 1, build_bm[0] * 1e3, 1 / build_bm[0],
    #                    'gh_len={} scan_algorithm=NEIGHBOUR_BFS iterations={}'.format(gh_len, b.iterations)])
    # bm_results.append(['geotrie', 'lookup', test_size, lookup_bm[0] * 1e3, test_size / lookup_bm[0],
    #                    'gh_len={} scan_algorithm=NEIGHBOUR_BFS iterations={}'.format(gh_len, b.iterations)])

    s = BenchmarkSI("sti", "desc", test_size=test_size)
    s.set_index(STRTreeIndex)
    s.set_dataset(input_data)
    s.iterations = iters
    build_bm = s.benchmark_build()
    print('build: {}ms ± {}ms'.format(build_bm[0] * 1e3, build_bm[1] * 1e3))
    lookup_bm = s.benchmark_lookup(node_capacity=5)
    print('lookup: {}ms ± {}ms'.format(lookup_bm[0] * 1e3, lookup_bm[1] * 1e3))

    bm_results.append(['strtree', 'build', 1, build_bm[0] * 1e3, 1 / build_bm[0],
                       'node_capacity=5 iterations={}'.format(s.iterations)])
    bm_results.append(['strtree', 'lookup', test_size, lookup_bm[0] * 1e3, test_size / lookup_bm[0],
                       'node_capacity=5 iterations={}'.format(s.iterations)])

    bm_df = pd.DataFrame(bm_results, columns=bm_columns)
    bm_df.to_csv("bm_all_10iter_nydata.csv", index=False)


if __name__ == '__main__':
    main()
