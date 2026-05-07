import tkinter as tk
import winsound

WORK_SECONDS = 25 * 60
BREAK_SECONDS = 5 * 60
TICK_MS = 1000


class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("番茄钟")
        self.root.geometry("360x280")
        self.root.resizable(False, False)
        self._center_window()

        self.is_work = True
        self.remaining = WORK_SECONDS
        self.running = False
        self._after_id = None

        self._build_ui()
        self._update_display()

    def _center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"+{x}+{y}")

    def _build_ui(self):
        self.status_label = tk.Label(
            self.root, text="工作中", font=("Microsoft YaHei", 16)
        )
        self.status_label.pack(pady=(30, 5))

        self.time_label = tk.Label(
            self.root, text="25:00", font=("Consolas", 48, "bold")
        )
        self.time_label.pack(pady=10)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        self.start_btn = tk.Button(
            btn_frame, text="开始", width=8, font=("Microsoft YaHei", 11),
            command=self._on_start
        )
        self.start_btn.grid(row=0, column=0, padx=8)

        self.pause_btn = tk.Button(
            btn_frame, text="暂停", width=8, font=("Microsoft YaHei", 11),
            command=self._on_pause, state=tk.DISABLED
        )
        self.pause_btn.grid(row=0, column=1, padx=8)

        self.reset_btn = tk.Button(
            btn_frame, text="重置", width=8, font=("Microsoft YaHei", 11),
            command=self._on_reset
        )
        self.reset_btn.grid(row=0, column=2, padx=8)

    def _on_start(self):
        if self.running:
            return
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self._tick()

    def _on_pause(self):
        self.running = False
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)

    def _on_reset(self):
        self.running = False
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        self.is_work = True
        self.remaining = WORK_SECONDS
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self._update_status()
        self._update_display()

    def _tick(self):
        if not self.running:
            return
        if self.remaining <= 0:
            self._on_timer_end()
            return
        self.remaining -= 1
        self._update_display()
        self._after_id = self.root.after(TICK_MS, self._tick)

    def _on_timer_end(self):
        self.running = False
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        winsound.Beep(1000, 600)
        self.is_work = not self.is_work
        self.remaining = WORK_SECONDS if self.is_work else BREAK_SECONDS
        self._update_status()
        self._update_display()
        self._on_start()

    def _update_display(self):
        mins, secs = divmod(self.remaining, 60)
        self.time_label.config(text=f"{mins:02d}:{secs:02d}")

    def _update_status(self):
        if self.is_work:
            self.status_label.config(text="工作中")
            self.root.config(bg="#f0f0f0")
            self.status_label.config(bg="#f0f0f0")
            self.time_label.config(bg="#f0f0f0", fg="#c0392b")
        else:
            self.status_label.config(text="休息中")
            self.root.config(bg="#e8f5e9")
            self.status_label.config(bg="#e8f5e9")
            self.time_label.config(bg="#e8f5e9", fg="#27ae60")


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()
