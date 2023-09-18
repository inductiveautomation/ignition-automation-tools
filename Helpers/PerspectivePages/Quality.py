from enum import Enum


class PerspectiveQuality(Enum):
    """
    These "qualities" are representative of Perspective's handling of Ignition Quality Codes, and differ slightly
    from the normal wording (ie: "unknown" vs "uncertain"). These qualities are intended only to be used within the
    context of Perspective Pages, in order to assist with areas which must address or reference Qualities in
    Perspective or the Quality Overlays of Perspective Components.
    """
    ERROR = 'error'
    UNKNOWN = 'unknown'
    PENDING = 'pending'
