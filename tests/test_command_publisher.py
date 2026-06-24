import unittest

from golf_cart_vision.command_publisher.mock_publisher import MockCommandPublisher
from golf_cart_vision.state_machine.follow_state_machine import MockCommand


class MockCommandPublisherTest(unittest.TestCase):
    def test_publish_records_command(self) -> None:
        publisher = MockCommandPublisher()

        publisher.publish(MockCommand.START_FOLLOW)

        self.assertEqual(publisher.published_commands, [MockCommand.START_FOLLOW])

    def test_publish_ignores_none(self) -> None:
        publisher = MockCommandPublisher()

        publisher.publish(None)

        self.assertEqual(publisher.published_commands, [])


if __name__ == "__main__":
    unittest.main()
