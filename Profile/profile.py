# Profile/profile.py
"""
Lightweight profile system that plugs into the existing Tk app (work_timer.py).

- UserProfile persisted to ~/.touch_grass_profile.json
- ProfileWindow (500x600) to edit name/focus/break and view XP
- attach_profile(...) adds a small top-right panel that opens Profile
- GIF clips play in the avatar box when you log certain actions
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional, List
import json, os
import tkinter as tk
from tkinter import messagebox, filedialog

# --- asset paths -------------------------------------------------------------
HERE = os.path.dirname(__file__)
ASSETS_DIR = os.path.abspath(os.path.join(HERE, "..", "pictures"))
DRINK_GIF = os.path.join(ASSETS_DIR, "drink_water.gif")
WALK_GIF  = os.path.join(ASSETS_DIR, "walking.gif")  # make sure this exists

# ----------------------------- storage ---------------------------------------

PROFILE_PATH = os.path.join(os.path.expanduser("~"), ".touch_grass_profile.json")

@dataclass
class UserProfile:
    display_name: str = "Player 1"
    focus_min:   int  = 50
    break_min:   int  = 10
    xp:          int  = 0
    avatar_path: Optional[str] = None

def load_profile() -> UserProfile:
    if not os.path.exists(PROFILE_PATH):
        p = UserProfile(); save_profile(p); return p
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return UserProfile(**data)
    except Exception:
        p = UserProfile(); save_profile(p); return p

def save_profile(p: UserProfile) -> None:
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(asdict(p), f, indent=2)

# ---------------------------- XP helpers -------------------------------------

BASE_LEVEL_XP = 500  # level N requires N * BASE_LEVEL_XP

# Use keys that match the new button handlers below
ACTION_XP = {
    "focus_session": 100,
    "brush_teeth":    50,
    "water_break":    20,
    "outdoor_break":  60,
}
ACTION_MULT = {
    "brush_teeth":   2.0,  # (x2)
    "outdoor_break": 2.0,  # (x2)
}

def level_info(xp: int) -> tuple[int, int, int, int]:
    lvl, rem, need = 1, xp, BASE_LEVEL_XP
    while rem >= need:
        rem -= need
        lvl += 1
        need = BASE_LEVEL_XP * lvl
    return lvl, rem, need, (need - rem)

def grant_xp(prof: UserProfile, action: str, units: int = 1) -> int:
    base = ACTION_XP.get(action, 0)
    mult = ACTION_MULT.get(action, 1.0)
    gained = int(base * mult * max(1, units))
    prof.xp += gained
    save_profile(prof)
    return gained

# --------------- push minutes into an existing timer instance ----------------

def _apply_to_app(app, prof: UserProfile) -> bool:
    changed = False
    if hasattr(app, "work_time"):
        app.work_time = prof.focus_min * 60; changed = True
    if hasattr(app, "break_time"):
        app.break_time = prof.break_min * 60; changed = True

    if changed:
        if hasattr(app, "reset_timer"):
            try: app.reset_timer()
            except Exception: pass
        elif hasattr(app, "_update_timer_label"):
            try:
                if hasattr(app, "time_remaining"):
                    app.time_remaining = app.work_time
                app._update_timer_label()
            except Exception: pass
    return changed

# ------------------------------ Profile window -------------------------------

class ProfileWindow(tk.Toplevel):
    """Profile editor + XP, with short GIF clips in the avatar box."""
    def __init__(self, master: tk.Tk, app, prof: UserProfile,
                 on_change=None, title_prefix: str = "Profile"):
        super().__init__(master)
        self.app, self.prof, self.on_change = app, prof, on_change
        self.title(f"{title_prefix} — {prof.display_name}")
        self.geometry("500x600")
        self.configure(bg="#2E3440")
        self.resizable(False, False)
        self.transient(master)

        # --- animation state (for small GIFs in the avatar box) ---------------
        self._anim_after_id: Optional[str] = None
        self._anim_frames: Optional[List[tk.PhotoImage]] = None
        self._anim_index: int = 0
        self._anim_cycles_left: int = 0
        self._water_frames: Optional[List[tk.PhotoImage]] = None
        self._walk_frames: Optional[List[tk.PhotoImage]] = None

        # Header
        tk.Label(self, text="Profile", font=("Arial", 20, "bold"),
                 fg="#D8DEE9", bg="#2E3440").pack(pady=12)

        # Avatar area (150x150 box)
        self.avatar_img = None
        self.avatar_canvas = tk.Canvas(self, width=150, height=150,
                                       bg="#3B4252", highlightthickness=0)
        self.avatar_canvas.pack(pady=6)
        tk.Button(self, text="Choose Picture…", command=self._choose_avatar)\
            .pack(pady=(0, 8))

        # Editable settings
        frm = tk.Frame(self, bg="#2E3440"); frm.pack(pady=8)

        tk.Label(frm, text="Name:",  fg="#D8DEE9", bg="#2E3440", font=("Arial", 12))\
            .grid(row=0, column=0, sticky="e", padx=8, pady=4)
        tk.Label(frm, text="Focus:", fg="#D8DEE9", bg="#2E3440", font=("Arial", 12))\
            .grid(row=1, column=0, sticky="e", padx=8, pady=4)
        tk.Label(frm, text="Break:", fg="#D8DEE9", bg="#2E3440", font=("Arial", 12))\
            .grid(row=2, column=0, sticky="e", padx=8, pady=4)

        self.name_var  = tk.StringVar(value=prof.display_name)
        self.focus_var = tk.IntVar(value=prof.focus_min)
        self.break_var = tk.IntVar(value=prof.break_min)

        tk.Entry(frm, textvariable=self.name_var, width=20)\
            .grid(row=0, column=1, sticky="w")
        tk.Spinbox(frm, from_=5, to=180, increment=5, textvariable=self.focus_var, width=6)\
            .grid(row=1, column=1, sticky="w")
        tk.Spinbox(frm, from_=3, to=60, increment=1, textvariable=self.break_var, width=6)\
            .grid(row=2, column=1, sticky="w")
        tk.Button(frm, text="Save", command=self._save_basic)\
            .grid(row=0, column=2, rowspan=3, padx=10)

        # Level + XP bar
        self.level_lbl = tk.Label(self, fg="#E5E9F0", bg="#2E3440", font=("Arial", 14, "bold"))
        self.level_lbl.pack(pady=(12, 4))
        self.xp_bar = tk.Canvas(self, width=340, height=18, bg="#3B4252", highlightthickness=0)
        self.xp_bar.pack()
        self.xp_detail = tk.Label(self, fg="#A3B1C6", bg="#2E3440", font=("Arial", 10))
        self.xp_detail.pack(pady=4)

        # XP action buttons (new names)
        act = tk.Frame(self, bg="#2E3440"); act.pack(pady=10)
        self._mk_xp_btn(act, "Log Focus Session",
                        lambda: self._earn("focus_session"))\
            .grid(row=0, column=0, padx=6, pady=4)
        self._mk_xp_btn(act, "Brush Teeth (x2)",
                        lambda: self._earn("brush_teeth"))\
            .grid(row=0, column=1, padx=6, pady=4)
        self._mk_xp_btn(act, "Drink Water",
                        lambda: self._earn("water_break", DRINK_GIF))\
            .grid(row=1, column=0, padx=6, pady=4)
        self._mk_xp_btn(act, "Outdoor Break (x2)",
                        lambda: self._earn("outdoor_break", WALK_GIF))\
            .grid(row=1, column=1, padx=6, pady=4)

        tk.Button(self, text="Close", command=self.destroy).pack(pady=8)

        # Initial paint
        self._draw_avatar()
        self._refresh_xp()
        self.bind("<Escape>", lambda e: self.destroy())

    # ---- animation helpers ---------------------------------------------------

    def _stop_anim(self) -> None:
        if self._anim_after_id is not None:
            try: self.after_cancel(self._anim_after_id)
            except Exception: pass
            self._anim_after_id = None

    def _load_gif_frames(self, path: str) -> Optional[List[tk.PhotoImage]]:
        if not os.path.exists(path):
            return None
        frames: List[tk.PhotoImage] = []
        # Load all frames from a GIF without Pillow
        idx = 0
        try:
            while True:
                fr = tk.PhotoImage(file=path, format=f"gif -index {idx}")
                # Downscale to fit 150×150
                w, h = fr.width(), fr.height()
                fx = max(1, w // 150); fy = max(1, h // 150)
                if fx > 1 or fy > 1:
                    fr = fr.subsample(fx, fy)
                frames.append(fr)
                idx += 1
        except Exception:
            pass
        return frames or None

    def _play_gif(self, frames: Optional[List[tk.PhotoImage]], cycles: int = 2) -> None:
        """Play a preloaded list of frames in the avatar canvas."""
        if not frames:
            return
        self._stop_anim()
        self._anim_frames = frames
        self._anim_index = 0
        self._anim_cycles_left = max(1, cycles)

        def _tick():
            if not self._anim_frames:
                return
            fr = self._anim_frames[self._anim_index]
            self.avatar_canvas.delete("all")
            self.avatar_canvas.create_image(75, 75, image=fr)
            self._anim_index += 1
            if self._anim_index >= len(self._anim_frames):
                self._anim_index = 0
                self._anim_cycles_left -= 1
                if self._anim_cycles_left <= 0:
                    self._stop_anim()
                    self._draw_avatar()
                    return
            self._anim_after_id = self.after(80, _tick)  # ~12.5 fps

        _tick()

    # ---- UI helpers ----------------------------------------------------------

    def _mk_xp_btn(self, parent, text, cmd) -> tk.Button:
        return tk.Button(
            parent, text=text, command=cmd, font=("Arial", 12),
            bg="#81A1C1", fg="#2E3440",
            activebackground="#81A1C1", activeforeground="#2E3440",
            relief="ridge", bd=3
        )

    def _choose_avatar(self) -> None:
        path = filedialog.askopenfilename(
            title="Choose a picture",
            filetypes=[("PNG or GIF", "*.png;*.gif"),
                       ("All supported", "*.png;*.gif;*.ppm;*.pgm;*.jpg;*.jpeg")]
        )
        if not path: return
        self.prof.avatar_path = path
        save_profile(self.prof)
        self._draw_avatar()
        if self.on_change: self.on_change(self.prof)

    def _draw_avatar(self) -> None:
        self.avatar_canvas.delete("all")
        if self.prof.avatar_path and os.path.exists(self.prof.avatar_path):
            try:
                self.avatar_img = tk.PhotoImage(file=self.prof.avatar_path)
                w, h = self.avatar_img.width(), self.avatar_img.height()
                fx = max(1, w // 150); fy = max(1, h // 150)
                if fx > 1 or fy > 1:
                    self.avatar_img = self.avatar_img.subsample(fx, fy)
                self.avatar_canvas.create_image(75, 75, image=self.avatar_img)
                return
            except Exception:
                pass
        # Placeholder
        c = self.avatar_canvas
        c.create_oval(45, 25, 105, 85, fill="#E5E9F0", outline="#D8DEE9", width=2)
        c.create_oval(60, 45, 68, 53, fill="#2E3440")
        c.create_oval(82, 45, 90, 53, fill="#2E3440")
        c.create_line(75, 85, 75, 120, fill="#E5E9F0", width=6)
        c.create_line(55, 120, 95, 120, fill="#E5E9F0", width=12)

    def _save_basic(self) -> None:
        self.prof.display_name = self.name_var.get().strip() or "Player 1"
        self.prof.focus_min   = int(self.focus_var.get())
        self.prof.break_min   = int(self.break_var.get())
        save_profile(self.prof)
        _apply_to_app(self.app, self.prof)
        self.title(f"Profile — {self.prof.display_name}")
        if self.on_change: self.on_change(self.prof)
        messagebox.showinfo("Saved", "Profile updated.", parent=self)

    def _earn(self, action: str, anim_path: Optional[str] = None) -> None:
        gained = grant_xp(self.prof, action)
        self._refresh_xp()
        if self.on_change: self.on_change(self.prof)

        # Play the requested clip (preload & cache)
        if anim_path:
            if anim_path == DRINK_GIF:
                if self._water_frames is None:
                    self._water_frames = self._load_gif_frames(DRINK_GIF)
                self._play_gif(self._water_frames, cycles=2)
            elif anim_path == WALK_GIF:
                if self._walk_frames is None:
                    self._walk_frames = self._load_gif_frames(WALK_GIF)
                self._play_gif(self._walk_frames, cycles=2)

        messagebox.showinfo("XP", f"+{gained} XP ({action.replace('_',' ').title()})", parent=self)

    def _refresh_xp(self) -> None:
        lvl, into, need, left = level_info(self.prof.xp)
        self.level_lbl.config(text=f"Level {lvl}")
        self.xp_bar.delete("all")
        w = int(340 * into / max(1, need))
        self.xp_bar.create_rectangle(0, 0, 340, 18, fill="#3B4252", outline="")
        self.xp_bar.create_rectangle(0, 0, w, 18, fill="#A3BE8C", outline="")
        self.xp_detail.config(text=f"{self.prof.xp} XP  •  {left} XP to next level")

# --------------------- public helpers / top-right panel ----------------------

_PROFILE_WIN_REF: ProfileWindow | None = None

def _position_near(widget: tk.Widget, window: tk.Toplevel, pad: tuple[int,int]=(12, 8)) -> None:
    window.update_idletasks()
    try:
        wx, wy, ww = widget.winfo_rootx(), widget.winfo_rooty(), widget.winfo_width()
    except Exception:
        root = window.master; root.update_idletasks()
        rx, ry, rw = root.winfo_rootx(), root.winfo_rooty(), root.winfo_width()
        wx, wy, ww = rx + rw, ry, 0
    W = window.winfo_width()
    x = int(wx + ww - W - pad[0]); y = int(wy + pad[1])
    window.geometry(f"+{max(0,x)}+{max(0,y)}")

def open_profile_window(root: tk.Tk, app, on_change=None, near_widget: tk.Widget | None = None) -> None:
    global _PROFILE_WIN_REF
    if _PROFILE_WIN_REF and _PROFILE_WIN_REF.winfo_exists():
        _PROFILE_WIN_REF.deiconify(); _PROFILE_WIN_REF.lift(); _PROFILE_WIN_REF.focus_force()
    else:
        prof = load_profile()
        _PROFILE_WIN_REF = ProfileWindow(root, app, prof, on_change=on_change)
    if near_widget is not None:
        _position_near(near_widget, _PROFILE_WIN_REF)

def attach_profile(root: tk.Tk, app, title_prefix: str = "Posture Pomodoro Timer") -> UserProfile:
    prof = load_profile()
    root.title(f"{title_prefix} — {prof.display_name}")

    # Match panel to app theme
    try:
        PANEL_BG = root.cget("bg")
    except Exception:
        PANEL_BG = "#EEE8C9"

    def _readable_text(bg_hex: str) -> tuple[str, str, str]:
        h = bg_hex.lstrip("#")
        if len(h) == 3: h = "".join(ch * 2 for ch in h)
        try:
            r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
            lum = 0.2126*(r/255)**2.2 + 0.7152*(g/255)**2.2 + 0.0722*(b/255)**2.2
        except Exception:
            lum = 1.0
        return ("#2B2B2B", "#6E6E6E", "#B7A98A") if lum > 0.5 else ("#EDEFF2", "#C8CFD9", "#96A0AE")

    TXT, SUBTXT, STROKE = _readable_text(PANEL_BG)

    name_var = tk.StringVar(value=prof.display_name)
    mins_var = tk.StringVar(value=f"{prof.focus_min}/{prof.break_min} min")

    panel = tk.Frame(root, bg=PANEL_BG, bd=0, highlightthickness=0)
    panel.place(relx=1.0, rely=0.0, anchor="ne", x=-12, y=12)

    panel.columnconfigure(0, weight=0)
    panel.columnconfigure(1, weight=1)
    panel.columnconfigure(2, weight=0)

    thumb_canvas = tk.Canvas(panel, width=28, height=28, bg=PANEL_BG, highlightthickness=0)
    thumb_canvas.grid(row=0, column=0, rowspan=2, padx=(0, 8), pady=(2, 2), sticky="w")
    thumb_img = None

    name_lbl = tk.Label(panel, textvariable=name_var, font=("Segoe UI", 10, "bold"), fg=TXT, bg=PANEL_BG)
    name_lbl.grid(row=0, column=1, sticky="w")
    mins_lbl = tk.Label(panel, textvariable=mins_var, font=("Segoe UI", 9), fg=SUBTXT, bg=PANEL_BG)
    mins_lbl.grid(row=1, column=1, sticky="w")

    edit_btn = tk.Button(
        panel, text="Edit",
        command=lambda: open_profile_window(root, app, on_change=_on_change, near_widget=panel),
        cursor="hand2", font=("Segoe UI", 9, "bold"),
        bg=PANEL_BG, fg=TXT, activebackground=PANEL_BG, activeforeground=TXT,
        bd=0, highlightthickness=0, relief="flat", padx=6, pady=1
    )
    edit_btn.grid(row=0, column=2, rowspan=2, sticky="e")

    def _refresh_thumb(p: UserProfile) -> None:
        nonlocal thumb_img
        thumb_canvas.delete("all")
        if p.avatar_path and os.path.exists(p.avatar_path):
            try:
                img = tk.PhotoImage(file=p.avatar_path)
                w, h = img.width(), img.height()
                fx = max(1, w // 28); fy = max(1, h // 28)
                if fx > 1 or fy > 1: img = img.subsample(fx, fy)
                thumb_img = img
                thumb_canvas.create_image(14, 14, image=thumb_img)
                return
            except Exception:
                pass
        thumb_canvas.create_oval(4, 4, 24, 24, outline=STROKE)

    _refresh_thumb(prof)
    _apply_to_app(app, prof)

    def _on_change(p: UserProfile) -> None:
        name_var.set(p.display_name)
        mins_var.set(f"{p.focus_min}/{p.break_min} min")
        root.title(f"{title_prefix} — {p.display_name}")
        _apply_to_app(app, p)
        _refresh_thumb(p)

    def _open_from_panel(_evt=None):
        open_profile_window(root, app, on_change=_on_change, near_widget=panel)

    for w in (panel, name_lbl, mins_lbl, thumb_canvas):
        w.bind("<Button-1>", _open_from_panel)
        w.configure(cursor="hand2")

    return prof
