from __future__ import annotations

from golf_cart_vision.gesture_detector.detection_types import GestureDetection
from golf_cart_vision.gesture_detector.event_stabilizer import StabilizerOutput
from golf_cart_vision.state_machine.follow_state_machine import MockCommand


def draw_detections(
    frame: object,
    detections: list[GestureDetection],
    state: str,
    stabilizer_output: StabilizerOutput | None = None,
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

    gesture_text = _gesture_debug_text(detections)
    cv2.putText(
        frame,
        gesture_text,
        (20, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
    )

    filter_text = _stabilizer_debug_text(stabilizer_output)
    cv2.putText(
        frame,
        filter_text,
        (20, 145),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
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


def _gesture_debug_text(detections: list[GestureDetection]) -> str:
    if not detections:
        return "GESTURE: no_hand"

    detection = detections[0]
    ratio = detection.details.get("spread_ratio")
    threshold = detection.details.get("spread_threshold")
    fingers = detection.details.get("extended_fingers")

    if ratio is None or threshold is None or fingers is None:
        return f"GESTURE: {detection.class_name}"

    return (
        f"GESTURE: {detection.class_name} "
        f"ratio={ratio} threshold={threshold} fingers={fingers}"
    )


def _stabilizer_debug_text(stabilizer_output: StabilizerOutput | None) -> str:
    if stabilizer_output is None:
        return "FILTER: off"

    return (
        f"FILTER: raw={stabilizer_output.raw_event.value} "
        f"stable={stabilizer_output.stable_event.value} "
        f"confirm={stabilizer_output.candidate_elapsed_seconds:.2f}/"
        f"{stabilizer_output.confirmation_seconds:.2f}s "
        f"frames={stabilizer_output.candidate_count}"
    )
