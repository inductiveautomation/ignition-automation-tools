import copy
import json
import re
from enum import Enum
from typing import Dict, List, Optional


class AlarmState(Enum):
    """
    An enumeration of the possible states an alarm could have. Each state here should have a matching event type in
    Ignition's Alarm Journal.
    """
    ACKNOWLEDGED = 'Acknowledged'
    ACTIVE = 'Active'
    CLEARED = 'Cleared'
    UNACKNOWLEDGED = 'Unacknowledged'
    SYSTEM = 'System'
    ENABLED = 'Enabled'
    DISABLED = 'Disabled'


class AlarmStatusTableAlarmState(Enum):
    """
    The Alarm Status Table has its own unique set of states, built out of intersections of basic Alarm States.
    """
    ACTIVE_ACKNOWLEDGED = ", ".join([AlarmState.ACTIVE.value, AlarmState.ACKNOWLEDGED.value])
    ACTIVE_UNACKNOWLEDGED = ", ".join([AlarmState.ACTIVE.value, AlarmState.UNACKNOWLEDGED.value])
    CLEARED_ACKNOWLEDGED = ", ".join([AlarmState.CLEARED.value, AlarmState.ACKNOWLEDGED.value])
    CLEARED_UNACKNOWLEDGED = ", ".join([AlarmState.CLEARED.value, AlarmState.UNACKNOWLEDGED.value])


class AlarmPriority(Enum):
    """
    An enumeration of the possible priorities an alarm could have.
    """
    CRITICAL = 'Critical'
    DIAGNOSTIC = 'Diagnostic'
    HIGH = 'High'
    LOW = 'Low'
    MEDIUM = 'Medium'


class AlarmMode(Enum):
    EQUALITY = 'Equality'
    INEQUALITY = 'Inequality'
    ABOVE_VALUE = 'AboveValue'
    BELOW_VALUE = 'BelowValue'
    BETWEEN_VALUES = 'BetweenValues'
    OUTSIDE_VALUES = 'OutsideValues'
    OUT_OF_ENG_RANGE = 'OutOfEngRange'
    BAD_QUALITY = 'BadQuality'
    ANY_CHANGE = 'AnyChange'
    BIT = 'Bit'
    ON_CONDITION = 'OnCondition'


class AlarmDefinition(object):

    def __init__(self, name: str):
        self._name = name
        self.ack_mode = None
        self.ack_notes_reqd = None
        self.ack_pipeline = None
        self.active_pipeline = None
        self.clear_pipeline = None
        self.deadband = None
        self.deadband_eval_mode = None
        self.display_path = None
        self.enabled = None
        self.label = None
        self.notes = None
        self.notify_initial_event = None
        self.pipeline_project = None
        self.priority: Optional[AlarmPriority] = None
        self.shelving_allowed = None
        self.time_off_delay_seconds = None
        self.time_on_delay_seconds = None
        self.timestamp_source = None

        # Alarm Mode Settings
        self.active_condition = None
        self.any_change = None
        self.bit_on_zero = None
        self.bit_position = None
        self.display_name = None
        self.inclusive_a = None
        self.inclusive_b = None
        self.mode: Optional[AlarmMode] = None
        self.on_each_evaluation = None
        self.setpoint_a = None
        self.setpoint_b = None

    def get_name(self) -> str:
        return self._name

    def to_dict(self) -> Dict:
        local_alarm = self.duplicate()
        special_case = ['_name']
        # Get set attributes of the Tag Object
        attrs = vars(local_alarm)
        alarm_dict = {}
        for item in special_case:
            new_item = item.replace('_', '')
            attrs[new_item] = attrs[item]
            del attrs[item]
        for attr in attrs:
            ignition_key = self._to_camel_case(attr)
            if getattr(local_alarm, attr) is not None:
                if isinstance(getattr(local_alarm, attr), Enum):
                    alarm_dict[ignition_key] = getattr(local_alarm, attr).value
                else:
                    alarm_dict[ignition_key] = getattr(local_alarm, attr)
        return alarm_dict

    def duplicate(self):
        return copy.deepcopy(self)

    @staticmethod
    def _to_camel_case(name) -> str:
        init, *temp = name.split('_')
        return ''.join([init.lower(), *map(str.title, temp)])


class AlarmHelper:
    @staticmethod
    def build_alarm_from_string(dict_as_string: str) -> AlarmDefinition:
        """Creates an AlarmDefinition object from a string representation of a python dict
        Used for converting alarm definitions the Ignition Gateway provides into Objects"""
        response_json = json.loads(
            dict_as_string)
        if 'error' not in response_json:
            if isinstance(
                    response_json,
                    list):
                response_json = response_json[0]
            name = response_json.get('name')
            alarm = AlarmDefinition(
                    name=name)
            for key in response_json.keys():
                alarm = AlarmHelper._process_key(
                    alarm,
                    key,
                    response_json[key])
            return alarm

    @staticmethod
    def convert_alarmdefs_to_config_dicts(alarm_list: List[AlarmDefinition]) -> List[Dict]:
        """Take a list of AlarmDefinition objects and convert them into a list of dicts """
        alarms = []
        for alarm in alarm_list:
            alarms.append(
                alarm.to_dict())
        return alarms

    @staticmethod
    def _process_path(path_parts: json):
        path_parts.pop()
        return '/'.join(
            path_parts)

    @staticmethod
    def _process_key(alarm: AlarmDefinition, key: str, value: object):
        excluded_types = ['path', 'name']
        if key not in excluded_types:
            mapped_key = AlarmHelper._to_snake_case(
                key)
            setattr(
                alarm,
                mapped_key,
                value)
        return alarm

    @staticmethod
    def _to_snake_case(name):
        name = re.sub(
            '(.)([A-Z][a-z]+)',
            r'\1_\2',
            name)
        name = re.sub(
            '__([A-Z])',
            r'_\1',
            name)
        name = re.sub(
            '([a-z0-9])([A-Z])',
            r'\1_\2',
            name)
        return name.lower()
