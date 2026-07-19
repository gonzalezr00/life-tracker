"""
Macro calculator for the fitness domain.

Designed to slot into core/domains/fitness/service.py once the storage
interface (core/storage/base.py) is finalized. For now it's fed plain
dataclasses so it can be built and tested independently of the DB.

Architecture:
    - Enums              closed vocabularies (Sex, ActivityLevel, GoalDirection)
    - FitnessProfile     static-ish attributes of a person (height, age, sex...)
    - BodyweightGoal     current + target weight, optional deadline
    - BMRFormula         abstract strategy for basal metabolic rate calculations
    - MifflinStJeor      concrete BMR strategy (default)
    - MacroPlan          result object: calorie + macro targets
    - MacroPlanner       orchestrating service — the main entry point
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from enum import Enum


class Sex(Enum):
    MALE = "male"
    FEMALE = "female"


class ActivityLevel(Enum):
    SEDENTARY = "sedentary"  # little/no exercise
    LIGHT = "light"  # light exercise 1-3 days/week
    MODERATE = "moderate"  # moderate exercise 3-5 days/week
    ACTIVE = "active"  # hard exercise 6-7 days/week
    VERY_ACTIVE = "very_active"  # very hard exercise + physical job

    @property
    def multiplier(self) -> float:
        return {
            ActivityLevel.SEDENTARY: 1.2,
            ActivityLevel.LIGHT: 1.375,
            ActivityLevel.MODERATE: 1.55,
            ActivityLevel.ACTIVE: 1.725,
            ActivityLevel.VERY_ACTIVE: 1.9,
        }[self]


class GoalDirection(Enum):
    CUT = "cut"
    MAINTAIN = "maintain"
    BULK = "bulk"
