state = "IDLE"


def handle_event(event: str) -> str:
    global state

    if state == "IDLE" and event == "start":
        state = "FOLLOWING"
    elif state == "FOLLOWING" and event == "stop":
        state = "IDLE"

    return state


events = ["start", "stop", "stop", "start"]

for event in events:
    next_state = handle_event(event)
    print(f"event={event} -> state={next_state}")
