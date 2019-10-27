from shapely.geometry import Point


class BaseGeometryPoint(object):
    @property
    def bbox(self):
        raise NotImplementedError("bounding box of base geometry is not implemented")

    @property
    def centroid(self):
        raise NotImplementedError("centroid of base geometry is not implemented")

    def contains(self, point: Point):
        raise NotImplementedError("contains of base geometry is not implemented")