from __future__ import annotations

import argparse
import time
from typing import Protocol
from pathlib import Path

from golf_cart_vision.command_publisher.mock_publisher import MockCommandPublisher
from golf_cart_vision.config.settings import load_config
from golf_cart_vision.gesture_detector.detection_types import DetectorOutput
from golf_cart_vision.gesture_detector.mediapipe_detector import MediaPipeGestureDetector
from golf_cart_vision.gesture_detector.mock_detector import MockGestureDetector
from golf_cart_vision.state_machine.follow_state_machine import FollowStateMachine
from golf_cart_vision.video_input.camera import OpenCVCamera
from golf_cart_vision.visualizer.console_visualizer import ConsoleVisualizer
from golf_cart_vision.visualizer.opencv_visualizer import draw_detections


class GestureDetector(Protocol):
    def detect(self, frame: object | None = None) -> DetectorOutput:
        ...


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Golf cart vision-following MVP demo.")
    parser.add_argument(
        "--config",
        default="configs/default.yaml",
        help="Path to YAML config file.",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=None,
        help="Override max frames from the config. In camera mode, 0 means run until q.",
    )
    parser.add_argument(
        "--camera",
        action="store_true",
        help="Open the camera and draw detection results on the video window.",
    )
    parser.add_argument(
        "--detector",
        choices=("mock", "mediapipe"),
        default=None,
        help="Override detector mode. Use mediapipe for real hand-gesture detection.",
    )
    parser.add_argument(
        "--window-name",
        default="Golf Cart Vision MVP",
        help="Camera demo window name.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(Path(args.config))
    detector_mode = args.detector or config.detector_mode

    if detector_mode == "mediapipe" and not args.camera:
        raise SystemExit("The mediapipe detector needs camera frames. Run with --camera.")

    try:
        detector = create_detector(detector_mode=detector_mode, config=config)
    except RuntimeError as error:
        raise SystemExit(str(error)) from error

    state_machine = FollowStateMachine()
    publisher = MockCommandPublisher()

    if args.camera:
        max_frames = args.frames
        try:
            run_camera_demo(
                detector=detector,
                state_machine=state_machine,
                publisher=publisher,
                camera_index=config.camera_index,
                max_frames=max_frames,
                window_name=args.window_name,
            )
            return
        finally:
            close = getattr(detector, "close", None)
            if callable(close):
                close()

    max_frames = args.frames if args.frames is not None else config.max_frames
    run_console_demo(
        detector=detector,
        state_machine=state_machine,
        publisher=publisher,
        max_frames=max_frames,
        frame_delay_seconds=config.frame_delay_seconds,
    )


def create_detector(detector_mode: str, config) -> GestureDetector:
    if detector_mode == "mock":
        return MockGestureDetector(config.mock_gesture_sequence)

    if detector_mode == "mediapipe":
        return MediaPipeGestureDetector(
            model_path=config.mediapipe_model_path,
            min_detection_confidence=config.mediapipe_min_detection_confidence,
            min_tracking_confidence=config.mediapipe_min_tracking_confidence,
        )

    raise ValueError(f"Unsupported detector_mode: {detector_mode}")


def run_console_demo(
    detector: GestureDetector,
    state_machine: FollowStateMachine,
    publisher: MockCommandPublisher,
    max_frames: int,
    frame_delay_seconds: float,
) -> None:
    visualizer = ConsoleVisualizer()

    for frame_index in range(max_frames):
        detector_output = detector.detect(frame=None)
        transition = state_machine.handle_event(detector_output.event)
        publisher.publish(transition.command)
        visualizer.render(
            frame_index=frame_index,
            detector_output=detector_output,
            state=transition.new_state.value,
            command=transition.command,
        )
        time.sleep(frame_delay_seconds)


def run_camera_demo(
    detector: GestureDetector,
    state_machine: FollowStateMachine,
    publisher: MockCommandPublisher,
    camera_index: int,
    max_frames: int | None,
    window_name: str,
) -> None:
    try:
        import cv2
    except ImportError as error:
        raise RuntimeError(
            "Camera mode requires OpenCV. Install it with: python -m pip install opencv-python"
        ) from error

    frame_limit = None if max_frames in (None, 0) else max_frames

    with OpenCVCamera(camera_index=camera_index) as camera:
        for frame_index, frame in enumerate(camera.frames()):
            detector_output = detector.detect(frame=frame)
            transition = state_machine.handle_event(detector_output.event)
            publisher.publish(transition.command)

            output_frame = draw_detections(
                frame=frame,
                detections=detector_output.detections,
                state=transition.new_state.value,
                command=transition.command,
            )
            cv2.imshow(window_name, output_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            if frame_limit is not None and frame_index + 1 >= frame_limit:
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
