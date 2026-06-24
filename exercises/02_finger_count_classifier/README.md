# Exercise 02: Palm Spread Classifier

## 练习目标

理解 MediaPipe 手部关键点的基本思路：不是直接识别“手势名字”，而是先找到手上的 21 个点，再用点的位置关系判断手指是分开还是合并。

## 需要改哪个文件

修改本目录下的 `exercise.py`。

## 预期输出

运行：

```bash
python3 exercises/02_finger_count_classifier/exercise.py
```

你应该看到：

```text
spread palm ratio: 0.67
joined palm ratio: 0.13
```

## 提示

- 指尖之间距离越大，说明手指越分开。
- 直接看距离不稳定，因为手离摄像头远近会变。
- 所以用 `指尖平均间距 / 手掌宽度` 做比例。
- 这里不判断手心或手背，只判断关键点之间的距离。

## 答案检查方式

手指分开的模拟数据应该比手指合并的模拟数据比例更大。
