import argparse

import geopandas as gpd
import os
import logging
from datetime import datetime
import numpy as np

from shapely.geometry import Point

from geotrieindex import GeoTrieIndex

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

    gti = GeoTrieIndex(gh_len, scan_algorithm=GeoTrieIndex.SUBSAMPLE_GRID)
    print('building td...')
    begin = datetime.now()
    gti.build(input_data)
    t = datetime.now() - begin
    print('building took {}s'.format(t.total_seconds()))

    max_bounds = geojson.bounds.max()
    min_bounds = geojson.bounds.min()

    max_lon = max_bounds["maxx"]
    max_lat = max_bounds["maxy"]
    min_lon = min_bounds["minx"]
    min_lat = min_bounds["miny"]
    test_size = int(1e6)
    rx = (max_lon - min_lon) * np.random.random(test_size) + min_lon
    ry = (max_lat - min_lat) * np.random.random(test_size) + min_lat
    test_points = zip(rx, ry)

    print('searching...')
    found = 0
    begin = datetime.now()

    for i in np.arange(test_size):
        for pt in test_points:
            pt_geom = Point(*pt)
            if len(gti.lookup(pt_geom)) > 0:
                found += 1
    t = datetime.now() - begin
    print('searching took {}s for {}/{} points'.format(t.total_seconds(), found, test_size))
    print('Found: {}/1M'.format(found))

    # gti.show(False)


if __name__ == '__main__':
    main()
