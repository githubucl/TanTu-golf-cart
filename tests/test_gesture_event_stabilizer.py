import unittest

from golf_cart_vision.gesture_detector.detection_types import GestureEvent
from golf_cart_vision.gesture_detector.event_stabilizer import GestureEventStabilizer


class GestureEventStabilizerTest(unittest.TestCase):
    def test_single_frame_gesture_is_not_stable(self) -> None:
        stabilizer = GestureEventStabilizer(confirmation_frames=2)

        result = stabilizer.update(GestureEvent.START_GESTURE)

        self.assertEqual(result.raw_event, GestureEvent.START_GESTURE)
        self.assertEqual(result.stable_event, GestureEvent.NO_GESTURE)
        self.assertEqual(result.candidate_count, 1)

    def test_two_matching_frames_make_gesture_stable(self) -> None:
        stabilizer = GestureEventStabilizer(confirmation_frames=2)

        stabilizer.update(GestureEvent.START_GESTURE)
        result = stabilizer.update(GestureEvent.START_GESTURE)

        self.assertEqual(result.stable_event, GestureEvent.START_GESTURE)
        self.assertEqual(result.candidate_count, 2)

    def test_different_gesture_resets_candidate(self) -> None:
        stabilizer = GestureEventStabilizer(confirmation_frames=2)

        stabilizer.update(GestureEvent.START_GESTURE)
        result = stabilizer.update(GestureEvent.STOP_GESTURE)

        self.assertEqual(result.stable_event, GestureEvent.NO_GESTURE)
        self.assertEqual(result.candidate_event, GestureEvent.STOP_GESTURE)
        self.assertEqual(result.candidate_count, 1)

    def test_one_missing_frame_is_tolerated(self) -> None:
        stabilizer = GestureEventStabilizer(
            confirmation_frames=2,
            missing_tolerance_frames=1,
        )

        stabilizer.update(GestureEvent.START_GESTURE)
        stabilizer.update(GestureEvent.NO_GESTURE)
        result = stabilizer.update(GestureEvent.START_GESTURE)

        self.assertEqual(result.stable_event, GestureEvent.START_GESTURE)

    def test_missing_frame_does_not_emit_stable_event(self) -> None:
        stabilizer = GestureEventStabilizer(
            confirmation_frames=2,
            missing_tolerance_frames=1,
        )

        stabilizer.update(GestureEvent.START_GESTURE)
        stabilizer.update(GestureEvent.START_GESTURE)
        result = stabilizer.update(GestureEvent.NO_GESTURE)

        self.assertEqual(result.stable_event, GestureEvent.NO_GESTURE)
        self.assertEqual(result.candidate_count, 2)

    def test_too_many_missing_frames_reset_candidate(self) -> None:
        stabilizer = GestureEventStabilizer(
            confirmation_frames=2,
            missing_tolerance_frames=0,
        )

        stabilizer.update(GestureEvent.START_GESTURE)
        stabilizer.update(GestureEvent.NO_GESTURE)
        result = stabilizer.update(GestureEvent.START_GESTURE)

        self.assertEqual(result.stable_event, GestureEvent.NO_GESTURE)
        self.assertEqual(result.candidate_count, 1)

    def test_invalid_confirmation_frames_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            GestureEventStabilizer(confirmation_frames=0)


if __name__ == "__main__":
    unittest.main()
