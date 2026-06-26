from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AppConfig:
    detector_mode: str = "mock"
    camera_index: int = 0
    max_frames: int = 8
    frame_delay_seconds: float = 0.2
    mediapipe_model_path: str = "models/hand_landmarker.task"
    mediapipe_min_detection_confidence: float = 0.6
    mediapipe_min_tracking_confidence: float = 0.5
    palm_spread_threshold: float = 0.55
    gesture_confirmation_seconds: float = 0.2
    gesture_missing_tolerance_seconds: float = 0.1
    mock_gesture_sequence: list[str] = field(
        default_factory=lambda: ["none", "start", "start", "none", "none", "stop", "stop", "none"]
    )


def load_config(path: str | Path = "configs/default.yaml") -> AppConfig:
    config_path = Path(path)
    if not config_path.exists():
        return AppConfig()

    raw_data = _load_simple_yaml(config_path)
    if not isinstance(raw_data, dict):
        raise ValueError(f"Config file must contain a YAML mapping: {config_path}")

    data: dict[str, Any] = {**AppConfig().__dict__, **raw_data}
    return AppConfig(
        detector_mode=str(data["detector_mode"]),
        camera_index=int(data["camera_index"]),
        max_frames=int(data["max_frames"]),
        frame_delay_seconds=float(data["frame_delay_seconds"]),
        mediapipe_model_path=str(data["mediapipe_model_path"]),
        mediapipe_min_detection_confidence=float(data["mediapipe_min_detection_confidence"]),
        mediapipe_min_tracking_confidence=float(data["mediapipe_min_tracking_confidence"]),
        palm_spread_threshold=float(data["palm_spread_threshold"]),
        gesture_confirmation_seconds=float(data["gesture_confirmation_seconds"]),
        gesture_missing_tolerance_seconds=float(data["gesture_missing_tolerance_seconds"]),
        mock_gesture_sequence=list(data["mock_gesture_sequence"]),
    )


def _load_simple_yaml(config_path: Path) -> dict[str, Any]:
    """Reads the small config shape used in Stage 1 without external packages."""
    data: dict[str, Any] = {}
    current_list_key: str | None = None

    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        stripped = line.strip()
        if stripped.startswith("- "):
            if current_list_key is None:
                raise ValueError(f"List item without a list key in {config_path}: {raw_line}")
            data.setdefault(current_list_key, []).append(stripped[2:].strip())
            continue

        current_list_key = None
        if ":" not in stripped:
            raise ValueError(f"Unsupported config line in {config_path}: {raw_line}")

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == "":
            data[key] = []
            current_list_key = key
        else:
            data[key] = _parse_scalar(value)

    return data


def _parse_scalar(value: str) -> Any:
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value.strip('"').strip("'")
