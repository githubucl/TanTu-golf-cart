# Exercise 01: State Machine Basics

## 练习目标

理解状态机的核心：系统当前处于一个状态，收到事件后，按照规则切换到下一个状态。

## 需要改哪个文件

修改本目录下的 `exercise.py`。

## 预期输出

运行：

```bash
python exercises/01_state_machine_basics/exercise.py
```

你应该看到类似输出：

```text
event=start -> state=FOLLOWING
event=stop -> state=IDLE
```

## 提示

- 初始状态设置为 `IDLE`。
- 当状态是 `IDLE` 且事件是 `start`，切到 `FOLLOWING`。
- 当状态是 `FOLLOWING` 且事件是 `stop`，切到 `IDLE`。
- 其他情况保持原状态。

## 答案检查方式

确认 `start` 会让状态变成 `FOLLOWING`，`stop` 会让状态回到 `IDLE`。
