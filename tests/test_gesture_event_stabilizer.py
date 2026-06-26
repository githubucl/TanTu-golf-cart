import unittest

from golf_cart_vision.gesture_detector.detection_types import GestureEvent
from golf_cart_vision.gesture_detector.event_stabilizer import GestureEventStabilizer


class GestureEventStabilizerTest(unittest.TestCase):
    def test_gesture_is_not_stable_before_required_duration(self) -> None:
        stabilizer = GestureEventStabilizer(confirmation_seconds=0.2)

        result = stabilizer.update(GestureEvent.START_GESTURE, now_seconds=10.0)

        self.assertEqual(result.raw_event, GestureEvent.START_GESTURE)
        self.assertEqual(result.stable_event, GestureEvent.NO_GESTURE)
        self.assertEqual(result.candidate_count, 1)
        self.assertEqual(result.candidate_elapsed_seconds, 0.0)

    def test_matching_gesture_becomes_stable_after_duration(self) -> None:
        stabilizer = GestureEventStabilizer(confirmation_seconds=0.2)

        stabilizer.update(GestureEvent.START_GESTURE, now_seconds=10.0)
        result = stabilizer.update(GestureEvent.START_GESTURE, now_seconds=10.2)

        self.assertEqual(result.stable_event, GestureEvent.START_GESTURE)
        self.assertEqual(result.candidate_count, 2)
        self.assertAlmostEqual(result.candidate_elapsed_seconds, 0.2)

    def test_different_gesture_resets_candidate_timer(self) -> None:
        stabilizer = GestureEventStabilizer(confirmation_seconds=0.2)

        stabilizer.update(GestureEvent.START_GESTURE, now_seconds=10.0)
        result = stabilizer.update(GestureEvent.STOP_GESTURE, now_seconds=10.1)

        self.assertEqual(result.stable_event, GestureEvent.NO_GESTURE)
        self.assertEqual(result.candidate_event, GestureEvent.STOP_GESTURE)
        self.assertEqual(result.candidate_count, 1)
        self.assertEqual(result.candidate_elapsed_seconds, 0.0)

    def test_short_missing_gap_is_tolerated(self) -> None:
        stabilizer = GestureEventStabilizer(
            confirmation_seconds=0.2,
            missing_tolerance_seconds=0.1,
        )

        stabilizer.update(GestureEvent.START_GESTURE, now_seconds=10.0)
        stabilizer.update(GestureEvent.NO_GESTURE, now_seconds=10.05)
        result = stabilizer.update(GestureEvent.START_GESTURE, now_seconds=10.2)

        self.assertEqual(result.stable_event, GestureEvent.START_GESTURE)
        self.assertEqual(result.candidate_count, 2)

    def test_missing_frame_does_not_emit_stable_event(self) -> None:
        stabilizer = GestureEventStabilizer(
            confirmation_seconds=0.2,
            missing_tolerance_seconds=0.1,
        )

        stabilizer.update(GestureEvent.START_GESTURE, now_seconds=10.0)
        stabilizer.update(GestureEvent.START_GESTURE, now_seconds=10.2)
        result = stabilizer.update(GestureEvent.NO_GESTURE, now_seconds=10.25)

        self.assertEqual(result.stable_event, GestureEvent.NO_GESTURE)
        self.assertEqual(result.candidate_count, 2)

    def test_long_missing_gap_resets_candidate(self) -> None:
        stabilizer = GestureEventStabilizer(
            confirmation_seconds=0.2,
            missing_tolerance_seconds=0.1,
        )

        stabilizer.update(GestureEvent.START_GESTURE, now_seconds=10.0)
        stabilizer.update(GestureEvent.NO_GESTURE, now_seconds=10.2)
        result = stabilizer.update(GestureEvent.START_GESTURE, now_seconds=10.3)

        self.assertEqual(result.stable_event, GestureEvent.NO_GESTURE)
        self.assertEqual(result.candidate_count, 1)
        self.assertEqual(result.candidate_elapsed_seconds, 0.0)

    def test_invalid_confirmation_seconds_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            GestureEventStabilizer(confirmation_seconds=0)

    def test_invalid_missing_tolerance_seconds_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            GestureEventStabilizer(missing_tolerance_seconds=-0.1)


if __name__ == "__main__":
    unittest.main()
