from Helpers.Ignition.Alarm import AlarmDefinition


class PerspectiveAlarm(object):
    """
    Defines the configuration of an Ignition alarm, and is not intended to be used for storing information
    about the state of an alarm over a period of time. Specifically, this class stores information about the
    important configuration attributes Perspective could have need of while interacting with the Alarm Tables, where
    information like `source_path` is required while working with shelved alarms.
    """

    def __init__(self, name: str, display_path: str, priority: str, label: str,
                 source_path: str, tag_path: str, notes: str = None):
        self.name = name
        self.display_path = display_path
        self.priority = priority
        self.label = label
        self.notes = notes
        self.source_path = source_path
        self.tag_path = tag_path
        self.notes = notes

    def get_alarm_definition(self) -> AlarmDefinition:
        definition = AlarmDefinition(name=self.name)
        definition.display_path = self.display_path
        definition.priority = self.priority
        definition.label = self.label
        definition.notes = self.notes
        definition.source = self.source_path
        definition.tag_path = self.tag_path
        definition.notes = self.notes
        return definition
