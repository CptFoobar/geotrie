import argparse

import geopandas as gpd
import os
import logging
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
                        help="length of geohash, between 1 and 12 (inclusive)")
    parser.add_argument("-i", "--input", help="path to input geojson", required=False)
    parser.add_argument("-s", "--sample", help="sample size", type=int, required=False)
    args = parser.parse_args()
    gh_len = args.len_geohash
    input_path = args.input
    sample_size = args.sample

    if gh_len <= 0 or gh_len > 10:
        logging.error("Unsupported geohash length: {}. Must be between 1 and 12.".format(gh_len))

    if not os.path.exists(input_path):
        logging.error("Invalid input file: No such file or directory: {}".format(input_path))
        return

    geojson = gpd.read_file(input_path)
    if sample_size is not None and sample_size > 0:
        input_data = geojson[:sample_size]
    else:
        input_data = geojson

    test_size = int(1e5)
    b = BenchmarkSI("gti", "desc", test_size=test_size)
    b.set_index(GeoTrieIndex)
    b.set_dataset(input_data)
    build_bm = b.benchmark_build(gh_len=gh_len, scan_algorithm=GeoTrieIndex.SUBSAMPLE_GRID)
    print('build: {}ms ± {}ms'.format(build_bm[0]*1e3, build_bm[1]*1e3))
    lookup_bm = b.benchmark_lookup(gh_len=gh_len, scan_algorithm=GeoTrieIndex.SUBSAMPLE_GRID)
    print('lookup: {}ms ± {}ms'.format(lookup_bm[0]*1e3, build_bm[1]*1e3))

    s = BenchmarkSI("sti", "desc", test_size=test_size)
    s.set_index(STRTreeIndex)
    s.set_dataset(input_data)

    build_bm = s.benchmark_build()
    print('build: {}ms ± {}ms'.format(build_bm[0]*1e3, build_bm[1]*1e3))
    lookup_bm = s.benchmark_lookup()
    print('lookup: {}ms ± {}ms'.format(lookup_bm[0]*1e3, build_bm[1]*1e3))


if __name__ == '__main__':
    main()
