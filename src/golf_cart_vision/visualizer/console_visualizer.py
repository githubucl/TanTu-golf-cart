from __future__ import annotations

from golf_cart_vision.gesture_detector.detection_types import DetectorOutput
from golf_cart_vision.state_machine.follow_state_machine import MockCommand


class ConsoleVisualizer:
    """Console-only visualizer for the first learning stage."""

    def render(
        self,
        frame_index: int,
        detector_output: DetectorOutput,
        state: str,
        command: MockCommand | None,
    ) -> None:
        gesture = detector_output.event.value
        command_text = command.value if command is not None else "-"
        detection_count = len(detector_output.detections)
        print(
            f"[FRAME {frame_index:03d}] "
            f"gesture={gesture} detections={detection_count} "
            f"state={state} command={command_text}"
        )
