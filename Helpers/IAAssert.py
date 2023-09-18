from typing import Union, Optional, Iterable

from selenium.webdriver.support.color import Color

from Helpers.Ignition.Tag import UdtInstance, Tag, UdtDef, Folder


class IAAssert:

    @staticmethod
    def contains(iterable: Iterable, expected_value, failure_msg: Optional[str] = None) -> None:
        """
        Assert that some iterable contains a specific value.

        :param iterable: Some Iterable object, like a list, dict, tuple, or set.
        :param expected_value: A value which should be an element of the iterable.
        :param failure_msg: Any custom failure message you'd like to supply to explain the impact or cause of a
            potential assertion failure.

        :raises AssertionError: If the supplied expected_value is not an element of the supplied iterable.
        """
        msg = IAAssert._generate_failure_msg(msg=f'Assert {expected_value} in {iterable}',
                                             failure_msg=failure_msg)
        assert expected_value in iterable, msg

    @staticmethod
    def does_not_contain(iterable: Iterable, expected_value, failure_msg: Optional[str] = None) -> None:
        """
        Assert that some iterable does not contain a specific value.

        :param iterable: Some Iterable object, like a list, dict, tuple, or set.
        :param expected_value: A value which should not be an element of the iterable.
        :param failure_msg: Any custom failure message you'd like to supply to explain the impact or cause of a
            potential assertion failure.

        :raises AssertionError: If the supplied expected_value is an element of the supplied iterable.
        """
        msg = IAAssert._generate_failure_msg(msg=f'Assert {expected_value} is not in {iterable}',
                                             failure_msg=failure_msg)
        assert expected_value not in iterable, msg

    @staticmethod
    def is_equal_to(
            actual_value,
            expected_value,
            failure_msg: Optional[str] = None,
            as_type=None) -> None:
        """
        Verify some value is equal to another value. When comparing two values which might be of different types, use
        the as_type argument to specify the type both values should be cast as; this is useful for ignoring instances
        where numeric and string values appear the same but differ in type.

        :param actual_value: The actual value you are comparing/verifying.
        :param expected_value: The value expected to be reflected in the actual value.
        :param failure_msg: Any custom failure message you'd like to supply to explain the impact or cause of a
            potential assertion failure.
        :param as_type: Used to compare the two values as a specific type.

        :raises AssertionError: If the supplied expected_value is an element of the supplied iterable.
        """
        if as_type is not None:
            if as_type == int:
                # must convert to float first!
                actual_value = float(actual_value)
                expected_value = float(expected_value)
            if as_type == Color:
                # Color only accepts a tuple constructor, which throws a wrench into our previous casting.
                assert IAAssert._color_convert(color_as_string=actual_value) ==\
                       IAAssert._color_convert(color_as_string=expected_value),\
                       IAAssert._generate_failure_msg(
                           msg=f'Assert {IAAssert._color_convert(color_as_string=actual_value)} == '
                               f'{IAAssert._color_convert(color_as_string=expected_value)} -> '
                               f'These values were converted to hex before comparison.',
                           failure_msg=failure_msg)
            elif as_type in [Tag, UdtDef, UdtInstance, Folder]:
                # Tags need to be compared as their dictionary counterparts.
                # msg will provide additional insight into any failure.
                assert actual_value.to_dict() == expected_value.to_dict(), \
                    IAAssert._generate_failure_msg(
                        msg=f'Dictionary Values do not match.  The following items are different:\n'
                            f'keys & values in Expected not in Actual: '
                            f'{expected_value.diff_my_unmatched_keys_values(actual_value)}\n'
                            f'keys & values in Actual not in Expected: '
                            f'{expected_value.diff_their_unmatched_keys_values(actual_value)}\n'
                            f'values that do not match: '
                            f'[{actual_value.diff_key_values(expected_tag=expected_value)}]',
                        failure_msg=failure_msg
                )
            else:
                assert as_type(actual_value) == as_type(expected_value), \
                    IAAssert._generate_failure_msg(msg=f'Assert {as_type(actual_value)} == '
                                                       f'{as_type(expected_value)}',
                                                   failure_msg=failure_msg)
        else:
            assert actual_value == expected_value, \
                IAAssert._generate_failure_msg(msg=f'Assert {str(type(actual_value))} {actual_value} == '
                                                   f'{str(type(expected_value))} {expected_value}',
                                               failure_msg=failure_msg)

    @staticmethod
    def is_greater_than(
            left_value,
            right_value,
            failure_msg: Optional[str] = None) -> None:
        """
        Assert that one value is strictly greater than another value. Note that type differences here can cause issues,
        so cast your values before supplying them.

        left_value > right_value

        :param left_value: The value to verify is greater than the right value.
        :param right_value: The value to verify is less than the left value.
        :param failure_msg: Any custom failure message you'd like to supply to explain the impact or cause of a
            potential assertion failure.

        :raises AssertionError: If the left value is not strictly greater than the right value.
        """
        IAAssert._is_greater_than(
            left_value=left_value,
            right_value=right_value,
            failure_msg=failure_msg,
            or_equal_to=False)

    @staticmethod
    def is_greater_than_or_equal_to(
            left_value,
            right_value,
            failure_msg: Optional[str] = None) -> None:
        """
        Assert that one value is greater than or equal to than another value. Note that type differences here can cause
        issues, so cast your values before supplying them.

        left_value >= right_value

        :param left_value: The value to verify is greater than or equal to the right value.
        :param right_value: The value to verify is less than or equal to the left value.
        :param failure_msg: Any custom failure message you'd like to supply to explain the impact or cause of a
            potential assertion failure.

        :raises AssertionError: If the left value is not greater than or equal to the right value.
        """
        IAAssert._is_greater_than(
            left_value=left_value,
            right_value=right_value,
            failure_msg=failure_msg,
            or_equal_to=True)

    @staticmethod
    def is_less_than(
            left_value,
            right_value,
            failure_msg: str = None) -> None:
        """
        Assert that a value is strictly less than another value. Note that type differences here can cause issues, so
        cast your values before supplying them.

        left_value < right_value

        :param left_value: The value to verify is less than the right value.
        :param right_value: The value to verify is greater than the left value.
        :param failure_msg: Any custom failure message you'd like to supply to explain the impact or cause of a
            potential assertion failure.

        :raises AssertionError: If the left value is not less than the right value.
        """
        IAAssert._is_less_than(
            left_value=left_value,
            right_value=right_value,
            failure_msg=failure_msg,
            or_equal_to=False)

    @staticmethod
    def is_less_than_or_equal_to(
            left_value,
            right_value,
            failure_msg: Optional[str] = None) -> None:
        """
        Assert that a value is less than or equal to another value. Note that type differences here can cause issues, so
        cast your values before supplying them.

        left_value <= right_value

        :param left_value: The value to verify is less than or equal to the right value.
        :param right_value: The value to verify is greater than or equal to the left value.
        :param failure_msg: Any custom failure message you'd like to supply to explain the impact or cause of a
            potential assertion failure.

        :raises AssertionError: If the left value is not less than or equal to the right value.
        """
        IAAssert._is_less_than(
            left_value=left_value,
            right_value=right_value,
            failure_msg=failure_msg,
            or_equal_to=True)

    @staticmethod
    def is_not_equal_to(
            actual_value,
            expected_value,
            failure_msg: Optional[str] = None,
            as_type=None) -> None:
        """
        Assert that two values are not equal. Due to type differences, this function should almost always have a
        supplied type as part of the as_type argument.

        Example: A value of numeric 2 compared to a value of string "2" will return True because they are different
        types. Supplying a value of int or str for as_type will cast both as the supplied type resulting in supplied
        values of 2 and "2" as returning False (it is not true that they are not equal, meaning they are equal)
        because we will have removed the type difference as a root cause of the inequality.

        :param actual_value: The actual value to be verified.
        :param expected_value: The value expected to be reflected by the actual value.
        :param failure_msg: Any custom failure message you'd like to supply to explain the impact or cause of a
            potential assertion failure.
        :param as_type: Used to compare the two values as a specific type.

        :raises AssertionError: If the two values are equal.
        """
        if as_type is not None:
            if as_type == int:
                # must convert to float first!
                actual_value = float(actual_value)
                expected_value = float(expected_value)
            if as_type == Color:
                # special handling for color comparisons
                assert IAAssert._color_convert(color_as_string=actual_value) \
                       != IAAssert._color_convert(color_as_string=expected_value),\
                       IAAssert._generate_failure_msg(
                           msg=f'Assert {IAAssert._color_convert(color_as_string=actual_value)} != '
                               f'{IAAssert._color_convert(color_as_string=expected_value)}.',
                           failure_msg=failure_msg)
            else:
                assert as_type(actual_value) != as_type(expected_value),\
                    IAAssert._generate_failure_msg(msg=f'Assert {as_type(actual_value)} != '
                                                       f'{as_type(expected_value)}',
                                                   failure_msg=failure_msg)
        else:
            assert actual_value != expected_value,\
                IAAssert._generate_failure_msg(msg=f'Assert {actual_value} != {expected_value}',
                                               failure_msg=failure_msg)

    @staticmethod
    def is_not_true(value: bool, failure_msg: str = None) -> None:
        """
        Assert that some value is not truthy. NOTE: This is not a pure boolean check for False; falsy values like
        0 and None and empty Iterables will not raise an AssertionError here because they register as falsy in Python.

        :param value: A value you expect to be falsy, such as False, None, numeric 0, or empty Iterable types
            (including Strings).
        :param failure_msg: Any custom failure message you'd like to supply to explain the impact or cause of a
            potential assertion failure.

        :raises AssertionError: If the supplied value is truthy, such as True, any non-zero numeric value, any
            non-empty string, or any non-empty Iterable.
        """
        msg = IAAssert._generate_failure_msg(msg=f'Assert {value}',
                                             failure_msg=failure_msg)
        assert not value, msg

    @staticmethod
    def is_true(value: bool, failure_msg: str = None) -> None:
        """
        Assert that some value is truthy. NOTE: This is not a pure boolean check for True; truthy values like
        1 and non-empty Iterables will not raise an AssertionError here because they register as truthy in Python.

        :param value: A value you expect to be truthy, such as True, 1, or non-empty Iterable types  (including
            Strings).
        :param failure_msg: Any custom failure message you'd like to supply to explain the impact or cause of a
            potential assertion failure.

        :raises AssertionError: If the supplied value is falsy, such as False, 0, an empty string, or any empty
            Iterable.
        """
        msg = IAAssert._generate_failure_msg(msg=f'Assert {value}',
                                             failure_msg=failure_msg)
        assert value, msg

    @staticmethod
    def is_within_range(
            low_end_value: Union[int, float],
            value: Union[int, float],
            high_end_value: Union[int, float],
            inclusive: bool,
            failure_msg: str = None) -> None:
        """
        Assert some value falls within some defined range. Inclusion or exclusion is controlled by the inclusive arg.
        For one-sided ranges, use less-than or greater-than assertion functions.

        :param low_end_value: The low-end of your range.
        :param value: The value you are verifying falls within the range.
        :param high_end_value: The high-end of your range.
        :param inclusive: Controls whether the low-end AND high-end of your range are inclusive.
        :param failure_msg: Any custom failure message you'd like to supply to explain the impact or cause of a
            potential assertion failure.

        :raises AssertionError: If the supplied value does not fall within the defined range.
        """
        msg = IAAssert._generate_failure_msg(msg=f"Assert {low_end_value} <{'=' if inclusive else ''} {value}"
                                                 f" <{'=' if inclusive else ''} {high_end_value}",
                                             failure_msg=failure_msg)
        if inclusive:
            assert low_end_value <= value <= high_end_value, msg
        else:
            assert low_end_value < value < high_end_value, msg

    @classmethod
    def _color_convert(cls, color_as_string: str) -> str:
        """
        Selenium's color helper does not recognize alpha values in hex strings longer than 7 characters (#XXXXXX), so
        if a hex value is supplied which is longer than seven characters we will force the kwarg conversion.
        :param color_as_string: Your color as an rgb/rgba or hex string.
        :returns: The string converted to a hex representation of a color
        """
        if color_as_string and color_as_string[0] == "#" and len(color_as_string) > 7 and color_as_string[-1] == "0":
            _conv = Color.from_string(color_as_string)
            return Color(red=_conv.red,
                         green=_conv.green,
                         blue=_conv.blue,
                         alpha=0).hex
        else:
            return Color.from_string(color_as_string).hex

    @classmethod
    def _generate_failure_msg(cls, msg: str, failure_msg: str) -> str:
        """Convenience function to concatenate and pretty-print failure messages to a defined assertion message."""
        return msg if not failure_msg else msg + '\nMessage: ' + failure_msg

    @classmethod
    def _is_greater_than(
            cls, left_value, right_value, failure_msg: Optional[str] = None, or_equal_to: bool = False) -> None:
        """
        Assert that one value is greater than or potentially equal to than another value. Note that type differences
        here can cause issues, so cast your values before supplying them.

        :param left_value: The value to verify is greater than or potentially equal to the right value.
        :param right_value: The value to verify is less than or potentially equal to the left value.
        :param or_equal_to: Determines if this will be a strict equality check or a loose equality check.
        :param failure_msg: Any custom failure message you'd like to supply to explain the impact or cause of a
            potential assertion failure.

        :raises AssertionError: If the left value is not greater than or potentially equal to the right value.
        """
        msg = IAAssert._generate_failure_msg(msg=f'Assert {left_value} >{"= " if or_equal_to else " "}{right_value}.',
                                             failure_msg=failure_msg)
        if or_equal_to:
            assert left_value >= right_value, msg
        else:
            assert left_value > right_value, msg

    @classmethod
    def _is_less_than(cls, left_value, right_value, failure_msg: str = None, or_equal_to: bool = False) -> None:
        """
        Assert that one value is less than or potentially equal to than another value. Note that type differences
        here can cause issues, so cast your values before supplying them.

        :param left_value: The value to verify is less than or potentially equal to the right value.
        :param right_value: The value to verify is greater than or potentially equal to the left value.
        :param or_equal_to: Determines if this will be a strict equality check or a loose equality check.
        :param failure_msg: Any custom failure message you'd like to supply to explain the impact or cause of a
            potential assertion failure.

        :raises AssertionError: If the left value is not less than or potentially equal to the right value.
        """
        msg = IAAssert._generate_failure_msg(msg=f'Assert {left_value} <{"= " if or_equal_to else " "}{right_value}.',
                                             failure_msg=failure_msg)
        if or_equal_to:
            assert left_value <= right_value, msg
        else:
            assert left_value < right_value, msg
