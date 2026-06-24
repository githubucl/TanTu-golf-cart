from __future__ import annotations

from golf_cart_vision.gesture_detector.detection_types import GestureDetection
from golf_cart_vision.state_machine.follow_state_machine import MockCommand


def draw_detections(
    frame: object,
    detections: list[GestureDetection],
    state: str,
    command: MockCommand | None = None,
) -> object:
    """Draws mock detections and current follow status on an OpenCV frame."""
    import cv2

    for detection in detections:
        if detection.bbox is None:
            continue
        box = detection.bbox
        label = f"{detection.class_name} {detection.confidence:.2f}"
        cv2.rectangle(frame, (box.x1, box.y1), (box.x2, box.y2), (0, 255, 0), 2)
        cv2.putText(
            frame,
            label,
            (box.x1, max(20, box.y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )

    cv2.putText(
        frame,
        f"STATE: {state}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
    )

    command_text = command.value if command is not None else "-"
    cv2.putText(
        frame,
        f"COMMAND: {command_text}",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
    )
    return frame
