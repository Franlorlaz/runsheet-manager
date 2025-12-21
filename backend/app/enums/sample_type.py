from enum import Enum


class SampleType(str, Enum):
    wafer = "wafer"
    dice = "dice"
    other = "other"
