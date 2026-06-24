# Golf Cart Vision MVP

高尔夫球包车视觉跟随项目的第一阶段 MVP。

这一阶段先不接真实球车，也不接 YOLO 模型。目标是先跑通：

```text
mock gesture -> state machine -> mock command -> console output
```

## 当前阶段做了什么

- 两个状态：
  - `IDLE`：未跟随
  - `FOLLOWING`：正在跟随
- 两个手势事件：
  - `START_GESTURE`：启动跟随
  - `STOP_GESTURE`：停止跟随。第一阶段里，停止和暂停使用同一个手势。
- 两个 mock command：
  - `START_FOLLOW`
  - `STOP_FOLLOW`

## 安装

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

第一阶段 demo 只依赖 Python 标准库。下一阶段如果要开摄像头窗口，再安装：

```bash
python -m pip install -r requirements.txt
```

## 运行 demo

默认运行控制台 demo，不需要摄像头和 OpenCV：

```bash
python -m golf_cart_vision.main
```

你应该看到类似输出：

```text
[FRAME 000] gesture=NO_GESTURE detections=0 state=IDLE command=-
[MOCK_COMMAND] START_FOLLOW
[FRAME 001] gesture=START_GESTURE detections=1 state=FOLLOWING command=START_FOLLOW
[FRAME 004] gesture=STOP_GESTURE detections=1 state=IDLE command=STOP_FOLLOW
```

## 运行摄像头 demo

### 摄像头 + mock 检测

这个模式会打开摄像头，但检测结果仍然是假的，适合先验证窗口和画面显示：

```bash
PYTHONPATH=src python3 -m golf_cart_vision.main --camera
```

你应该看到摄像头窗口。窗口上会显示：

- mock 检测框；
- 当前状态 `IDLE` 或 `FOLLOWING`；
- 最近一次 mock command。

按 `q` 退出窗口。

如果想只跑 100 帧：

```bash
PYTHONPATH=src python3 -m golf_cart_vision.main --camera --frames 100
```

### 摄像头 + MediaPipe 真实手势检测

安装依赖：

```bash
python3 -m pip install opencv-python mediapipe
```

下载 MediaPipe 手部关键点模型：

```bash
mkdir -p models
curl -L https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task \
  -o models/hand_landmarker.task
```

运行：

```bash
PYTHONPATH=src python3 -m golf_cart_vision.main --camera --detector mediapipe
```

当前规则：

- 手指分开的张开手掌：`START_GESTURE` -> `START_FOLLOW`
- 手指合并的张开手掌：`STOP_GESTURE` -> `STOP_FOLLOW`

这里的“识别”不是 YOLO 训练模型，而是 MediaPipe 找到手部 21 个关键点后，程序用规则判断手指是否伸直、指尖之间距离是否足够大。

当前规则不区分手心和手背。只要 MediaPipe 能检测到手部关键点，手心朝摄像头或手背朝摄像头都走同一套分开/合并判断。

注意：`mediapipe 0.10.35` 使用新版 Tasks API，不再提供旧的 `mp.solutions.hands` 入口，所以项目需要 `models/hand_landmarker.task` 这个模型文件。

如果你的 Python 版本无法安装 `mediapipe`，建议新建 Python 3.11 或 3.12 虚拟环境再安装。

当前我在你的机器上检查到：

- `python3` 是 Python 3.13.2；
- `mediapipe` 还没有安装；
- `pip` 访问 PyPI 时出现 SSL 证书校验错误。

如果安装时报 SSL 错误，可以先在 macOS 里运行 Python 自带的证书安装脚本，常见路径类似：

```bash
/Applications/Python\ 3.13/Install\ Certificates.command
```

如果你后面安装了 Python 3.12，对应路径可能是：

```bash
/Applications/Python\ 3.12/Install\ Certificates.command
```

MediaPipe 的 [PyPI 页面](https://pypi.org/project/mediapipe/)列出了 Python 3.9、3.10、3.11、3.12 分类器，所以如果 Python 3.13 安装不顺，优先换 Python 3.12。

## 运行测试

```bash
PYTHONPATH=src python -m unittest discover tests
```

如果你已经安装了 `pytest`，也可以运行 `pytest`。

## 关键概念

- YOLO：一种目标检测模型。输入图片，输出图片里有什么目标、目标在哪、模型有多确定。
- bounding box：检测框，表示目标在画面中的位置。
- confidence：置信度，表示模型对检测结果有多确定。
- class id：类别编号，例如 1 代表启动手势，2 代表停止手势。
- state machine：状态机。它规定系统当前是什么状态，收到事件后能不能切换状态。
- mock command：模拟控制指令。现在只打印，未来可以替换成真实底盘通信。

## 下一步

下一小阶段建议加入“连续帧确认”。真实系统不能一帧看到手势就切状态，应该连续多帧确认后再输出命令，减少误触发。
