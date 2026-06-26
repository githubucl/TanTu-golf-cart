import unittest

from golf_cart_vision.gesture_detector.hand_gesture_classifier import (
    HandGesture,
    NormalizedPoint,
    SimpleHandGestureClassifier,
)


def make_landmarks_with_finger_tips(tip_above_pip: bool) -> list[NormalizedPoint]:
    landmarks = [NormalizedPoint(x=0.5, y=0.5) for _ in range(21)]
    for tip_index, pip_index in ((8, 6), (12, 10), (16, 14), (20, 18)):
        landmarks[pip_index] = NormalizedPoint(x=0.5, y=0.5)
        tip_y = 0.3 if tip_above_pip else 0.7
        landmarks[tip_index] = NormalizedPoint(x=0.5, y=tip_y)
    return landmarks


def make_open_palm_tip_spacing(tip_xs: list[float]) -> list[NormalizedPoint]:
    landmarks = [NormalizedPoint(x=0.5, y=0.5) for _ in range(21)]
    landmarks[5] = NormalizedPoint(x=0.35, y=0.55)
    landmarks[17] = NormalizedPoint(x=0.65, y=0.55)
    for tip_x, (tip_index, pip_index) in zip(tip_xs, ((8, 6), (12, 10), (16, 14), (20, 18))):
        landmarks[pip_index] = NormalizedPoint(x=tip_x, y=0.45)
        landmarks[tip_index] = NormalizedPoint(x=tip_x, y=0.25)
    return landmarks


class SimpleHandGestureClassifierTest(unittest.TestCase):
    def test_spread_open_palm_is_start_gesture(self) -> None:
        classifier = SimpleHandGestureClassifier()

        result = classifier.classify(make_open_palm_tip_spacing([0.2, 0.4, 0.6, 0.8]))

        self.assertEqual(result.gesture, HandGesture.OPEN_PALM_SPREAD)
        self.assertEqual(result.extended_finger_count, 4)

    def test_joined_open_palm_is_stop_gesture(self) -> None:
        classifier = SimpleHandGestureClassifier()

        result = classifier.classify(make_open_palm_tip_spacing([0.44, 0.48, 0.52, 0.56]))

        self.assertEqual(result.gesture, HandGesture.OPEN_PALM_JOINED)
        self.assertEqual(result.extended_finger_count, 4)

    def test_lower_threshold_makes_spread_easier_to_trigger(self) -> None:
        classifier = SimpleHandGestureClassifier(spread_threshold=0.3)

        result = classifier.classify(make_open_palm_tip_spacing([0.35, 0.47, 0.53, 0.65]))

        self.assertEqual(result.gesture, HandGesture.OPEN_PALM_SPREAD)

    def test_higher_threshold_makes_joined_easier_to_trigger(self) -> None:
        classifier = SimpleHandGestureClassifier(spread_threshold=0.4)

        result = classifier.classify(make_open_palm_tip_spacing([0.35, 0.47, 0.53, 0.65]))

        self.assertEqual(result.gesture, HandGesture.OPEN_PALM_JOINED)

    def test_mirrored_spread_palm_still_classifies_as_spread(self) -> None:
        classifier = SimpleHandGestureClassifier()
        mirrored_landmarks = [
            NormalizedPoint(x=1.0 - point.x, y=point.y, z=point.z)
            for point in make_open_palm_tip_spacing([0.2, 0.4, 0.6, 0.8])
        ]

        result = classifier.classify(mirrored_landmarks)

        self.assertEqual(result.gesture, HandGesture.OPEN_PALM_SPREAD)

    def test_non_open_palm_is_unknown(self) -> None:
        classifier = SimpleHandGestureClassifier()

        result = classifier.classify(make_landmarks_with_finger_tips(tip_above_pip=False))

        self.assertEqual(result.gesture, HandGesture.UNKNOWN)
        self.assertEqual(result.extended_finger_count, 0)

    def test_wrong_landmark_count_is_rejected(self) -> None:
        classifier = SimpleHandGestureClassifier()

        with self.assertRaises(ValueError):
            classifier.classify([NormalizedPoint(x=0.5, y=0.5)])


if __name__ == "__main__":
    unittest.main()
