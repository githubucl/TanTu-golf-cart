from __future__ import annotations

from golf_cart_vision.gesture_detector.detection_types import DetectorOutput
from golf_cart_vision.gesture_detector.event_stabilizer import StabilizerOutput
from golf_cart_vision.state_machine.follow_state_machine import MockCommand


class ConsoleVisualizer:
    """Console-only visualizer for the first learning stage."""

    def render(
        self,
        frame_index: int,
        detector_output: DetectorOutput,
        stabilizer_output: StabilizerOutput,
        state: str,
        command: MockCommand | None,
    ) -> None:
        raw_gesture = detector_output.event.value
        stable_gesture = stabilizer_output.stable_event.value
        command_text = command.value if command is not None else "-"
        detection_count = len(detector_output.detections)
        print(
            f"[FRAME {frame_index:03d}] "
            f"raw={raw_gesture} stable={stable_gesture} "
            f"confirm={stabilizer_output.candidate_count}/{stabilizer_output.confirmation_frames} "
            f"detections={detection_count} "
            f"state={state} command={command_text}"
        )
