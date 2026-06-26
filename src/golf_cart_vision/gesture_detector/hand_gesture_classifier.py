from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import hypot


class HandGesture(str, Enum):
    UNKNOWN = "unknown"
    OPEN_PALM_SPREAD = "open_palm_spread"
    OPEN_PALM_JOINED = "open_palm_joined"


@dataclass(frozen=True)
class NormalizedPoint:
    x: float
    y: float
    z: float = 0.0


@dataclass(frozen=True)
class HandGestureResult:
    gesture: HandGesture
    confidence: float
    extended_finger_count: int
    spread_ratio: float


class SimpleHandGestureClassifier:
    """Classifies a hand using MediaPipe's 21 normalized hand landmarks."""

    _FINGER_TIPS = (8, 12, 16, 20)
    _FINGER_JOINTS = (
        (8, 6),   # index tip, pip
        (12, 10), # middle tip, pip
        (16, 14), # ring tip, pip
        (20, 18), # pinky tip, pip
    )

    def __init__(self, spread_threshold: float = 0.55) -> None:
        self._spread_threshold = spread_threshold

    @property
    def spread_threshold(self) -> float:
        return self._spread_threshold

    def classify(self, landmarks: list[NormalizedPoint]) -> HandGestureResult:
        if len(landmarks) != 21:
            raise ValueError(f"Expected 21 hand landmarks, got {len(landmarks)}")

        extended_count = sum(
            1 for tip_index, pip_index in self._FINGER_JOINTS
            if self._is_finger_extended(landmarks[tip_index], landmarks[pip_index])
        )
        spread_ratio = self._finger_spread_ratio(landmarks)

        if extended_count < 4:
            return HandGestureResult(
                gesture=HandGesture.UNKNOWN,
                confidence=0.2,
                extended_finger_count=extended_count,
                spread_ratio=spread_ratio,
            )

        if spread_ratio >= self._spread_threshold:
            return HandGestureResult(
                gesture=HandGesture.OPEN_PALM_SPREAD,
                confidence=self._confidence_from_threshold_distance(spread_ratio),
                extended_finger_count=extended_count,
                spread_ratio=spread_ratio,
            )

        return HandGestureResult(
            gesture=HandGesture.OPEN_PALM_JOINED,
            confidence=self._confidence_from_threshold_distance(spread_ratio),
            extended_finger_count=extended_count,
            spread_ratio=spread_ratio,
        )

    @staticmethod
    def _is_finger_extended(tip: NormalizedPoint, pip: NormalizedPoint) -> bool:
        # In image coordinates, smaller y means higher on the image.
        return tip.y < pip.y

    def _finger_spread_ratio(self, landmarks: list[NormalizedPoint]) -> float:
        gaps = [
            self._distance(landmarks[left_tip], landmarks[right_tip])
            for left_tip, right_tip in zip(self._FINGER_TIPS, self._FINGER_TIPS[1:])
        ]
        average_tip_gap = sum(gaps) / len(gaps)
        palm_width = max(self._distance(landmarks[5], landmarks[17]), 1e-6)
        return average_tip_gap / palm_width

    def _confidence_from_threshold_distance(self, spread_ratio: float) -> float:
        distance_from_threshold = abs(spread_ratio - self._spread_threshold)
        return min(0.99, 0.6 + distance_from_threshold)

    @staticmethod
    def _distance(first: NormalizedPoint, second: NormalizedPoint) -> float:
        return hypot(first.x - second.x, first.y - second.y)
