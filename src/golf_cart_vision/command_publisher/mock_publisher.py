from __future__ import annotations

from golf_cart_vision.state_machine.follow_state_machine import MockCommand


class MockCommandPublisher:
    """Prints commands now; can later be replaced by a chassis publisher."""

    def __init__(self) -> None:
        self.published_commands: list[MockCommand] = []

    def publish(self, command: MockCommand | None) -> None:
        if command is None:
            return
        self.published_commands.append(command)
        print(f"[MOCK_COMMAND] {command.value}")
