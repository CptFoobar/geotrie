import argparse

import geopandas as gpd
import os
import logging
import pandas as pd
from datetime import datetime
import numpy as np
from geopandas.sindex import SpatialIndex

from shapely.geometry import Point, Polygon
from shapely.strtree import STRtree
from tqdm import tqdm

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

    gti = GeoTrieIndex(gh_len)
    gti.build(input_data)

    sti = STRTreeIndex()
    sti.build(input_data)

    # max_bounds = input_data.bounds.max()
    # min_bounds = input_data.bounds.min()
    #
    # max_lon = max_bounds["maxx"]
    # max_lat = max_bounds["maxy"]
    # min_lon = min_bounds["minx"]
    # min_lat = min_bounds["miny"]

    # -73.92261294314002,40.55628162435524,-73.91268998222618,40.56466438890167
    qp = Polygon([[-73.92261294314102, 40.55628162435625], [-73.92261294314102, 40.56466438890200],
                  [-73.91268998222518, 40.56466438890200], [-73.91268998222518, 40.55628162435625]])

    # qp = Polygon([[-73.92261294314102, 40.55628162435625], [-70, 35], [-73.92261294314102, 40.55628162435625]])

    kmap = {}
    print("from gti")

    for k in tqdm(range(1)):
        o = gti.overlaps(qp)
        kmap[len(o)] = 1 if len(o) not in kmap.keys() else kmap[len(o)] + 1
    print(kmap)

    kmap = {}
    print("from sti")

    for k in tqdm(range(1)):
        o = sti.overlaps(qp)
        kmap[len(o)] = 1 if len(o) not in kmap.keys() else kmap[len(o)] + 1
    print(kmap)
    # print(qp.wkt)
    # bm_results = []
    # bm_columns = ['index_type', 'op', 'op_count', 'total_time_ms', 'ops_per_sec', 'remark']
    # iterations = 1
    # test_size = int(1e5)
    #
    # b = BenchmarkSI("gti", "desc", test_size=test_size)
    # b.set_index(GeoTrieIndex)
    # b.set_dataset(input_data)
    # b.iterations = iterations
    # build_bm = b.benchmark_build(gh_len=gh_len, scan_algorithm=GeoTrieIndex.SUBSAMPLE_GRID)
    # print('build: {}ms ± {}ms'.format(build_bm[0] * 1e3, build_bm[1] * 1e3))
    # lookup_bm = b.benchmark_lookup(gh_len=gh_len, scan_algorithm=GeoTrieIndex.SUBSAMPLE_GRID)
    # print('lookup: {}ms ± {}ms'.format(lookup_bm[0] * 1e3, lookup_bm[1] * 1e3))
    #
    # bm_results.append(['geotrie', 'build', 1, build_bm[0] * 1e3, 1 / build_bm[0],
    #                    'gh_len={} scan_algorithm=SUBSAMPLE_GRID iterations={}'.format(gh_len, b.iterations)])
    # bm_results.append(['geotrie', 'lookup', test_size, lookup_bm[0] * 1e3, test_size / lookup_bm[0],
    #                    'gh_len={} scan_algorithm=SUBSAMPLE_GRID iterations={}'.format(gh_len, b.iterations)])
    #
    # s = BenchmarkSI("sti", "desc", test_size=test_size)
    # s.set_index(STRTreeIndex)
    # s.set_dataset(input_data)
    # s.iterations = iterations
    # build_bm = s.benchmark_build()
    # print('build: {}ms ± {}ms'.format(build_bm[0] * 1e3, build_bm[1] * 1e3))
    # lookup_bm = s.benchmark_lookup()
    # print('lookup: {}ms ± {}ms'.format(lookup_bm[0] * 1e3, lookup_bm[1] * 1e3))
    #
    # bm_results.append(['strtree', 'build', 1, build_bm[0] * 1e3, 1 / build_bm[0],
    #                    'node_capacity=10 iterations={}'.format(s.iterations)])
    # bm_results.append(['strtree', 'lookup', test_size, lookup_bm[0] * 1e3, test_size / lookup_bm[0],
    #                    'node_capacity=10 iterations={}'.format(s.iterations)])
    #
    # bm_df = pd.DataFrame(bm_results, columns=bm_columns)
    # bm_df.to_csv("tmp.csv", index=False)


if __name__ == '__main__':
    main()
