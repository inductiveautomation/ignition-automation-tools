import math


class GeographicPoint:
    """
    A standard two-dimensional point representing a geographical location on Earth, consisting of both latitude and
    longitude values represented as floats.
    """

    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude
        self._current_index = 0
        self._items = [latitude, longitude]

    def __getitem__(self, index):
        try:
            return self._items[index]
        except IndexError:
            raise IndexError("GeographicPoint only have two coordinates; supply an index in this range: -2<=N<=1.")

    def __iter__(self):
        return self

    def __next__(self):
        if self._current_index < 2:
            coordinate_value = self._items[self._current_index]
            self._current_index += 1
            return coordinate_value
        raise StopIteration

    def __repr__(self):
        return f'{self.__class__.__name__}(latitude: {self.latitude}, longitude: {self.longitude})'

    def __eq__(self, other):
        return (math.isclose(self.latitude, other.latitude, abs_tol=1e-08, rel_tol=0) and
                math.isclose(self.longitude, other.longitude, abs_tol=1e-08, rel_tol=0))
