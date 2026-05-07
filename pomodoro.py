import tkinter as tk
import winsound

# 时长配置（秒）
FOCUS_SECONDS = 25 * 60
SHORT_BREAK_SECONDS = 5 * 60
LONG_BREAK_SECONDS = 15 * 60
TICK_MS = 1000

# 配色
BG = "#f0f2f5"
CARD_BG = "#ffffff"
BORDER = "#d0d7de"
TEXT = "#1f2328"
TEXT_DIM = "#656d76"
ACCENT_FOCUS = "#e5534b"
ACCENT_SHORT = "#2da44e"
ACCENT_LONG = "#0969da"
BTN_BG = "#f3f4f6"
BTN_HOVER = "#e1e4e8"


class CircularProgress(tk.Canvas):
    """环形进度条"""

    def __init__(self, parent, size=220, ring_width=10, **kw):
        super().__init__(parent, width=size, height=size,
                         bg=CARD_BG, highlightthickness=0, **kw)
        self.size = size
        self.ring_width = ring_width
        self.center = size / 2
        self.radius = (size - ring_width) / 2 - 4

    def draw(self, fraction, color):
        """fraction: 0.0 ~ 1.0，color: 进度环颜色"""
        self.delete("all")
        r = self.radius
        bbox = (self.center - r, self.center - r,
                self.center + r, self.center + r)
        # 背景环
        self.create_arc(*bbox, outline=BORDER, width=self.ring_width,
                        style="arc", start=90, extent=-359.9)
        if fraction <= 0:
            return
        extent = -fraction * 359.9
        self.create_arc(*bbox, outline=color, width=self.ring_width,
                        style="arc", start=90, extent=extent)


class PomodoroApp:
    MODES = [
        ("专注", FOCUS_SECONDS, ACCENT_FOCUS),
        ("短休息", SHORT_BREAK_SECONDS, ACCENT_SHORT),
        ("长休息", LONG_BREAK_SECONDS, ACCENT_LONG),
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("番茄钟")
        self.root.geometry("400x520")
        self.root.resizable(False, False)
        self.root.config(bg=BG)
        self._center_window()

        # 状态
        self.mode_index = 0  # 0=专注, 1=短休息, 2=长休息
        self.total_seconds = self.MODES[0][1]
        self.remaining = self.total_seconds
        self.running = False
        self._after_id = None
        self.completed_count = 0  # 已完成番茄数

        self._build_ui()
        self._update_display()
        self._draw_progress()

    def _center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"+{x}+{y}")

    def _build_ui(self):
        # 主容器
        self.main_frame = tk.Frame(self.root, bg=CARD_BG,
                                   highlightthickness=1,
                                   highlightbackground=BORDER)
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center",
                              width=360, height=480)

        # 标题
        tk.Label(self.main_frame, text="🍅 番茄钟", font=("Microsoft YaHei", 18, "bold"),
                 fg=TEXT, bg=CARD_BG).pack(pady=(28, 16))

        # 模式选择器
        mode_frame = tk.Frame(self.main_frame, bg=CARD_BG)
        mode_frame.pack(pady=(0, 10))
        self.mode_btns = []
        for i, (name, _, color) in enumerate(self.MODES):
            btn = tk.Button(mode_frame, text=name, font=("Microsoft YaHei", 10),
                            fg=TEXT_DIM, bg=BTN_BG, activeforeground=TEXT,
                            activebackground=BTN_HOVER,
                            relief="flat", bd=0, padx=14, pady=6,
                            cursor="hand2",
                            command=lambda idx=i: self._switch_mode(idx))
            btn.pack(side="left", padx=4)
            self.mode_btns.append(btn)
        self._highlight_mode()

        # 环形进度 + 时间
        self.progress = CircularProgress(self.main_frame, size=220, ring_width=10)
        self.progress.pack(pady=(10, 0))

        # 时间文字（叠在环形中间）
        self.time_label = tk.Label(self.progress, text="25:00",
                                   font=("Consolas", 44, "bold"),
                                   fg=TEXT, bg=CARD_BG)
        self.time_label.place(relx=0.5, rely=0.45, anchor="center")

        # 状态文字
        self.status_label = tk.Label(self.progress, text="专注",
                                     font=("Microsoft YaHei", 11),
                                     fg=ACCENT_FOCUS, bg=CARD_BG)
        self.status_label.place(relx=0.5, rely=0.68, anchor="center")

        # 完成计数
        count_frame = tk.Frame(self.main_frame, bg=CARD_BG)
        count_frame.pack(pady=(14, 0))
        self.count_label = tk.Label(count_frame, text="已完成 0 个番茄",
                                    font=("Microsoft YaHei", 10),
                                    fg=TEXT_DIM, bg=CARD_BG)
        self.count_label.pack()

        # 按钮区
        btn_frame = tk.Frame(self.main_frame, bg=CARD_BG)
        btn_frame.pack(pady=(18, 20))

        self.start_btn = tk.Button(btn_frame, text="开始专注",
                                   font=("Microsoft YaHei", 12, "bold"),
                                   fg="#ffffff", bg=ACCENT_FOCUS,
                                   activeforeground="#ffffff",
                                   activebackground="#c94640",
                                   relief="flat", bd=0, padx=36, pady=10,
                                   cursor="hand2",
                                   command=self._on_start)
        self.start_btn.pack(side="left", padx=8)

        self.reset_btn = tk.Button(btn_frame, text="重置",
                                   font=("Microsoft YaHei", 11),
                                   fg=TEXT_DIM, bg=BTN_BG,
                                   activeforeground=TEXT,
                                   activebackground=BTN_HOVER,
                                   relief="flat", bd=0, padx=22, pady=10,
                                   cursor="hand2",
                                   command=self._on_reset)
        self.reset_btn.pack(side="left", padx=8)

    def _highlight_mode(self):
        _, _, color = self.MODES[self.mode_index]
        for i, btn in enumerate(self.mode_btns):
            if i == self.mode_index:
                btn.config(fg="#ffffff", bg=color,
                           activeforeground="#ffffff", activebackground=color)
            else:
                btn.config(fg=TEXT_DIM, bg=BTN_BG,
                           activeforeground=TEXT, activebackground=BTN_HOVER)

    def _switch_mode(self, idx):
        if self.running:
            self._on_pause()
        self.mode_index = idx
        self.total_seconds = self.MODES[idx][1]
        self.remaining = self.total_seconds
        self._highlight_mode()
        self._update_display()
        self._update_status()
        self._draw_progress()
        self.start_btn.config(text=f"开始{self.MODES[idx][0]}",
                              bg=self.MODES[idx][2],
                              activebackground=self._darken(self.MODES[idx][2]))

    def _on_start(self):
        if self.running:
            # 暂停
            self._on_pause()
            return
        self.running = True
        _, _, color = self.MODES[self.mode_index]
        self.start_btn.config(text="暂停",
                              bg="#656d76",
                              activebackground="#4a5568")
        self._tick()

    def _on_pause(self):
        self.running = False
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        _, _, color = self.MODES[self.mode_index]
        self.start_btn.config(text=f"开始{self.MODES[self.mode_index][0]}",
                              bg=color,
                              activebackground=self._darken(color))

    def _on_reset(self):
        if self.running:
            self._on_pause()
        self.remaining = self.total_seconds
        self._update_display()
        self._draw_progress()

    def _tick(self):
        if not self.running:
            return
        if self.remaining <= 0:
            self._on_timer_end()
            return
        self.remaining -= 1
        self._update_display()
        self._draw_progress()
        self._after_id = self.root.after(TICK_MS, self._tick)

    def _on_timer_end(self):
        self.running = False
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        winsound.Beep(1000, 600)

        # 专注模式完成才计数
        if self.mode_index == 0:
            self.completed_count += 1
            self.count_label.config(text=f"已完成 {self.completed_count} 个番茄")

        # 自动切换到下一个模式
        if self.mode_index == 0:
            self._switch_mode(1)  # 专注 -> 短休息
        else:
            self._switch_mode(0)  # 休息 -> 专注

        self._on_start()

    def _update_display(self):
        mins, secs = divmod(self.remaining, 60)
        self.time_label.config(text=f"{mins:02d}:{secs:02d}")

    def _update_status(self):
        name, _, color = self.MODES[self.mode_index]
        self.status_label.config(text=name, fg=color)

    def _draw_progress(self):
        fraction = 1.0 - (self.remaining / self.total_seconds)
        _, _, color = self.MODES[self.mode_index]
        self.progress.draw(fraction, color)

    @staticmethod
    def _darken(hex_color, factor=0.85):
        """将颜色变暗"""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r, g, b = int(r * factor), int(g * factor), int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()
