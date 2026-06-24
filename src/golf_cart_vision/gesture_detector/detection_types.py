from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GestureEvent(str, Enum):
    NO_GESTURE = "NO_GESTURE"
    START_GESTURE = "START_GESTURE"
    STOP_GESTURE = "STOP_GESTURE"


@dataclass(frozen=True)
class BoundingBox:
    x1: int
    y1: int
    x2: int
    y2: int


@dataclass(frozen=True)
class GestureDetection:
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox | None = None


@dataclass(frozen=True)
class DetectorOutput:
    event: GestureEvent
    detections: list[GestureDetection]
