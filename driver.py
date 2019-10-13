import argparse
from collections import deque

from geotrie import GeoTrie
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon
import os
import logging
from pprint import pprint
import geohash_hilbert as ghh
from datetime import datetime
from geotrie_index import GeoTrieIndex, FifoQueue


def main():
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
    sample = geojson[:100]

    # gt = GeoTrie(3)
    # gt.insert("abc", 1)
    # gt.insert("abc", 2)
    # gt.insert("abc", 3)
    # gt.insert("abdc", 3)
    # gt.insert("xyz", 8)
    # gt.walk()

    gti = GeoTrieIndex(gh_len)
    begin = datetime.now()
    print(begin)
    gti.build(geojson)
    t = datetime.now() - begin
    print('took {}ms'.format(t))
    # gti.show(False)


if __name__ == '__main__':
    main()
