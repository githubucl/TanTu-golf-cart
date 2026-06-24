from math import hypot


finger_tips = [8, 12, 16, 20]
finger_tip_pairs = [
    (8, 12),
    (12, 16),
    (16, 20),
]


def distance(first: dict[str, float], second: dict[str, float]) -> float:
    return hypot(first["x"] - second["x"], first["y"] - second["y"])


def palm_spread_ratio(landmarks: list[dict[str, float]]) -> float:
    total_tip_gap = 0.0
    for first_tip_index, second_tip_index in finger_tip_pairs:
        first_tip = landmarks[first_tip_index]
        second_tip = landmarks[second_tip_index]
        # TODO: 把相邻两个指尖的距离加到 total_tip_gap。

    average_tip_gap = total_tip_gap / len(finger_tip_pairs)
    palm_width = distance(landmarks[5], landmarks[17])
    return average_tip_gap / palm_width


def make_landmarks(tip_xs: list[float]) -> list[dict[str, float]]:
    landmarks = [{"x": 0.5, "y": 0.5} for _ in range(21)]
    landmarks[5] = {"x": 0.35, "y": 0.55}
    landmarks[17] = {"x": 0.65, "y": 0.55}
    for tip_index, tip_x in zip(finger_tips, tip_xs):
        landmarks[tip_index] = {"x": tip_x, "y": 0.25}
    return landmarks


spread_palm = make_landmarks([0.2, 0.4, 0.6, 0.8])
joined_palm = make_landmarks([0.44, 0.48, 0.52, 0.56])

print("spread palm ratio:", round(palm_spread_ratio(spread_palm), 2))
print("joined palm ratio:", round(palm_spread_ratio(joined_palm), 2))
