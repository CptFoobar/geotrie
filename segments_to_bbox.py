import argparse

import geopandas as gpd
import logging
import os
import time


def current_milli_time():
    return int(round(time.time() * 1000))


def main():
    # TODO: Use logging
    parser = argparse.ArgumentParser(description="Line segments to bounding box")
    parser.add_argument("-i", "--input", help="line segments (geoJSON)", type=str, required=True)
    args = parser.parse_args()
    input_path = args.input

    if not os.path.exists(input_path):
        logging.error("Invalid input file: No such file or directory: {}".format(input_path))
        return

    geojson = gpd.read_file(input_path)
    input_data = geojson
    print(input_data.count())
    file_name = os.path.basename(input_path)
    ext_index = file_name.rfind(".")
    updated_file_name = file_name[:ext_index] + "_bbox" + file_name[ext_index:]
    input_data.envelope.to_file(os.path.join(os.path.dirname(input_path), updated_file_name), driver="GeoJSON")


if __name__ == '__main__':
    main()
