from __future__ import annotations

from dataclasses import dataclass

from golf_cart_vision.gesture_detector.detection_types import GestureEvent


@dataclass(frozen=True)
class StabilizerOutput:
    raw_event: GestureEvent
    stable_event: GestureEvent
    candidate_event: GestureEvent
    candidate_count: int
    confirmation_frames: int


class GestureEventStabilizer:
    """Requires the same gesture for multiple frames before it reaches the state machine."""

    def __init__(
        self,
        confirmation_frames: int = 2,
        missing_tolerance_frames: int = 1,
    ) -> None:
        if confirmation_frames < 1:
            raise ValueError("confirmation_frames must be at least 1")
        if missing_tolerance_frames < 0:
            raise ValueError("missing_tolerance_frames must be at least 0")

        self._confirmation_frames = confirmation_frames
        self._missing_tolerance_frames = missing_tolerance_frames
        self._candidate_event = GestureEvent.NO_GESTURE
        self._candidate_count = 0
        self._missing_count = 0

    def update(self, raw_event: GestureEvent) -> StabilizerOutput:
        if raw_event == GestureEvent.NO_GESTURE:
            self._handle_missing_event()
        elif raw_event == self._candidate_event:
            self._candidate_count += 1
            self._missing_count = 0
        else:
            self._candidate_event = raw_event
            self._candidate_count = 1
            self._missing_count = 0

        stable_event = (
            self._candidate_event
            if (
                raw_event != GestureEvent.NO_GESTURE
                and self._candidate_count >= self._confirmation_frames
            )
            else GestureEvent.NO_GESTURE
        )

        return StabilizerOutput(
            raw_event=raw_event,
            stable_event=stable_event,
            candidate_event=self._candidate_event,
            candidate_count=self._candidate_count,
            confirmation_frames=self._confirmation_frames,
        )

    def _handle_missing_event(self) -> None:
        if self._candidate_event == GestureEvent.NO_GESTURE:
            return

        if self._missing_count < self._missing_tolerance_frames:
            self._missing_count += 1
            return

        self._candidate_event = GestureEvent.NO_GESTURE
        self._candidate_count = 0
        self._missing_count = 0
