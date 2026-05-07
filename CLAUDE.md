# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
python pomodoro.py    # 运行番茄钟（tkinter GUI）
```

无构建步骤、lint 或测试套件。

## Architecture

单文件 tkinter GUI 应用 (`pomodoro.py`)。

- **`CircularProgress`** — 基于 `tk.Canvas` 的环形进度条，用 `create_arc` 绘制背景环和进度环。
- **`PomodoroApp`** — 主应用类，持有全部状态和 UI。
  - **模式**: `MODES` 列表定义三种模式（专注/短休息/长休息），各有独立的时长和强调色。`mode_index` 追踪当前模式。
  - **核心状态**: `remaining`（剩余秒数）、`running`、`completed_count`（已完成番茄数）。
  - **计时**: `_tick()` 通过 `root.after(TICK_MS, self._tick)` 驱动倒计时，每秒更新显示和进度环。计时结束后响铃并自动切换模式（专注→短休息，休息→专注）。
  - **配色**: 模块级常量定义浅色主题，UI 中统一引用。
- `winsound.Beep` 是 Windows 专用 API，移植到其他平台需替换。
