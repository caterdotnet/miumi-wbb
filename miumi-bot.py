import sys
import os

def resource(relative_path):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)

import tkinter as tk
import tkinter.font
import tkinter.filedialog
import random
import time
import pyautogui
import webbrowser
from pynput.keyboard import Controller as KbController, Key
keyboard = KbController()

import pygetwindow as gw

START_TIME = time.time()

WORDS_FILE = resource("valid-words.txt")

# data

def load_words(filepath: str) -> list[str]:
    try:
        with open(filepath, "r") as f:
            return [line.strip().upper() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def find_word(slice_str: str, word_list: list[str], played: set[str], poi: str = "random"):
    slice_upper = slice_str.upper()
    all_matches  = [w for w in word_list if slice_upper in w]
    avail        = [w for w in all_matches if w not in played]
    already_played = len(all_matches) - len(avail)
    if not avail:
        return None, len(all_matches), already_played
    if poi == "long":
        result = max(avail, key=len)
    elif poi == "short":
        result = min(avail, key=len)
    elif poi == "hyphen":
        hyphenated = [w for w in avail if "-" in w]
        result = random.choice(hyphenated) if hyphenated else random.choice(avail)
    else:
        result = random.choice(avail)
    return result, len(avail), already_played

# im gonna dieeeeeeeeeehjuhugeuhuhgeahugaeuhahuhuhueghaugehukgaehkuagekhauguhkgheuake pl ease ghekep me!!11!!111

XP_BG      = "#ece9d8"
XP_TITLE_L = "#0a246a"
XP_TITLE_R = "#a6caf0"
XP_TITLE_FG= "#ffffff"
XP_BTN     = "#ece9d8"
XP_BORDER2 = "#003c74"
XP_BLUE    = "#0a246a"
XP_HILIGHT = "#316ac5"
XP_WHITE   = "#ffffff"
XP_TEXT    = "#000000"
XP_SUBTEXT = "#555555"
XP_BORDER  = "#919b9c"
XP_ERR     = "#cc0000"
SEG        = "Tahoma"

WINDOW_KEYWORDS = ["Roblox", "Roblox Player", "RobloxPlayer", "Word Bomb", "wordbomb", "Chrome", "Google Chrome"]

# more ui design because YES

def draw_gradient(canvas, w, h, color_l, color_r):
    r1,g1,b1 = [x>>8 for x in canvas.winfo_rgb(color_l)]
    r2,g2,b2 = [x>>8 for x in canvas.winfo_rgb(color_r)]
    for i in range(w):
        t = i / max(w-1, 1)
        color = "#{:02x}{:02x}{:02x}".format(
            int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t)
        )
        canvas.create_line(i, 0, i, h, fill=color)

def xp_button(parent, text, command, width=10):
    return tk.Button(
        parent, text=text, command=command,
        font=(SEG, 8), bg=XP_BTN, fg=XP_TEXT,
        activebackground="#dff0ff", activeforeground=XP_TEXT,
        relief="raised", bd=2, padx=8, pady=3,
        cursor="arrow", width=width,
        highlightbackground=XP_BORDER2,
        highlightcolor=XP_BORDER2,
        highlightthickness=1,
    )

def focus_game_window():
    """Try to focus Roblox or Chrome using substring match on window titles."""
    all_wins = gw.getAllWindows()
    for kw in WINDOW_KEYWORDS:
        kw_lower = kw.lower()
        matches = [w for w in all_wins if kw_lower in w.title.lower() and w.title.strip()]
        if matches:
            try:
                matches[0].activate()
                return True
            except Exception:
                pass
    return False

# actual app

class WordBombApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Miumi")
        self.root.resizable(False, False)
        self.root.configure(bg=XP_BG)
        try:
            icon = tk.PhotoImage(file=resource("miumi-profile.png"))
            self.root.iconphoto(True, icon)
        except Exception:
            pass
        self.root.geometry("480x560")

        self.word_list = load_words(WORDS_FILE)
        self.played: set[str] = set()
        self._history_entries: list[tuple[str, str]] = []

        self.auto_type_var    = tk.BooleanVar(value=False)
        self.window_focus_var = tk.BooleanVar(value=False)
        self.poi_var          = tk.StringVar(value="random")

        self._build_ui()
        self._update_status_idle()

    def _group(self, parent, label):
        return tk.LabelFrame(
            parent, text=f" {label} ",
            font=(SEG, 8), fg=XP_BLUE, bg=XP_BG,
            relief="groove", bd=2,
        )

    def _get_nerd_font(self, size, bold=False):
        weight = "bold" if bold else "normal"
        for fname in ("JetBrainsMono NF", "JetBrains Mono NF", "JetBrainsMono Nerd Font",
                      "Cascadia Code NF", "FiraCode NF", "Courier New", "Courier", "monospace"):
            try:
                f = tk.font.Font(family=fname, size=size, weight=weight)
                if f.actual("family").lower() not in ("", "system", "fixed"):
                    return (fname, size, weight) if bold else (fname, size)
            except Exception:
                pass
        return ("Courier New", size, weight) if bold else ("Courier New", size)

    def _build_ui(self):
        W = 480

        title_canvas = tk.Canvas(self.root, height=28, width=W, bd=0, highlightthickness=0)
        title_canvas.pack(fill="x")
        self.root.update_idletasks()
        draw_gradient(title_canvas, W, 28, XP_TITLE_L, XP_TITLE_R)
        title_canvas.create_text(8, 14, text="miumi-mim",
                                  font=(SEG, 9, "bold"), fill=XP_TITLE_FG, anchor="w")
        close_btn = tk.Button(self.root, text="✕", font=(SEG, 7, "bold"),
                               bg="#e8404a", fg=XP_WHITE, activebackground="#ff6060",
                               relief="raised", bd=1, width=2, padx=0, command=self.root.destroy)
        title_canvas.create_window(W-6, 4, anchor="ne", window=close_btn, width=18, height=20)

        tk.Frame(self.root, bg="#4a90d9", height=2).pack(fill="x")

        header = tk.Frame(self.root, bg=XP_BG, padx=12, pady=8)
        header.pack(fill="x")

        try:
            self._pfp_img = tk.PhotoImage(file=resource("miumi-profile.png"))
            orig_w = self._pfp_img.width()
            orig_h = self._pfp_img.height()
            scale  = max(1, max(orig_w, orig_h) // 40)
            if scale > 1:
                self._pfp_img = self._pfp_img.subsample(scale, scale)
            pfp_label = tk.Label(header, image=self._pfp_img, bg=XP_BG, relief="flat", bd=0)
        except Exception:
            pfp_label = tk.Label(header, text="💣", font=(SEG, 24), bg=XP_BG)
        pfp_label.pack(side="left", padx=(0, 10))

        name_frame = tk.Frame(header, bg=XP_BG)
        name_frame.pack(side="left", anchor="w")

        nf = self._get_nerd_font(13, bold=True)
        tk.Label(name_frame, text="miumi-mim", font=nf,
                 fg=XP_BLUE, bg=XP_BG).pack(anchor="w")

        info_link = tk.Label(name_frame, text="see info",
                              font=(SEG, 8, "underline"), fg=XP_HILIGHT, bg=XP_BG,
                              cursor="hand2")
        info_link.pack(anchor="w")
        info_link.bind("<Button-1>", lambda e: self._toggle_info())

        tk.Frame(self.root, bg=XP_BORDER, height=1).pack(fill="x", padx=12)

        self._body_container = tk.Frame(self.root, bg=XP_BG)
        self._body_container.pack(fill="both", expand=True)

        self._main_body = tk.Frame(self._body_container, bg=XP_BG, padx=12, pady=10)
        self._main_body.pack(fill="both", expand=True)

        self._info_body = tk.Frame(self._body_container, bg=XP_BG, padx=16, pady=12)

        self._info_showing = False
        body = self._main_body

        grp_input = self._group(body, "Enter Word Slice")
        grp_input.pack(fill="x", pady=(0, 8))

        input_inner = tk.Frame(grp_input, bg=XP_BG)
        input_inner.pack(padx=8, pady=6, fill="x")

        tk.Label(input_inner, text="Slice:", font=(SEG, 8),
                 fg=XP_TEXT, bg=XP_BG).pack(side="left")

        self.entry = tk.Entry(input_inner, font=(SEG, 10, "bold"),
                               bg=XP_WHITE, fg=XP_TEXT,
                               insertbackground=XP_HILIGHT,
                               relief="sunken", bd=2, width=14)
        self.entry.pack(side="left", padx=(6, 8), ipady=2)
        self.entry.bind("<Return>", lambda e: self._on_find())
        self.entry.focus()

        xp_button(input_inner, "Find Word", self._on_find, width=9).pack(side="left")

        grp_result = self._group(body, "Result")
        grp_result.pack(fill="x", pady=(0, 8))

        result_inner = tk.Frame(grp_result, bg=XP_WHITE, relief="sunken", bd=1)
        result_inner.pack(padx=8, pady=6, fill="x")

        self.output_label = tk.Label(
            result_inner, text="[ waiting for input... ]",
            font=(SEG, 12, "bold"), fg=XP_SUBTEXT, bg=XP_WHITE,
            anchor="w", padx=8, pady=6, width=26, wraplength=380,
        )
        self.output_label.pack(fill="x")

        grp_hist = self._group(body, "Session History")
        grp_hist.pack(fill="both", expand=True, pady=(0, 4))

        hist_inner = tk.Frame(grp_hist, bg=XP_BG)
        hist_inner.pack(padx=8, pady=6, fill="both", expand=True)

        scrollbar = tk.Scrollbar(hist_inner, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.played_listbox = tk.Listbox(
            hist_inner, font=("Courier New", 9),
            bg=XP_WHITE, fg=XP_TEXT,
            selectbackground=XP_HILIGHT, selectforeground=XP_WHITE,
            relief="sunken", bd=2, height=6,
            yscrollcommand=scrollbar.set, activestyle="dotbox",
        )
        self.played_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.played_listbox.yview)

        export_row = tk.Frame(body, bg=XP_BG)
        export_row.pack(fill="x", pady=(0, 6))
        xp_button(export_row, "Export List", self._export_list, width=10).pack(side="left")

        grp_poi = self._group(body, "Priority (poi)")
        grp_poi.pack(fill="x", pady=(0, 8))

        poi_inner = tk.Frame(grp_poi, bg=XP_BG)
        poi_inner.pack(padx=8, pady=4, fill="x")

        for label, value in [
            ("None (random)",   "random"),
            ("Long words",      "long"),
            ("Short words",     "short"),
            ("Hyphenated",      "hyphen"),
        ]:
            tk.Radiobutton(
                poi_inner, text=label, variable=self.poi_var, value=value,
                font=(SEG, 8), bg=XP_BG, fg=XP_TEXT,
                activebackground=XP_BG, cursor="arrow",
                selectcolor=XP_WHITE,
            ).pack(side="left", padx=(0, 10))

        tk.Frame(self.root, bg=XP_BORDER, height=1).pack(fill="x")

        footer = tk.Frame(self.root, bg=XP_BG, pady=6)
        footer.pack(fill="x")

        left_footer = tk.Frame(footer, bg=XP_BG)
        left_footer.pack(side="left", padx=8)

        xp_button(left_footer, "New Session", self._new_session, width=10).pack(side="left")

        chk_frame = tk.Frame(left_footer, bg=XP_BG)
        chk_frame.pack(side="left", padx=(10, 0))

        tk.Checkbutton(
            chk_frame, text="Auto type", variable=self.auto_type_var,
            font=(SEG, 7), bg=XP_BG, fg=XP_TEXT,
            activebackground=XP_BG, cursor="arrow",
        ).pack(anchor="w")

        tk.Checkbutton(
            chk_frame, text="Window focus", variable=self.window_focus_var,
            font=(SEG, 7), bg=XP_BG, fg=XP_TEXT,
            activebackground=XP_BG, cursor="arrow",
        ).pack(anchor="w")

        self.status_label = tk.Label(
            footer, text="",
            font=(SEG, 7), fg=XP_SUBTEXT, bg=XP_BG,
            anchor="e", wraplength=220, justify="right",
        )
        self.status_label.pack(side="right", padx=8)

    # info page

    def _build_info_page(self):
        nf = self._get_nerd_font(11, bold=True)
        for widget in self._info_body.winfo_children():
            widget.destroy()

        tk.Label(self._info_body, text="miumi-mim — Info",
                 font=nf, fg=XP_BLUE, bg=XP_BG).pack(anchor="w", pady=(0, 6))

        tk.Frame(self._info_body, bg=XP_BORDER, height=1).pack(fill="x", pady=(0, 8))

        sections = [
            ("What is Miumi?",
             "Miumi is a Word Bomb assistant bot. Give it a word slice (e.g. AW) "
             "and it instantly finds a valid word from a 286k+ word dictionary that "
             "satisfies the slice. It can also auto-focus the game window and type "
             "the word for you — hands-free."),

            ("How to use",
             "1. Type your slice into the input box and press Enter or click Find Word.\n"
             "2. The result appears in the Result box.\n"
             "3. Enable Auto type + Window focus to have Miumi type directly into Roblox or Chrome.\n"
             "4. Click New Session to reset the played words list between games."),

            ("Settings",
             "Auto type — Miumi types the result into the focused window using driver-level "
             "keystrokes.\n\n"
             "Window focus — Miumi finds and activates Roblox or Chrome window before typing. "
             "If no matching window is found, it aborts and shows an error in the log.\n\n"
             "Priority (poi) — Controls which word is picked from all valid matches:\n"
             "  \u2022 None (random): picks any valid word at random.\n"
             "  \u2022 Long words: always picks the longest matching word.\n"
             "  \u2022 Short words: always picks the shortest matching word.\n"
             "  \u2022 Hyphenated: prefers hyphenated words; falls back to random if none exist.\n"
             "  Only one poi mode can be active at a time."),

            ("Session history",
             "Every word Miumi plays is logged in the Session History list. "
             "Miumi will never repeat a word within the same session. "
             "Click New Session to clear the list and start fresh.\n\n"
             "Export List — saves the current session history to a .txt file. "
             "A save dialog lets you choose the filename and location."),
        ]

        for title, body_text in sections:
            tk.Label(self._info_body, text=title,
                     font=(SEG, 9, "bold"), fg=XP_TEXT, bg=XP_BG).pack(anchor="w", pady=(6, 2))
            tk.Label(self._info_body, text=body_text,
                     font=(SEG, 8), fg=XP_SUBTEXT, bg=XP_BG,
                     wraplength=430, justify="left").pack(anchor="w", padx=(8, 0))

        tk.Button(self._info_body, text="\u2190 Back",
                  font=(SEG, 8), bg=XP_BTN, fg=XP_TEXT,
                  activebackground="#dff0ff", relief="raised", bd=2,
                  cursor="arrow", padx=8, pady=3,
                  command=self._toggle_info).pack(anchor="w", pady=(14, 0))

    def _toggle_info(self):
        if not self._info_showing:
            self._build_info_page()
            self._main_body.pack_forget()
            self._info_body.pack(fill="both", expand=True)
            self._info_showing = True
        else:
            self._info_body.pack_forget()
            self._main_body.pack(fill="both", expand=True)
            self._info_showing = False

    # logic

    def _runtime(self):
        elapsed = int(time.time() - START_TIME)
        h, rem  = divmod(elapsed, 3600)
        m, s    = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def _update_status_idle(self):
        n = len(self.word_list)
        self.status_label.config(
            text=f"No words played. {n:,} words loaded.  [{self._runtime()}]",
            fg=XP_SUBTEXT,
        )

    def _on_find(self):
        slice_str = self.entry.get().strip()
        if not slice_str:
            return

        if not self.word_list:
            self._set_output("valid-words.txt not loaded.", error=True)
            return

        result, match_count, already_played = find_word(slice_str, self.word_list, self.played, self.poi_var.get())

        if result:
            self.played.add(result)
            self._set_output(result)
            self._add_to_history(result, slice_str)

            n_loaded = len(self.word_list)
            self.status_label.config(
                text=f"[{slice_str.upper()}]; {match_count:,} - {already_played} words found. {n_loaded:,} words loaded.  [{self._runtime()}]",
                fg=XP_SUBTEXT,
            )

            if self.window_focus_var.get():
                focused = focus_game_window()
                if not focused:
                    self.status_label.config(
                        text="Window not found! Is Roblox/Word Bomb open?",
                        fg=XP_ERR,
                    )
                    self.entry.delete(0, tk.END)
                    self.entry.focus()
                    return
                time.sleep(0.5)

            if self.auto_type_var.get():
                for ch in result.lower():
                    keyboard.press(ch)
                    keyboard.release(ch)
                    time.sleep(0.04)
                keyboard.press(Key.enter)
                keyboard.release(Key.enter)
                time.sleep(0.1)
                self.root.after(0, self.root.focus_force)
                time.sleep(0.1)
                self.root.after(0, self.root.focus_force)
                self.root.after(0, self.entry.focus)

        else:
            self._set_output(f'None for "{slice_str.upper()}"', error=True)
            self.status_label.config(
                text=f"[{slice_str.upper()}]; 0 - {already_played} words found. {len(self.word_list):,} words loaded.  [{self._runtime()}]",
                fg=XP_ERR,
            )

        self.entry.delete(0, tk.END)
        self.entry.focus()

    def _set_output(self, text: str, error: bool = False):
        self.output_label.config(
            text=text.upper(),
            fg=XP_ERR if error else XP_BLUE,
        )

    def _add_to_history(self, word: str, slice_str: str):
        self._history_entries.append((word, slice_str))
        count = self.played_listbox.size() + 1
        self.played_listbox.insert(
            tk.END,
            f"  {count:>3}.  {word:<22}  [{slice_str.upper()}]"
        )
        self.played_listbox.yview_moveto(1.0)

    def _export_list(self):
        if not self._history_entries:
            self.status_label.config(text="Nothing to export yet.", fg=XP_ERR)
            return

        filepath = tkinter.filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="miumi-session.txt",
            title="Export Session History",
        )
        if not filepath:
            return

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"miumi-mim — Session Export\n")
            f.write(f"Runtime: {self._runtime()}  |  Words played: {len(self._history_entries)}\n")
            f.write("=" * 50 + "\n\n")
            for i, (word, slice_str) in enumerate(self._history_entries, 1):
                f.write(f"  {i:>3}.  {word:<22}  [{slice_str.upper()}]\n")

        self.status_label.config(
            text=f"Exported {len(self._history_entries)} words.",
            fg=XP_SUBTEXT,
        )

    def _new_session(self):
        last_count = len(self.played)
        self.played.clear()
        self._history_entries.clear()
        self.played_listbox.delete(0, tk.END)
        self.output_label.config(text="[ new session started... ]", fg=XP_SUBTEXT)
        n = len(self.word_list)
        self.status_label.config(
            text=f"{last_count} words last session. {n:,} words loaded.  [{self._runtime()}]",
            fg=XP_SUBTEXT,
        )
        self.entry.focus()

if __name__ == "__main__":
    root = tk.Tk()
    app = WordBombApp(root)
    root.mainloop()