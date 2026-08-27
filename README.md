# demoCC3 — 番茄钟 (Pomodoro Timer)

> 基于 Python tkinter 的桌面番茄钟应用（带环形进度条 UI）

一个简洁的番茄工作法计时器，带有美观的环形进度条界面，帮助专注工作与休息交替。

---

## 🍅 功能

- **专注模式**：25 分钟倒计时
- **短休息**：5 分钟
- **长休息**：15 分钟（每完成 4 个番茄后触发）
- **环形进度条**：基于 tkinter Canvas 的可视化进度
- **自动切换**：专注 → 短休息 → 专注循环
- **提醒**：时间到后响铃（Windows `winsound.Beep`）

---

## 🚀 运行

```bash
python pomodoro.py
```

> 依赖：Python 3 + tkinter（标准库自带，无需额外安装）
>
> ⚠️ `winsound.Beep` 为 Windows 专用 API，移植到其他平台需替换。

---

## 📁 文件

| 文件 | 说明 |
|---|---|
| `pomodoro.py` | 主程序（单文件，含 CircularProgress + PomodoroApp） |
| `CLAUDE.md` | Claude Code 项目说明文档 |
| `深圳美食图片/` | 深圳美食图片收藏 |

---

*单文件 tkinter GUI 应用，简洁实用。*
