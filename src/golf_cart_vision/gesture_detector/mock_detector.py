from __future__ import annotations

from collections.abc import Sequence

from golf_cart_vision.gesture_detector.detection_types import (
    BoundingBox,
    DetectorOutput,
    GestureDetection,
    GestureEvent,
)


class MockGestureDetector:
    """A predictable detector used before a real YOLO model exists."""

    def __init__(self, gesture_sequence: Sequence[str]) -> None:
        if not gesture_sequence:
            raise ValueError("gesture_sequence must contain at least one item")
        self._sequence = list(gesture_sequence)
        self._index = 0

    def detect(self, frame: object | None = None) -> DetectorOutput:
        del frame
        gesture_name = self._sequence[self._index % len(self._sequence)]
        self._index += 1

        if gesture_name == "start":
            return DetectorOutput(
                event=GestureEvent.START_GESTURE,
                detections=[
                    GestureDetection(
                        class_id=1,
                        class_name="start_follow",
                        confidence=0.95,
                        bbox=BoundingBox(120, 80, 240, 220),
                    )
                ],
            )

        if gesture_name == "stop":
            return DetectorOutput(
                event=GestureEvent.STOP_GESTURE,
                detections=[
                    GestureDetection(
                        class_id=2,
                        class_name="stop_follow",
                        confidence=0.93,
                        bbox=BoundingBox(130, 90, 250, 230),
                    )
                ],
            )

        return DetectorOutput(event=GestureEvent.NO_GESTURE, detections=[])
