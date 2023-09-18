class Point:
    """
    A standard two-dimensional point within the DOM, consisting of both an X and Y coordinate. This location is
    understood to be pixels measured from the top-left corner of the Viewport of the browser.
    """

    def __init__(self, x: float, y: float):
        self.X = x
        self.Y = y
        self._current_index = 0
        self._items = [x, y]

    def __getitem__(self, index):
        try:
            return self._items[index]
        except IndexError:
            raise IndexError("Points only have two coordinates; supply an index in this range: -2<=N<=1.")

    def __iter__(self):
        return self

    def __next__(self):
        if self._current_index < 2:
            coordinate_value = self._items[self._current_index]
            self._current_index += 1
            return coordinate_value
        raise StopIteration
