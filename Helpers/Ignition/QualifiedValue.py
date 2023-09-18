from datetime import datetime
from enum import Enum
from typing import Optional, Any


class LegacyQualityCode(Enum):
    GOOD_UNSPECIFIED = 0
    GOOD_WRITEPENDING = 2
    GOOD = 192
    GOOD_PROVISIONAL = 200
    GOOD_INITIAL = 201
    GOOD_OVERLOAD = 202
    GOOD_BACKFILL = 203
    UNCERTAIN = 256
    UNCERTAIN_LASTKNOWNVALUE = 257
    UNCERTAIN_INITIALVALUE = 258
    UNCERTAIN_DATASUBNORMAL = 259
    UNCERTAIN_ENGINEERINGUNITSEXCEEDED = 260
    UNCERTAIN_INCOMPLETEOPERATION = 261
    BAD = 512
    BAD_UNAUTHORIZED = 513
    BAD_ACCESSDENIED = 514
    BAD_DISABLED = 515
    BAD_STALE = 516
    BAD_TRIALEXPIRED = 517
    BAD_LICENSEEXCEEDED = 518
    BAD_NOTFOUND = 519
    BAD_REFERENCENOTFOUND = 520
    BAD_AGGREGATENOTFOUND = 521
    BAD_NOTCONNECTED = 522
    BAD_GATEWAYCOMMOFF = 523
    BAD_OUTOFRANGE = 524
    BAD_DATABASENOTCONNECTED = 525
    BAD_READONLY = 526
    BAD_FAILURE = 527
    BAD_UNSUPPORTED = 528
    ERROR = 768
    ERROR_CONFIGURATION = 769
    ERROR_EXPRESSIONEVAL = 770
    ERROR_TAGEXECUTION = 771
    ERROR_TYPECONVERSION = 772
    ERROR_DATABASEQUERY = 773
    ERROR_IO = 774
    ERROR_TIMEOUTEXPIRED = 775
    ERROR_EXCEPTION = 776
    ERROR_INVALIDPATHSYNTAX = 777
    ERROR_FORMATTING = 778
    ERROR_SCRIPTEVAL = 779
    ERROR_CYCLEDETECTED = 780


class QualifiedValue:
    """
    The QualifiedValue class is provided as a way to store Qualified Value objects with easy to reference attributes.
    """

    def __init__(
            self,
            value: Optional[Any] = None,
            quality: LegacyQualityCode = LegacyQualityCode.UNCERTAIN,
            timestamp: datetime = datetime.now()):
        self.value = value
        self.quality = quality
        self.timestamp = timestamp
