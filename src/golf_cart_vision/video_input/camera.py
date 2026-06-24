from __future__ import annotations

from collections.abc import Iterator


class OpenCVCamera:
    """Small OpenCV camera wrapper for the later real-camera demo."""

    def __init__(self, camera_index: int = 0) -> None:
        self.camera_index = camera_index
        self._capture = None

    def __enter__(self) -> "OpenCVCamera":
        import cv2

        self._capture = cv2.VideoCapture(self.camera_index)
        if not self._capture.isOpened():
            raise RuntimeError(f"Could not open camera index {self.camera_index}")
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        del exc_type, exc, traceback
        if self._capture is not None:
            self._capture.release()

    def frames(self) -> Iterator[object]:
        if self._capture is None:
            raise RuntimeError("Camera must be opened with a context manager")

        while True:
            ok, frame = self._capture.read()
            if not ok:
                break
            yield frame
