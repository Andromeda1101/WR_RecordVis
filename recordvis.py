import os
import random
from datetime import datetime
import tkinter as tk
from tkinter import font as tkfont

from config import RecordConfig
from log import Log

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def session_logfile() -> str:
    ensure_dir(RecordConfig.record_dir)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(RecordConfig.record_dir, f"session_{ts}.log")

def build_trials():
    # Mapping according to experiment.md
    order = [
        ("board", ["number", "alphabet", "word"]),
        ("board", ["number", "alphabet", "word"]),
        ("palm",  ["number", "alphabet", "word"]),
        ("thigh", ["number", "alphabet", "word"]),
    ]
    trials = []

    # Read counts with new semantics:
    # - numbers: cycles of 0..9 => 10 * cycles
    # - alphabet: cycles of A..Z then a..z => 52 * cycles
    # - words: exact count
    num_cycles = RecordConfig.number_times
    alpha_cycles = RecordConfig.alphabet_times
    word_count = RecordConfig.word_times

    def repeat_cycles(seq: list[str], cycles: int) -> list[str]:
        return seq * max(0, int(cycles))

    def fill_to_count(seq: list[str], n: int) -> list[str]:
        if not seq:
            return [""] * n
        return [seq[i % len(seq)] for i in range(n)]

    # Pre-built base sequences
    numbers_base = RecordConfig.number_list  # ["0".."9"]
    alphabet_base = RecordConfig.alphabet_list_upper + RecordConfig.alphabet_list_lower  # A..Z then a..z

    def numbers_stimuli() -> list[str]:
        return repeat_cycles(numbers_base, num_cycles)  # length 10 * num_cycles

    def alphabet_stimuli() -> list[str]:
        return repeat_cycles(alphabet_base, alpha_cycles)  # length 52 * alpha_cycles

    # CHANGED: randomize word selection
    def words_stimuli(n: int) -> list[str]:
        wl = RecordConfig.word_list or []
        if not wl:
            return [""] * n
        if len(wl) >= n:
            return random.sample(wl, k=n)
        return random.choices(wl, k=n)

    for body_part, contents in order:
        for content in contents:
            if content == "number":
                stimuli = numbers_stimuli()
            elif content == "alphabet":
                stimuli = alphabet_stimuli()
            else:  # word
                stimuli = words_stimuli(word_count)

            n = len(stimuli)
            half = n // 2
            speeds_seq = (["fast"] * half) + (["slow"] * (n - half))

            for i in range(n):
                trials.append({
                    "body_part": body_part,
                    "content": content,        # category
                    "speed": speeds_seq[i],
                    "stimulus": stimuli[i],    # concrete item
                })
    return trials

class ExperimentUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.trials = build_trials()
        self.index = 0
        self.recording = False
        self.logger = Log(session_logfile())

        self.root.title("WR RecordVis")
        self.root.geometry("900x600")
        self.root.configure(bg="white")

        self.font_title = tkfont.Font(family="Arial", size=28, weight="bold")
        self.font_body = tkfont.Font(family="Arial", size=20)
        self.font_status = tkfont.Font(family="Arial", size=18, slant="italic")

        self.lbl_title = tk.Label(root, text="可视化实验记录平台", font=self.font_title, bg="white")
        self.lbl_title.pack(pady=10)

        self.lbl_info = tk.Label(root, text="", font=self.font_body, bg="white", justify="left")
        self.lbl_info.pack(pady=10)

        self.lbl_stim = tk.Label(root, text="", font=self.font_body, fg="#333", bg="white")
        self.lbl_stim.pack(pady=20)

        self.lbl_status = tk.Label(root, text="按空格开始/结束，本次试次尚未开始", font=self.font_status, fg="#0066cc", bg="white")
        self.lbl_status.pack(pady=10)

        self.lbl_help = tk.Label(root, text="SPACE 开始/结束, ESC 退出", font=self.font_status, fg="#999", bg="white")
        self.lbl_help.pack(pady=5)

        root.bind("<space>", self.on_space)
        root.bind("<Escape>", self.on_escape)

        self.update_view()

    def current_trial(self):
        return self.trials[self.index] if self.index < len(self.trials) else None

    def update_view(self):
        t = self.current_trial()
        if not t:
            self.lbl_info.config(text="实验完成")
            self.lbl_stim.config(text="")
            self.lbl_status.config(text="所有试次已结束，按 ESC 退出")
            return

        label_map = {"number": "数字", 
                     "alphabet": "字母", 
                     "word": "单词",
                     "thigh": "大腿",
                     "palm": "手掌",
                     "board": "手写板",
                     "fast": "快",
                     "slow": "慢",
                     }


        info = [
            f"部位: {label_map.get(t['body_part'], '未知')}",
            f"内容: {label_map.get(t['content'], '未知')}",
            f"速度: {label_map.get(t['speed'], '未知')}",
            f"进度: {self.index + 1} / {len(self.trials)}",
        ]
        self.lbl_info.config(text="\n".join(info))

        stim_label = label_map.get(t["content"], "内容")
        self.lbl_stim.config(text=f"{stim_label}: {t['stimulus']}")

        if not self.recording:
            self.lbl_status.config(text="按空格开始记录（Start）")
        else:
            self.lbl_status.config(text="正在记录... 再次按空格结束（End）")

    def on_space(self, _event=None):
        t = self.current_trial()
        if not t:
            return
        if not self.recording:
            self.logger.set_experiment_info(
                body_part=t["body_part"],
                content=t["content"],   # category
                speed=t["speed"],
                trial_index=self.index + 1,
                stimulus=t["stimulus"], # concrete content
            )
            self.logger.record_start()
            self.recording = True
        else:
            self.logger.record_end()
            self.logger.save_log()
            self.recording = False
            self.index += 1
        self.update_view()

    def on_escape(self, _event=None):
        self.root.quit()

def main():
    random.seed()
    root = tk.Tk()
    ExperimentUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
