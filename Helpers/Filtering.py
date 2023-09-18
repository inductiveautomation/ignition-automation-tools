from typing import List, Iterable


class Items:
    """
    This helper allows for defining some iterable collection of items so that they can then be filtered by some
    function.
    """

    def __init__(self, items: Iterable):
        self._items = items

    def filter(self, filtering_function) -> List:
        """
        Filter this Items object based on whether each item results in a truthy evaluation when run through the
        supplied function.

        Example:
            items (constructor) = "apple"
            filtering_function = lambda e: e in "laptop"
            In this example, every item (character) within the iterable supplied within the constructor (our string
            "apple") will be evaluated to see if it (e) is in the string "laptop". The returned list after evaluation
            will be ["a", "p", "p", "l"].

        :param filtering_function: A function (usually a lambda) which accepts one argument and performs some sort of
            evaluation of that argument. As each item in this Items object is evaluated as the argument of the function,
            a truthy evaluation will result in the item being evaluated remaining in the returned list, while a falsy
            evaluation will result in the item being omitted from the returned list.

        :returns: A list, where each item in the list was evaluated by the supplied function and resulted in a truthy
            evaluation.
        """
        return list(filter(filtering_function, self._items))
