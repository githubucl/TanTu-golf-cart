from __future__ import annotations

from golf_cart_vision.gesture_detector.detection_types import (
    BoundingBox,
    DetectorOutput,
    GestureDetection,
    GestureEvent,
)
from golf_cart_vision.gesture_detector.hand_gesture_classifier import (
    HandGesture,
    NormalizedPoint,
    SimpleHandGestureClassifier,
)


class MediaPipeGestureDetector:
    """Detects simple start/stop gestures from live camera frames."""

    def __init__(
        self,
        min_detection_confidence: float = 0.6,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        try:
            import mediapipe as mp
        except ImportError as error:
            raise RuntimeError(
                "MediaPipe detector requires mediapipe. Install it with: "
                "python -m pip install mediapipe"
            ) from error

        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._classifier = SimpleHandGestureClassifier()

    def close(self) -> None:
        self._hands.close()

    def detect(self, frame: object | None = None) -> DetectorOutput:
        if frame is None:
            raise ValueError("MediaPipeGestureDetector requires a camera frame")

        import cv2

        height, width = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb_frame)

        if not results.multi_hand_landmarks:
            return DetectorOutput(event=GestureEvent.NO_GESTURE, detections=[])

        hand_landmarks = results.multi_hand_landmarks[0]
        landmarks = [
            NormalizedPoint(x=point.x, y=point.y, z=point.z)
            for point in hand_landmarks.landmark
        ]
        classification = self._classifier.classify(landmarks)
        bbox = _landmarks_to_bbox(landmarks, width=width, height=height)

        if classification.gesture == HandGesture.OPEN_PALM_SPREAD:
            detection = GestureDetection(
                class_id=1,
                class_name="open_palm_spread_start",
                confidence=classification.confidence,
                bbox=bbox,
            )
            return DetectorOutput(event=GestureEvent.START_GESTURE, detections=[detection])

        if classification.gesture == HandGesture.OPEN_PALM_JOINED:
            detection = GestureDetection(
                class_id=2,
                class_name="open_palm_joined_stop",
                confidence=classification.confidence,
                bbox=bbox,
            )
            return DetectorOutput(event=GestureEvent.STOP_GESTURE, detections=[detection])

        detection = GestureDetection(
            class_id=0,
            class_name="unknown_hand",
            confidence=classification.confidence,
            bbox=bbox,
        )
        return DetectorOutput(event=GestureEvent.NO_GESTURE, detections=[detection])


def _landmarks_to_bbox(
    landmarks: list[NormalizedPoint],
    width: int,
    height: int,
    padding_px: int = 12,
) -> BoundingBox:
    xs = [point.x * width for point in landmarks]
    ys = [point.y * height for point in landmarks]

    x1 = max(0, int(min(xs)) - padding_px)
    y1 = max(0, int(min(ys)) - padding_px)
    x2 = min(width - 1, int(max(xs)) + padding_px)
    y2 = min(height - 1, int(max(ys)) + padding_px)
    return BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2)
