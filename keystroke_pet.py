import tkinter as tk
import json
import os
import time
from pynput import keyboard

IDLE_MS      = 10 * 60 * 1000  # 10 min until sleep
BANNER_MS    = 3500             # evolution banner duration
STREAK_FIRE  = "\U0001f525"     # 🔥


class KeystrokePet:

    # ── INIT ────────────────────────────────────────────────────────────────────
    def __init__(self):
        self.save_file     = "pet_stats.json"
        self.reset_job     = None
        self.idle_job      = None
        self.is_sleeping   = False
        self.current_level = 0
        self.x = self.y    = None

        self.evolutions    = self._decode()
        self.stats         = self._load_stats()
        self._update_level()

        # UI
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='#1a1a2e')

        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()

        try:
            dpi = self.root.winfo_fpixels('1i')
        except Exception:
            dpi = 96
        self.scale = max(1.0, dpi / 96.0)

        fs = int(8  * self.scale)   # small font
        fp = int(14 * self.scale)   # pet font
        ft = int(9  * self.scale)   # stats font

        self.lbl_level = tk.Label(self.root,
            text=self._level_text(), font=('Helvetica', fs, 'bold'),
            fg='#f1c40f', bg='#1a1a2e')
        self.lbl_level.pack(pady=(5, 0))

        self.lbl_pet = tk.Label(self.root,
            text=self.faces['normal'], font=('Courier', fp, 'bold'),
            fg='#4cd137', bg='#1a1a2e')
        self.lbl_pet.pack(pady=(2, 0))

        self.lbl_stats = tk.Label(self.root,
            text=self._stats_str(), font=('Helvetica', ft),
            fg='#a9b0c0', bg='#1a1a2e')
        self.lbl_stats.pack(pady=(2, 5))

        self.banner = tk.Label(self.root,
            text='', font=('Helvetica', fs, 'bold'),
            fg='#1a1a2e', bg='#9b59b6', padx=6, pady=2)
        # banner not packed until evolution fires

        for w in (self.root, self.lbl_level, self.lbl_pet, self.lbl_stats):
            w.bind('<ButtonPress-1>',   self._drag_start)
            w.bind('<ButtonRelease-1>', self._drag_stop)
            w.bind('<B1-Motion>',       self._drag_move)

        self.root.geometry(f'+{self.sw - int(220*self.scale)}'
                           f'+{self.sh - int(150*self.scale)}')
        self.root.after(150, self._fit)

        self._schedule_idle()
        self._start_listener()

    # ── EVOLUTION DATA ──────────────────────────────────────────────────────────
    # Faces hex-encoded — reading source won't spoil the surprise.
    def _decode(self):
        raw = {
            0: {
                'normal': '28 20 20 2d 5f 2d 29 20 20',
                'copy':   '28 20 2e 5f 2e 29 20 63 28',
                'paste':  '28 20 2e 5f 2e 29 3063 2661',
                'save':   '28 20 2d 5f 2d 29 7a 7a 5a 5a',
                'undo':   '28 20 20 b0 5f b0 29 20 20',
                'sleep':  '28 20 2d 5f 2d 29 7a 7a 5a 20',
            },
            1000: {
                'normal': '2f 1420 ff61 a788 ff61 141f 5c',
                'copy':   '2f 1420 20 2e 5f 2e 20 141f 5c',
                'paste':  '2f 1420 20 2661 1d55 2661 141f 5c',
                'save':   '2f 1420 20 2d 1d17 2d 20 141f 5c',
                'undo':   '2f 1420 20 2299 fe3f 2299 141f 5c',
                'sleep':  '2f 1420 20 1d17 20 2e 20 141f 5c',
            },
            2000: {
                'normal': '28 20 20 2022 1d25 2022 20 29 20 1f33f',
                'copy':   '28 20 2a 1d25 2a 20 29 20 1f33f',
                'paste':  '28 20 2661 1d25 2661 29 20 1f33f',
                'save':   '28 20 2d 1d25 2d 20 29 20 1f33f',
                'undo':   '28 20 2299 1d25 2299 29 20 1f33f',
                'sleep':  '28 20 2d 1d25 2d 20 29 20 1f33f',
            },
            3000: {
                'normal': '1f432 28 20 2d8 1d55 2d8 29',
                'copy':   '1f432 28 20 2d8 25be 2d8 29',
                'paste':  '1f432 28 20 2661 1d55 2661 29',
                'save':   '1f432 28 20 2d8 1d17 2d8 29',
                'undo':   '1f432 28 20 2299 1d55 2299 29',
                'sleep':  '1f432 28 20 2d8 1d17 2d8 29 7a 7a 5a',
            },
            4000: {
                'normal': '28 20 2d9 25bf 2d9 20 29 1f47b',
                'copy':   '28 20 2022 15dc 2022 20 29 1f47b',
                'paste':  '28 20 2661 203f 2661 20 29 1f47b',
                'save':   '28 20 1d55 203f 1d55 20 29 1f47b',
                'undo':   '28 20 2299 25bf 2299 29 1f47b',
                'sleep':  '28 20 1d17 203f 1d17 20 29 1f47b',
            },
            5000: {
                'normal': '3c8 28 20 25d5 203f 25d5 20 29 3c8',
                'copy':   '3c8 28 20 25d5 15dc 25d5 20 29 3c8',
                'paste':  '3c8 28 20 2661 203f 2661 20 29 3c8',
                'save':   '3c8 28 20 1d55 203f 1d55 20 29 3c8',
                'undo':   '3c8 28 20 2299 203f 2299 20 29 3c8',
                'sleep':  '3c8 28 20 2d8 1d17 2d8 20 29 3c8',
            },
        }
        return {
            t: {k: ''.join(chr(int(x, 16)) for x in v.split())
                for k, v in faces.items()}
            for t, faces in raw.items()
        }

    # ── STATS ───────────────────────────────────────────────────────────────────
    def _load_stats(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return {'bites_eaten': 0, 'pastes_played': 0,
                'last_active_date': '', 'streak_days': 0}

    def _save_stats(self):
        with open(self.save_file, 'w') as f:
            json.dump(self.stats, f)

    def _update_streak(self):
        today     = time.strftime('%Y-%m-%d')
        last      = self.stats.get('last_active_date', '')
        if last == today:
            return
        yesterday = time.strftime('%Y-%m-%d',
                                  time.localtime(time.time() - 86400))
        self.stats['streak_days'] = (
            self.stats.get('streak_days', 0) + 1
            if last == yesterday else 1)
        self.stats['last_active_date'] = today

    def _stats_str(self):
        total      = self.stats['bites_eaten'] + self.stats['pastes_played']
        thresholds = sorted(self.evolutions.keys())
        next_t     = next((t for t in thresholds if t > total), None)
        progress   = f'\u2192{next_t - total}' if next_t else '\u2605MAX'
        streak     = self.stats.get('streak_days', 0)
        fire       = f' {STREAK_FIRE}{streak}d' if streak >= 2 else ''
        return (f"C:{self.stats['bites_eaten']} "
                f"V:{self.stats['pastes_played']}  {progress}{fire}")

    def _level_text(self):
        return f'Lv{self.current_level}'

    def _update_level(self):
        total      = self.stats['bites_eaten'] + self.stats['pastes_played']
        thresholds = sorted(self.evolutions.keys())
        thresh, idx = 0, 0
        for i, t in enumerate(thresholds):
            if total >= t:
                thresh, idx = t, i
        self.current_level = idx
        self.faces = self.evolutions[thresh]

    # ── WINDOW FIT ──────────────────────────────────────────────────────────────
    def _fit(self):
        self.root.geometry('')            # release any fixed WxH
        self.root.update_idletasks()      # let tkinter measure content
        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()
        x = self.sw - w - int(20 * self.scale)
        y = self.sh - h - int(60 * self.scale)
        self.root.geometry(f'{w}x{h}+{x}+{y}')

    # ── DRAG ────────────────────────────────────────────────────────────────────
    def _drag_start(self, e): self.x, self.y = e.x, e.y
    def _drag_stop(self,  e): self.x = self.y = None
    def _drag_move(self,  e):
        self.root.geometry(
            f'+{self.root.winfo_x() + e.x - self.x}'
            f'+{self.root.winfo_y() + e.y - self.y}')

    # ── IDLE / SLEEP ────────────────────────────────────────────────────────────
    def _schedule_idle(self):
        if self.idle_job:
            self.root.after_cancel(self.idle_job)
        self.idle_job = self.root.after(IDLE_MS, self._sleep)

    def _sleep(self):
        self.is_sleeping = True
        self.lbl_pet.config(text=self.faces['sleep'], fg='#6c7a89')
        self.lbl_level.config(text=f'{self._level_text()} zzz', fg='#6c7a89')
        self._fit()

    def _wake(self):
        if self.is_sleeping:
            self.is_sleeping = False
            self.lbl_pet.config(text=self.faces['normal'], fg='#4cd137')
            self.lbl_level.config(text=self._level_text(), fg='#f1c40f')
            self._fit()

    # ── EVOLUTION BANNER ────────────────────────────────────────────────────────
    def _show_banner(self):
        names = {1: 'AWAKENED', 2: 'SETTLED', 3: 'EMPOWERED',
                 4: 'TRANSCENDED', 5: 'COSMIC'}
        name = names.get(self.current_level, 'EVOLVED')
        self.banner.config(
            text=f'\u2736 {name} \u2014 Lv{self.current_level} \u2736')
        self.banner.pack(pady=(0, 4))
        self._fit()
        self.root.after(BANNER_MS, self._hide_banner)

    def _hide_banner(self):
        self.banner.pack_forget()
        self._fit()

    # ── REACTIONS ───────────────────────────────────────────────────────────────
    def _react(self, face_key, stat_key=None):
        self._wake()
        self._schedule_idle()

        old_level = self.current_level

        if stat_key:
            self.stats[stat_key] += 1
            self._update_streak()
            self._save_stats()
            self._update_level()
            self.root.after(0, lambda: self.lbl_stats.config(
                text=self._stats_str()))

        if self.current_level > old_level:
            def _evolve():
                self.lbl_level.config(
                    text=f'EVOLVED! Lv{self.current_level}', fg='#9b59b6')
                self.lbl_pet.config(text=self.faces['paste'], fg='#f1c40f')
                self._fit()
                self._show_banner()
            self.root.after(0, _evolve)
        else:
            def _show(fk=face_key):
                self.lbl_pet.config(text=self.faces[fk], fg='#e94560')
                self._fit()
            self.root.after(0, _show)

        if self.reset_job:
            self.root.after_cancel(self.reset_job)
        self.reset_job = self.root.after(2000, self._reset_face)

    def _reset_face(self):
        if not self.is_sleeping:
            self.lbl_pet.config(text=self.faces['normal'], fg='#4cd137')
            self.lbl_level.config(text=self._level_text(), fg='#f1c40f')
            self._fit()

    # ── QUIT ────────────────────────────────────────────────────────────────────
    def _quit(self):
        self._save_stats()
        self.root.destroy()

    # ── LISTENER ────────────────────────────────────────────────────────────────
    def _start_listener(self):
        keyboard.GlobalHotKeys({
            '<ctrl>+c': lambda: self._react('copy',  'bites_eaten'),
            '<cmd>+c':  lambda: self._react('copy',  'bites_eaten'),
            '<ctrl>+v': lambda: self._react('paste', 'pastes_played'),
            '<cmd>+v':  lambda: self._react('paste', 'pastes_played'),
            '<ctrl>+s': lambda: self._react('save'),
            '<cmd>+s':  lambda: self._react('save'),
            '<ctrl>+z': lambda: self._react('undo'),
            '<cmd>+z':  lambda: self._react('undo'),
            '<ctrl>+q': lambda: self.root.after(0, self._quit),
            '<cmd>+q':  lambda: self.root.after(0, self._quit),
        }).start()

    # ── RUN ─────────────────────────────────────────────────────────────────────
    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    KeystrokePet().run()
