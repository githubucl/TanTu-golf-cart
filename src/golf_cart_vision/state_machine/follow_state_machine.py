from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from golf_cart_vision.gesture_detector.detection_types import GestureEvent


class FollowState(str, Enum):
    IDLE = "IDLE"
    FOLLOWING = "FOLLOWING"


class MockCommand(str, Enum):
    START_FOLLOW = "START_FOLLOW"
    STOP_FOLLOW = "STOP_FOLLOW"


@dataclass(frozen=True)
class TransitionResult:
    old_state: FollowState
    new_state: FollowState
    event: GestureEvent
    command: MockCommand | None

    @property
    def changed(self) -> bool:
        return self.old_state != self.new_state


class FollowStateMachine:
    """Two-state MVP: either the cart is following or it is not."""

    def __init__(self) -> None:
        self._state = FollowState.IDLE

    @property
    def state(self) -> FollowState:
        return self._state

    def handle_event(self, event: GestureEvent) -> TransitionResult:
        old_state = self._state
        command: MockCommand | None = None

        if self._state == FollowState.IDLE and event == GestureEvent.START_GESTURE:
            self._state = FollowState.FOLLOWING
            command = MockCommand.START_FOLLOW
        elif self._state == FollowState.FOLLOWING and event == GestureEvent.STOP_GESTURE:
            self._state = FollowState.IDLE
            command = MockCommand.STOP_FOLLOW

        return TransitionResult(
            old_state=old_state,
            new_state=self._state,
            event=event,
            command=command,
        )
