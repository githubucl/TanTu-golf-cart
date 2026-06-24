import unittest

from golf_cart_vision.gesture_detector.detection_types import GestureEvent
from golf_cart_vision.state_machine.follow_state_machine import (
    FollowState,
    FollowStateMachine,
    MockCommand,
)


class FollowStateMachineTest(unittest.TestCase):
    def test_initial_state_is_idle(self) -> None:
        machine = FollowStateMachine()

        self.assertEqual(machine.state, FollowState.IDLE)

    def test_start_gesture_enters_following(self) -> None:
        machine = FollowStateMachine()

        result = machine.handle_event(GestureEvent.START_GESTURE)

        self.assertEqual(result.old_state, FollowState.IDLE)
        self.assertEqual(result.new_state, FollowState.FOLLOWING)
        self.assertEqual(result.command, MockCommand.START_FOLLOW)

    def test_stop_gesture_returns_to_idle(self) -> None:
        machine = FollowStateMachine()
        machine.handle_event(GestureEvent.START_GESTURE)

        result = machine.handle_event(GestureEvent.STOP_GESTURE)

        self.assertEqual(result.old_state, FollowState.FOLLOWING)
        self.assertEqual(result.new_state, FollowState.IDLE)
        self.assertEqual(result.command, MockCommand.STOP_FOLLOW)

    def test_stop_gesture_does_nothing_when_already_idle(self) -> None:
        machine = FollowStateMachine()

        result = machine.handle_event(GestureEvent.STOP_GESTURE)

        self.assertEqual(result.old_state, FollowState.IDLE)
        self.assertEqual(result.new_state, FollowState.IDLE)
        self.assertIsNone(result.command)

    def test_no_gesture_does_not_change_state(self) -> None:
        machine = FollowStateMachine()
        machine.handle_event(GestureEvent.START_GESTURE)

        result = machine.handle_event(GestureEvent.NO_GESTURE)

        self.assertEqual(result.old_state, FollowState.FOLLOWING)
        self.assertEqual(result.new_state, FollowState.FOLLOWING)
        self.assertIsNone(result.command)


if __name__ == "__main__":
    unittest.main()
