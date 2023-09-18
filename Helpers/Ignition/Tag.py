import copy
import json
import re
from enum import Enum
from typing import List, Dict

from Helpers.Ignition.Alarm import AlarmHelper, AlarmDefinition


class DataType(Enum):
    BYTE = 'Int1'
    SHORT = 'Int2'
    INTEGER = 'Int4'
    LONG = 'Int8'
    FLOAT = 'Float4'
    DOUBLE = 'Float8'
    BOOLEAN = 'Boolean'
    STRING = 'String'
    DATE_TIME = 'DateTime'
    TEXT = 'Text'
    BYTE_ARRAY = 'Int1Array'
    SHORT_ARRAY = 'Int2Array'
    INTEGER_ARRAY = 'Int4Array'
    LONG_ARRAY = 'Int8Array'
    FLOAT_ARRAY = 'Float4Array'
    DOUBLE_ARRAY = 'Float8Array'
    BOOLEAN_ARRAY = 'BooleanArray'
    STRING_ARRAY = 'StringArray'
    DATE_TIME_ARRAY = 'DateTimeArray'
    DATASET = 'DataSet'
    DOCUMENT = 'Document'


class ValueSource(Enum):
    DERIVED = 'derived'
    EXPRESSION = 'expr'
    MEMORY = 'memory'
    OPC = 'opc'
    QUERY = 'db'
    REFERENCE = 'reference'


class SampleMode(Enum):
    PERODIC = 'Periodic'
    ON_CHANGE = 'OnChange'
    TAG_GROUP = 'TagGroup'


class _BaseTag(object):
    _name = None
    _path = None
    _provider = None
    tag_type = None
    access_rights = None
    alarm_eval_enabled = None
    alarms = None
    clamp_mode = None
    data_type: DataType = None
    deadband = None
    deadband_mode = None
    default_eng_units = None
    documentation = None
    enabled = None
    eng_high = None
    eng_limit_mode = None
    eng_low = None
    eng_unit = None
    event_scripts = None
    execution_mode = None
    execution_rate = None
    format_string = None
    historical_deadband_style = None
    history_enabled = None
    history_provider = None
    history_tag_group = None
    permission_model = None
    persist_value = None
    quality = None
    raw_high = None
    raw_low = None
    read_only = None
    read_permissions = None
    sample_mode: SampleMode = None
    scale_factor = None
    scale_mode = None
    scaled_high = None
    scaled_low = None
    tag_group = None
    timestamp = None
    tooltip = None
    type_color = None
    type_id = None
    value = None
    value_source: ValueSource = None
    write_permissions = None

    def __init__(self, name: str, path: str, provider: str = '[default]'):
        self._name = name
        self._path = path
        self._provider = f'{provider}'
        self._base_path = f'{self._provider}{path}'
        self._full_path = f'{self._base_path}{name}' if self._path == '' else f'{self._base_path}/{name}'

    def get_name(self) -> str:
        return self._name

    def get_path(self) -> str:
        return self._path

    def get_provider(self):
        return self._provider

    def get_base_path(self) -> str:
        return self._base_path

    def get_full_path(self) -> str:
        return self._full_path

    def to_dict(self) -> Dict:
        local_tag = self.duplicate()
        special_case = ['_name']
        not_used = ['_path', '_base_path', '_provider', '_full_path', '_type_id_path']
        # Get set attributes of the Tag Object
        attrs = vars(
            local_tag)
        tag_dict = {}
        for item in not_used:
            if item in attrs:
                del attrs[item]
        for item in special_case:
            new_item = item.replace('_', '')
            attrs[new_item] = attrs[item]
            del attrs[item]
        for attr in attrs:
            ignition_key = self._to_camel_case(
                name=attr)
            if getattr(local_tag, attr) is None:
                pass
            elif isinstance(getattr(local_tag, attr), Enum):
                tag_dict[ignition_key] = getattr(local_tag, attr).value
            else:
                tag_dict[ignition_key] = getattr(local_tag, attr)
        return tag_dict

    def diff(self, expected_tag):
        """Compares current tag definition to and expected tag definition and returns any differences"""
        return {
            'actual_extra_keys': self.diff_my_unmatched_keys_values(
                compare_tag=expected_tag),
            'expected_extra_keys': self.diff_their_unmatched_keys_values(
                compare_tag=expected_tag),
            'diff_values': self.diff_key_values(
                expected_tag=expected_tag)
        }

    def duplicate(self):
        return copy.deepcopy(self)

    def diff_key_values(self, expected_tag):
        """Compares the keys 2 tag definitions have in common and returns value differences"""
        diff_values = {}
        for my_key in self.to_dict().keys():
            if my_key not in self.diff_my_unmatched_keys(
                    compare_tag=expected_tag):
                if self.to_dict()[my_key] != expected_tag.to_dict()[my_key]:
                    diff_values[my_key] = {'actual': self.to_dict()[my_key], 'expected': expected_tag.to_dict()[my_key]}
        return diff_values

    def diff_my_unmatched_keys_values(self, compare_tag):
        """Compares against another tag definition and returns keys & values that are unique to this tag"""
        result = {}
        for key in self.diff_my_unmatched_keys(
                compare_tag=compare_tag):
            result[key] = self.to_dict()[key]
        return result

    def diff_their_unmatched_keys_values(self, compare_tag):
        """Compares against another tag definition and returns keys & values that are unique to the other tag"""
        result = {}
        for key in self.diff_their_unmatched_keys(
                compare_tag=compare_tag):
            result[key] = compare_tag.to_dict()[key]
        return result

    def diff_my_unmatched_keys(self, compare_tag):
        """Compares against another tag definition and returns keys that are unique to this tag"""
        return self._get_unmatched_keys(
            dict_keys1=self.to_dict().keys(),
            dict_keys2=compare_tag.to_dict().keys())

    def diff_their_unmatched_keys(self, compare_tag):
        """Compares against another tag definition and returns keys that are unique to the other tag"""
        return self._get_unmatched_keys(
            dict_keys1=compare_tag.to_dict().keys(),
            dict_keys2=self.to_dict().keys())

    @staticmethod
    def _get_unmatched_keys(dict_keys1, dict_keys2):
        key_diffs = []
        for key in dict_keys1:
            if key not in dict_keys2:
                key_diffs.append(key)
        return key_diffs

    @staticmethod
    def _to_camel_case(name):
        init, *temp = name.split(
            '_')
        return ''.join(
            [init.lower(), *map(
                str.title,
                temp)])

    def __str__(self):
        return str(
            self.to_dict())


class Tag(_BaseTag):
    """
    The Tag class allows for easy storage and reference of Tag attributes. This class does not perform as a Tag, only
    storing information for later reference.
    """
    def __init__(self, name: str, path: str, provider: str = '[default]'):
        super().__init__(
            name=name,
            path=path,
            provider=provider)
        self.tag_type = 'AtomicTag'
        self.value_source = ValueSource.MEMORY

    def get_alarm(self, alarm_name: str) -> AlarmDefinition:
        """
        Get a specific AlarmDefinition from a self.alarms list returned from an Ignition Gateway

        :param alarm_name: The name of the alarm definition you would like to obtain.

        :return: The AlarmDefinition configuration for the specified alarm.
        """
        for alarm in self.get_alarms():
            if alarm.get_name() == alarm_name:
                return alarm

    def get_alarms(self) -> List[AlarmDefinition]:
        """
        Get a list of configured AlarmDefinitions from this Tag.

        :returns: All Alarm configurations for this Tag.
        """
        my_alarms = []
        for alarm in copy.deepcopy(self.alarms):
            my_alarms.append(AlarmHelper.build_alarm_from_string(json.dumps(alarm)))
        return my_alarms

    def replace_alarm(self, alarm_name: str, new_config: dict):
        """Replace a specific alarm with a dict representation of a new alarm"""
        if self.alarms is not None:
            self.alarms[:] = [alarm for alarm in self.alarms if not alarm['name'] == alarm_name]
            self.alarms.append(new_config)
        else:
            self.alarms = [new_config]


class _ComplexTag(_BaseTag):
    tags = []

    def to_dict(self):
        local_tag = self.duplicate()
        special_case = ['_name']
        not_used = ['_path', '_base_path', '_provider', '_full_path', '_type_id_path']
        # Get set attributes of the Tag Object
        attrs = vars(
            local_tag)
        tag_dict = {}
        for item in not_used:
            if item in attrs:
                del attrs[item]
        for item in special_case:
            new_item = item.replace('_', '')
            attrs[new_item] = attrs[item]
            del attrs[item]
        for attr in attrs:
            ignition_key = self._to_camel_case(
                name=attr)
            if getattr(local_tag, attr) is None:
                pass
            elif isinstance(getattr(local_tag, attr), Enum):
                tag_dict[ignition_key] = getattr(local_tag, attr).value
            else:
                tag_dict[ignition_key] = getattr(local_tag, attr)
        if local_tag.tags != [] and 'tags' not in tag_dict:
            tag_dict['tags'] = local_tag.tags
        return tag_dict

    def diff_key_values(self, expected_tag):
        """Compares the keys 2 tag definitions have in common and returns value differences,
        includes special handling for 'tags' included in _ComplexTag objects"""
        diff_values = {}
        for my_key in self.to_dict().keys():
            if my_key not in self.diff_my_unmatched_keys(
                    compare_tag=expected_tag):
                if self.to_dict()[my_key] != expected_tag.to_dict()[my_key]:
                    diff_values[my_key] = {'actual': self.to_dict()[my_key], 'expected': expected_tag.to_dict()[my_key]}
        if 'tags' in diff_values:
            diff_values['tags'] = self.get_tag_differences(actual=diff_values['tags']['actual'],
                                                           expected=diff_values['tags']['expected'])

        return diff_values

    def get_member_tag(self, member_tag_name: str):
        """Get Tag object of a specific tag from a self.tags list returned from an Ignition Gateway"""
        tags = copy.deepcopy(self.tags)
        for tag in tags:
            if tag['name'] == member_tag_name:
                return TagHelper.build_tag_from_string(json.dumps(tag))

    def get_member_tags(self):
        """Get list of Tag objects from a self.tags list returned from an Ignition Gateway"""
        tags = copy.deepcopy(self.tags)
        my_tags = []
        for tag in tags:
            my_tags.append(self.get_member_tag(tag['name']))
        return my_tags

    def replace_member_tag(self, tag_name, new_config: dict):
        """Replace a specific tag with a dict representation of a new tag"""
        if self.tags is not None:
            self.tags[:] = [tag for tag in self.tags if not tag['name'] == tag_name]
            self.tags.append(new_config)
        else:
            self.tags = [new_config]

    @staticmethod
    def get_tag_differences(actual: list, expected: list):
        """Get the differences between two list of string representations of dicts that contain Tag Definitions
        This is normally what is returned from an Ignition Gateway"""
        actual_tags = []
        expected_tags = []
        tags_processed = []
        failures = {}
        for tag in actual:
            actual_tags.append(TagHelper.build_tag_from_string(
                dict_as_string=json.dumps(tag)))
        for tag in expected:
            expected_tags.append(TagHelper.build_tag_from_string(
                dict_as_string=json.dumps(tag)))

        for expected_tag in expected_tags:
            for actual_tag in actual_tags:
                if actual_tag.get_full_path() == expected_tag.get_full_path():
                    tags_processed.append(expected_tag.get_full_path())
                    if expected_tag.to_dict() != actual_tag.to_dict():
                        failures[expected_tag.get_full_path()] = actual_tag.diff(expected_tag=expected_tag)
        for expected_tag in expected_tags:
            if expected_tag.get_full_path() not in tags_processed:
                failures[expected_tag.get_full_path()] = {'actual': '', 'expected_tag': expected_tag.to_dict()}
        for actual_tag in actual_tags:
            if actual_tag.get_full_path() not in tags_processed:
                failures[actual_tag.get_full_path()] = {'actual': actual_tag.to_dict(), 'expected_tag': ''}

        return failures


class UdtInstance(_ComplexTag):
    type_id = None
    parameters = []

    def __init__(self, name: str, path: str, type_id: str, provider: str = '[default]'):
        super().__init__(
            name=name,
            path=path,
            provider=provider)
        self.tag_type = 'UdtInstance'
        self.type_id = type_id


class UdtDef(_ComplexTag):
    _type_id_path = None
    type_id = None
    parameters = []

    def __init__(self, name: str, path: str, provider: str = '[default]'):
        super().__init__(
            name=name,
            path=path,
            provider=provider)
        self.tag_type = 'UdtType'
        self._type_id_path = f'{self.get_path()}/{self.get_name()}'.replace('_types_/', '')

    def get_type_id_path(self):
        return self._type_id_path


class Folder(_ComplexTag):
    def __init__(self, name: str, path: str, provider: str = '[default]'):
        super().__init__(
            name=name,
            path=path,
            provider=provider)
        self.tag_type = 'Folder'
        self._path = f'{name}' if self._path == '' else f'{self._path}/{name}'


class TagHelper:
    @staticmethod
    def build_tag_from_string(dict_as_string: str):
        """Build a Tag, UdtInstance, UdtDef or Folder object from a string representation of a dict"""
        provider = ''
        path = ''
        response_json = json.loads(dict_as_string)
        if 'error' not in response_json:
            if isinstance(response_json, list):
                response_json = response_json[0]
            name = response_json.get('name')
            if 'path' in response_json:
                provider = f'[{response_json.get("path").get("source")}]'
                path = TagHelper._process_path(response_json.get('path', '').get('pathParts', ''))
            if response_json.get('tagType') == 'UdtInstance':
                tag = UdtInstance(name=name, provider=provider, path=path, type_id='')
            elif response_json.get('tagType') == 'UdtType':
                tag = UdtDef(name=name, provider=provider, path=path)
            elif response_json.get('tagType') == 'Folder':
                tag = Folder(name=name, provider=provider, path=path)
            else:
                tag = Tag(name=name, provider=provider, path=path)
            for key in response_json.keys():
                tag = TagHelper._process_key(tag, key, response_json[key])
            return tag

    @staticmethod
    def convert_tags_to_config_dicts(tag_list: list):
        """Convert a list of _baseTag objects a list of dicts to use for importing into Ignition"""
        tags = []
        for tag in tag_list:
            tags.append(tag.to_dict())
        return tags

    @staticmethod
    def _process_path(path_parts: json):
        path_parts.pop()
        return '/'.join(path_parts)

    @staticmethod
    def _process_key(tag: Tag, key: str, value: object):
        excluded_types = ['path', 'name']
        if key not in excluded_types:
            mapped_key = TagHelper._to_snake_case(key)
            setattr(tag, mapped_key, value)
        return tag

    @staticmethod
    def _to_snake_case(name):
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        name = re.sub('__([A-Z])', r'_\1', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
        return name.lower()
