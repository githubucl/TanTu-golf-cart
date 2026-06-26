from __future__ import annotations

from pathlib import Path

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
        model_path: str = "models/hand_landmarker.task",
        min_detection_confidence: float = 0.6,
        min_tracking_confidence: float = 0.5,
        palm_spread_threshold: float = 0.55,
    ) -> None:
        try:
            import mediapipe as mp
        except ImportError as error:
            raise RuntimeError(
                "MediaPipe detector requires mediapipe. Install it with: "
                "python -m pip install mediapipe"
            ) from error

        model_file = Path(model_path)
        if not model_file.exists():
            raise RuntimeError(
                f"MediaPipe hand model not found: {model_file}. "
                "Download it with: "
                "curl -L https://storage.googleapis.com/mediapipe-models/"
                "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task "
                "-o models/hand_landmarker.task"
            )

        base_options = mp.tasks.BaseOptions(model_asset_path=str(model_file))
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)
        self._classifier = SimpleHandGestureClassifier(spread_threshold=palm_spread_threshold)
        self._timestamp_ms = 0

    def close(self) -> None:
        self._landmarker.close()

    def detect(self, frame: object | None = None) -> DetectorOutput:
        if frame is None:
            raise ValueError("MediaPipeGestureDetector requires a camera frame")

        import cv2
        import mediapipe as mp

        height, width = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        self._timestamp_ms += 33
        results = self._landmarker.detect_for_video(mp_image, self._timestamp_ms)

        if not results.hand_landmarks:
            return DetectorOutput(event=GestureEvent.NO_GESTURE, detections=[])

        hand_landmarks = results.hand_landmarks[0]
        landmarks = [
            NormalizedPoint(x=point.x, y=point.y, z=point.z)
            for point in hand_landmarks
        ]
        classification = self._classifier.classify(landmarks)
        bbox = _landmarks_to_bbox(landmarks, width=width, height=height)

        if classification.gesture == HandGesture.OPEN_PALM_SPREAD:
            detection = GestureDetection(
                class_id=1,
                class_name="open_palm_spread_start",
                confidence=classification.confidence,
                bbox=bbox,
                details=_classification_details(
                    classification=classification,
                    spread_threshold=self._classifier.spread_threshold,
                ),
            )
            return DetectorOutput(event=GestureEvent.START_GESTURE, detections=[detection])

        if classification.gesture == HandGesture.OPEN_PALM_JOINED:
            detection = GestureDetection(
                class_id=2,
                class_name="open_palm_joined_stop",
                confidence=classification.confidence,
                bbox=bbox,
                details=_classification_details(
                    classification=classification,
                    spread_threshold=self._classifier.spread_threshold,
                ),
            )
            return DetectorOutput(event=GestureEvent.STOP_GESTURE, detections=[detection])

        detection = GestureDetection(
            class_id=0,
            class_name="unknown_hand",
            confidence=classification.confidence,
            bbox=bbox,
            details=_classification_details(
                classification=classification,
                spread_threshold=self._classifier.spread_threshold,
            ),
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


def _classification_details(
    classification,
    spread_threshold: float,
) -> dict[str, float | int | str]:
    return {
        "gesture": classification.gesture.value,
        "extended_fingers": classification.extended_finger_count,
        "spread_ratio": round(classification.spread_ratio, 3),
        "spread_threshold": round(spread_threshold, 3),
    }
