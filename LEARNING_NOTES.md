# Learning Notes

## 第一阶段第 1 小步：先跑通软件闭环

这一小步故意不用 YOLO，也不读取摄像头。

目的不是展示识别效果，而是先学懂视觉跟随项目的主流程：

```text
手势事件 -> 状态机 -> mock 控制指令 -> 输出
```

## 为什么先用 mock detector

`MockGestureDetector` 是假的检测器。它不会看图片，只会按配置里的顺序吐出模拟手势。

这样做的原因：

- 不会被模型文件、训练数据、摄像头画面质量卡住；
- 可以先验证状态机和控制命令是否正确；
- 后面接 YOLO 时，只要保证 YOLO 输出同样的事件结构，主流程不用大改。

更简单的替代方案：直接在 `main.py` 里写字符串列表。

更复杂的替代方案：一开始就接 YOLO 或 MediaPipe。

真实球车限制：mock detector 不能代表真实识别效果，它只适合验证软件结构。

## 为什么第一阶段只有两个状态

当前状态只有：

- `IDLE`：未跟随；
- `FOLLOWING`：正在跟随。

因为你确认“停止”和“暂停”使用同一个手势，而且第一阶段没有真实底盘、目标锁定和恢复跟随逻辑。

所以第一版中：

```text
IDLE + START_GESTURE -> FOLLOWING + START_FOLLOW
FOLLOWING + STOP_GESTURE -> IDLE + STOP_FOLLOW
```

`PAUSED` 暂时不实现。等后面有“仍然锁定用户，但临时不动”的需求时，再加入。

真实球车限制：真实车不能只靠单帧手势立刻启动或停止，必须加入连续帧确认、急停、安全冗余和人工接管。

## 每个模块在干什么

`config/settings.py`

读取 `configs/default.yaml`，集中管理配置。这样以后改模型路径、摄像头编号、阈值时，不需要到处改代码。

`gesture_detector/mock_detector.py`

模拟手势检测结果。后面会被 YOLO 检测器替换。

`gesture_detector/detection_types.py`

定义检测结果的数据结构，包括手势事件、检测框、类别名和置信度。

`state_machine/follow_state_machine.py`

管理状态切换。它不关心图像，只关心事件。

`command_publisher/mock_publisher.py`

输出 mock command。现在是 `print()`，未来可以换成串口、CAN、ROS、HTTP 或 MQTT。

`visualizer/console_visualizer.py`

把当前帧、识别事件、状态和命令打印出来，方便调试。

`video_input/camera.py`

预留 OpenCV 摄像头输入接口。下一阶段会真正接入主流程。

## 本阶段练习

练习文件在：

```text
exercises/01_state_machine_basics/
```

练习目标：自己补全一个最小状态机，理解 `IDLE` 和 `FOLLOWING` 的切换。

## 第二阶段第 1 小步：接入摄像头画面

现在主程序支持：

```bash
PYTHONPATH=src python3 -m golf_cart_vision.main --camera
```

这一阶段仍然用 `MockGestureDetector`，所以它并不会真的识别你的手势。它只是把固定的 mock 检测结果画到真实摄像头画面上。

这样设计的目的：

- 先验证摄像头能不能打开；
- 先学会 OpenCV 如何显示画面；
- 先确认“检测框、状态、命令”能画到画面上；
- 等这些基础稳定后，再接 YOLO 或 MediaPipe。

用到的技术点：

- `cv2.VideoCapture`：打开摄像头；
- `cv2.imshow`：显示窗口；
- `cv2.rectangle`：画检测框；
- `cv2.putText`：画状态文字；
- `cv2.waitKey`：监听键盘，按 `q` 退出。

为什么不直接接 YOLO：

因为 YOLO 需要模型文件、类别定义、阈值调试，甚至可能需要训练数据。先把摄像头和显示流程跑通，可以把问题拆小。

更简单的替代方案：

只在控制台打印状态，不显示摄像头画面。

更复杂的替代方案：

直接接 YOLO，或者做 Web dashboard，把摄像头画面推到浏览器。

真实球车风险：

摄像头画面能显示，不代表真实车可以安全跟随。真实系统还要处理延迟、掉帧、摄像头安装角度、震动、光照、目标丢失和急停策略。

## 第二阶段第 2 小步：MediaPipe 手势检测

现在主程序支持：

```bash
PYTHONPATH=src python3 -m golf_cart_vision.main --camera --detector mediapipe
```

这一小步开始真正看摄像头里的手，而不是只用 mock detector。

新版 `mediapipe 0.10.35` 使用 Tasks API，需要本地模型文件：

```text
models/hand_landmarker.task
```

这个模型文件负责从图像里找手部 21 个关键点。我们的代码不训练模型，只使用这个现成模型输出的关键点，再做分开/合并规则判断。

当前手势约定：

- 手指分开的张开手掌：启动跟随；
- 手指合并的张开手掌：停止跟随。

### MediaPipe 是什么

MediaPipe 可以理解成一个现成的“手部关键点检测器”。它看到一只手后，会输出 21 个点。

这些点不是手势名字，而是类似：

```text
手腕在哪里
食指指尖在哪里
食指关节在哪里
中指指尖在哪里
...
```

### 这一阶段怎么判断手势

我们没有训练模型，而是用简单规则：

```text
如果食指/中指/无名指/小指都伸直，并且指尖间距较大 -> 分开张开手掌 -> START_GESTURE
如果食指/中指/无名指/小指都伸直，并且指尖间距较小 -> 合并张开手掌 -> STOP_GESTURE
其他情况 -> NO_GESTURE
```

大白话解释：

在图片坐标里，`y` 越小，点越靠上。如果某根手指的指尖比中间关节更靠上，就粗略认为这根手指伸直了。

然后再看四个指尖之间的平均距离：

- 距离大：手指分开；
- 距离小：手指合并。

为了适配不同远近，代码不是直接看像素距离，而是用“指尖间距 / 手掌宽度”这个比例。这样手离摄像头近一点或远一点，判断会更稳定。

当前规则不判断手心还是手背。也就是说，手心朝摄像头和手背朝摄像头都可以尝试识别；真正限制是 MediaPipe 能不能稳定抓到 21 个关键点。

### 为什么状态切换有时不及时

这是初步试验版的典型现象。现在程序只看两个东西：

```text
手指是否都伸直
指尖间距比例是否超过阈值
```

如果你张开/合并时状态变化慢，通常有三种原因：

- MediaPipe 关键点本身有延迟或抖动；
- `spread_ratio` 在阈值附近来回波动；
- 你的真实手势和默认阈值 `0.55` 不匹配。

现在画面上会显示：

```text
GESTURE: ... ratio=0.72 threshold=0.55 fingers=4
```

调参规则：

- 张开后 `START` 慢：降低 `palm_spread_threshold`；
- 合并后 `STOP` 慢：提高 `palm_spread_threshold`。

运行例子：

```bash
PYTHONPATH=src python -m golf_cart_vision.main --camera --detector mediapipe --palm-spread-threshold 0.45
```

这个阶段的目标不是一次调到完美，而是先让你能看到模型内部的判断依据。下一步才适合加入“连续帧确认”和“状态防抖”，让真实产品更稳。

### 为什么先用 MediaPipe 而不是 YOLO

MediaPipe 不需要你现在有训练数据，也不需要你先训练模型。

它适合教学，因为你可以看到“手势判断”背后的逻辑：

```text
摄像头画面 -> 手部 21 个点 -> 手指是否伸直 + 指尖间距 -> 手势事件 -> 状态机
```

YOLO 更适合后续产品化或特定手势训练：

```text
摄像头画面 -> YOLO 直接输出 start/stop 类别和检测框
```

### 替代方案

更简单：

继续用 mock detector，只验证状态机。

更复杂：

训练 YOLO 手势模型，或者用连续动作识别模型判断一段时间内的动作。

### 真实球车风险

这个规则版检测器还不能直接用于真实球车：

- 张开手掌和普通挥手可能混淆；
- 手指合并/分开的阈值可能因人手大小、距离、角度变化而不稳定；
- 手背朝向时如果关键点不稳定，识别也会不稳定；
- 只看单帧容易误触发；
- 远距离时手太小，关键点会不稳定；
- 真实车必须加入连续帧确认、目标锁定、急停和底盘安全策略。

## 本阶段练习 2

练习文件在：

```text
exercises/02_finger_count_classifier/
```

练习目标：自己写一个简化版“手指分开/合并判断”，理解 MediaPipe 关键点判断手势的基本原理。
