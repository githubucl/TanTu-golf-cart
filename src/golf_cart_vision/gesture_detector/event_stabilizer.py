from __future__ import annotations

from dataclasses import dataclass
import time

from golf_cart_vision.gesture_detector.detection_types import GestureEvent


@dataclass(frozen=True)
class StabilizerOutput:
    raw_event: GestureEvent
    stable_event: GestureEvent
    candidate_event: GestureEvent
    candidate_count: int
    candidate_elapsed_seconds: float
    confirmation_seconds: float


class GestureEventStabilizer:
    """Requires the same gesture for a duration before it reaches the state machine."""

    _TIME_EPSILON_SECONDS = 1e-9

    def __init__(
        self,
        confirmation_seconds: float = 0.2,
        missing_tolerance_seconds: float = 0.1,
    ) -> None:
        if confirmation_seconds <= 0:
            raise ValueError("confirmation_seconds must be greater than 0")
        if missing_tolerance_seconds < 0:
            raise ValueError("missing_tolerance_seconds must be at least 0")

        self._confirmation_seconds = confirmation_seconds
        self._missing_tolerance_seconds = missing_tolerance_seconds
        self._candidate_event = GestureEvent.NO_GESTURE
        self._candidate_count = 0
        self._candidate_started_at: float | None = None
        self._last_seen_at: float | None = None

    def update(
        self,
        raw_event: GestureEvent,
        now_seconds: float | None = None,
    ) -> StabilizerOutput:
        now = time.monotonic() if now_seconds is None else now_seconds
        if raw_event == GestureEvent.NO_GESTURE:
            self._handle_missing_event(now)
        elif raw_event == self._candidate_event:
            self._candidate_count += 1
            self._last_seen_at = now
        else:
            self._candidate_event = raw_event
            self._candidate_count = 1
            self._candidate_started_at = now
            self._last_seen_at = now

        candidate_elapsed_seconds = self._candidate_elapsed_seconds(now)

        stable_event = (
            self._candidate_event
            if (
                raw_event != GestureEvent.NO_GESTURE
                and candidate_elapsed_seconds + self._TIME_EPSILON_SECONDS
                >= self._confirmation_seconds
            )
            else GestureEvent.NO_GESTURE
        )

        return StabilizerOutput(
            raw_event=raw_event,
            stable_event=stable_event,
            candidate_event=self._candidate_event,
            candidate_count=self._candidate_count,
            candidate_elapsed_seconds=candidate_elapsed_seconds,
            confirmation_seconds=self._confirmation_seconds,
        )

    def _handle_missing_event(self, now: float) -> None:
        if self._candidate_event == GestureEvent.NO_GESTURE:
            return

        if (
            self._last_seen_at is not None
            and now - self._last_seen_at <= self._missing_tolerance_seconds
        ):
            return

        self._candidate_event = GestureEvent.NO_GESTURE
        self._candidate_count = 0
        self._candidate_started_at = None
        self._last_seen_at = None

    def _candidate_elapsed_seconds(self, now: float) -> float:
        if self._candidate_started_at is None:
            return 0.0
        return max(0.0, now - self._candidate_started_at)
