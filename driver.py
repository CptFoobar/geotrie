import argparse

import geopandas as gpd
import os
import logging
from datetime import datetime

from shapely.geometry import Point

from geotrieindex import GeoTrieIndex


def main():
    # TODO: Use logging
    parser = argparse.ArgumentParser(prog="GeoTrie Driver", description="Driver program for GeoTrie algorithm")
    parser.add_argument("-l", "--len-geohash", type=int, default=4,
                        help="length of geohash, between 1 and 12 (inclusive)")
    parser.add_argument("-i", "--input", help="path to input geojson", required=False)
    args = parser.parse_args()
    gh_len = args.len_geohash
    input_path = args.input

    if gh_len <= 0 or gh_len > 12:
        logging.error("Unsupported geohash length: {}. Must be between 1 and 12.".format(gh_len))

    if not os.path.exists(input_path):
        logging.error("Invalid input file: No such file or directory: {}".format(input_path))
        return

    geojson = gpd.read_file(input_path)
    sample = geojson[:30]

    gti = GeoTrieIndex(gh_len)
    begin = datetime.now()
    gti.build(sample)
    t = datetime.now() - begin
    print('building took {}s'.format(t.total_seconds()))
    testpoint1 = Point((-73.9176514626831, 40.560473006628456))
    testpoint2 = Point((-73.81339916011954, 40.70293833261958))

    print([str(p) for p in gti.lookup(testpoint1)])
    print([str(p) for p in gti.lookup(testpoint2)])

    # gti.show(False)


if __name__ == '__main__':
    main()
