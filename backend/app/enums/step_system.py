from enum import Enum


class StepSystem(str, Enum):
    wet_bench = "Wet-Bench"
    ald_oxford = "ALD Oxford"
    ald_picosun = "ALD Picosun"
    other = "Other"
