import tkinter as tk
import json
import os
from datetime import date, timedelta
from pynput import keyboard

IDLE_MS      = 10 * 60 * 1000  # 10 min until sleep
BANNER_MS    = 3500             # evolution banner duration
STREAK_FIRE  = "\U0001f525"     # 🔥


class KeystrokePet:

    # ── INIT ────────────────────────────────────────────────────────────────────
    def __init__(self):
        # Predictable save location: tied to the script's actual directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.save_file     = os.path.join(base_dir, "pet_stats.json")
        
        self.reset_job     = None
        self.idle_job      = None
        self.is_sleeping   = False
        self.current_level = 0
        self.x = self.y    = None
        self.listener      = None

        self.evolutions    = self._decode()
        self.stats         = self._load_stats()
        self._update_level()

        # UI Setup
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

        # Added padx=10 to labels to prevent text from touching the window edge
        self.lbl_level = tk.Label(self.root,
            text=self._level_text(), font=('Helvetica', fs, 'bold'),
            fg='#f1c40f', bg='#1a1a2e', padx=10)
        self.lbl_level.pack(pady=(5, 0))

        self.lbl_pet = tk.Label(self.root,
            text=self.faces['normal'], font=('Courier', fp, 'bold'),
            fg='#4cd137', bg='#1a1a2e', padx=10)
        self.lbl_pet.pack(pady=(2, 0))

        self.lbl_stats = tk.Label(self.root,
            text=self._stats_str(), font=('Helvetica', ft),
            fg='#a9b0c0', bg='#1a1a2e', padx=10)
        self.lbl_stats.pack(pady=(2, 5))

        self.banner = tk.Label(self.root,
            text='', font=('Helvetica', fs, 'bold'),
            fg='#1a1a2e', bg='#9b59b6', padx=10, pady=2)

        for w in (self.root, self.lbl_level, self.lbl_pet, self.lbl_stats):
            w.bind('<ButtonPress-1>',   self._drag_start)
            w.bind('<ButtonRelease-1>', self._drag_stop)
            w.bind('<B1-Motion>',       self._drag_move)

        # Thread-safe virtual event bindings
        self.root.bind('<<ReactCopy>>',  lambda e: self._react('copy', 'bites_eaten'))
        self.root.bind('<<ReactPaste>>', lambda e: self._react('paste', 'pastes_played'))
        self.root.bind('<<ReactSave>>',  lambda e: self._react('save'))
        self.root.bind('<<ReactUndo>>',  lambda e: self._react('undo'))
        self.root.bind('<<ReactQuit>>',  lambda e: self._quit())

        # Initial positioning
        self.root.geometry(f'+{self.sw - int(220*self.scale)}'
                           f'+{self.sh - int(150*self.scale)}')
        self.root.after(150, self._fit)

        self._schedule_idle()
        self._start_listener()

    # ── EVOLUTION DATA ──────────────────────────────────────────────────────────
    def _decode(self):
        # The progression is based on the 'Total' score (Bites + Pastes)
        raw = {
            # LEVEL 0: 0 - 999 points (The Hatchling - Classic Blob)
            0: { 
                'normal': '28 20 d2 20 2aeb 20 d2 20 29',
                'copy':   '28 20 3e 5f 3c 20 29 20 1f331',
                'paste':  '28 20 5e 5f 5e 20 29 20 266a',
                'save':   '28 20 2d 5f 2d 20 29 20 1f4a4',
                'undo':   '28 20 6f 5f 6f 20 29',
                'sleep':  '28 20 2d 5f 2d 20 29 20 7a 5a',
            },
            # LEVEL 1: 1,000 - 1,999 points (The Maru - Round & Expressive)
            1000: { 
                'normal': '28 20 2022 203f 2022 20 29',
                'copy':   '28 20 2267 203f 2267 20 29 20 1f363',
                'paste':  '28 20 ff3e 203f ff3e 20 29 20 1f3ae',
                'save':   '28 20 25e1 203f 25e1 20 29 20 2728',
                'undo':   '28 20 2299 5f 2299 20 29',
                'sleep':  '28 20 75 5f 75 20 29 20 1f4a4',
            },
            # LEVEL 2: 2,000 - 2,999 points (The Scholar)
            2000: { 
                'normal': '28 d2 d2 2d 2023 2d d2 d2 29',
                'copy':   'd2 d2 28 20 2299 5f 2299 20 29 d2 d2',
                'paste':  '2728 28 20 d2 1d55 d2 20 29 2728',
                'save':   '28 20 d2 5f d2 20 29 20 1f4d6',
                'undo':   '28 20 2299 203f 2299 20 29 20 1f4a1',
                'sleep':  '28 20 2d 5f 2d 20 29 20 1f4a4',
            },
            # LEVEL 3: 3,000 - 3,999 points (The Cyber-Drake)
            3000: { 
                'normal': '231c 28 20 d2 5f d2 20 29 231f',
                'copy':   '231c 28 20 3e 5f 3c 20 29 231f 20 1f525',
                'paste':  '231c 28 20 2a 5f 2a 20 29 231f 20 26a1',
                'save':   '231c 28 20 2d 5f 2d 20 29 231f 20 1f4be',
                'undo':   '231c 28 20 d2 203f d2 20 29 231f',
                'sleep':  '231c 28 20 2d 5f 2d 20 29 231f 20 1f4a4',
            },
            # LEVEL 4: 4,000 - 4,999 points (The Void-Walker)
            4000: { 
                'normal': '201b 203d 28 20 d2 203f d2 20 29 203d 2018',
                'copy':   '201b 203d 28 20 2299 15dc 2299 20 29 203d 2018',
                'paste':  '201b 203d 28 20 2661 203f 2661 20 29 203d 2018',
                'save':   '201b 203d 28 20 1d55 1d17 1d55 20 29 203d 2018',
                'undo':   '201b 203d 28 20 203f 203f 203f 20 29 203d 2018',
                'sleep':  '201b 203d 28 20 2d 5f 2d 20 29 203d 2018 7a 5a',
            },
            # LEVEL 5: 5,000+ points (The Star-Eater - Final Form)
        5000: { 
                'normal': '2728 1f31f 28 20 d2 1d25 d2 20 29 1f31f 2728',
                'copy':   '1f30c 28 20 2299 1d25 2299 20 29 1f30c',
                'paste':  '2728 28 20 263c 1d25 263c 20 29 2728',
                'save':   '1f31f 28 20 1d55 1d25 1d55 20 29 1f31f',
                'undo':   '2728 28 20 2299 1d25 2299 20 29 2728',
                'sleep':  '1f311 28 20 2d 1d25 2d 20 29 1f311',
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
        today = date.today().isoformat()
        last  = self.stats.get('last_active_date', '')
        if last == today:
            return
        # Robust DST-safe yesterday calculation
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        
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
        self.root.geometry('')            
        self.root.update_idletasks()      
        # Added a 12px buffer to the width to prevent ASCII cropping
        w = self.root.winfo_reqwidth() + int(12 * self.scale)
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
        # Guaranteed main-thread execution via virtual events
        self._wake()
        self._schedule_idle()

        old_level = self.current_level

        if stat_key:
            self.stats[stat_key] += 1
            self._update_streak()
            self._save_stats()
            self._update_level()
            self.lbl_stats.config(text=self._stats_str())

        if self.current_level > old_level:
            self.lbl_level.config(text=f'EVOLVED! Lv{self.current_level}', fg='#9b59b6')
            self.lbl_pet.config(text=self.faces['paste'], fg='#f1c40f')
            self._fit()
            self._show_banner()
        else:
            self.lbl_pet.config(text=self.faces[face_key], fg='#e94560')
            self._fit()

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
        if self.listener:
            self.listener.stop()
        self.root.destroy()

    # ── LISTENER ────────────────────────────────────────────────────────────────
    def _start_listener(self):
        # Pushes virtual events to avoid background-thread UI crashes
        self.listener = keyboard.GlobalHotKeys({
            '<ctrl>+c': lambda: self.root.event_generate('<<ReactCopy>>',  when='tail'),
            '<cmd>+c':  lambda: self.root.event_generate('<<ReactCopy>>',  when='tail'),
            '<ctrl>+v': lambda: self.root.event_generate('<<ReactPaste>>', when='tail'),
            '<cmd>+v':  lambda: self.root.event_generate('<<ReactPaste>>', when='tail'),
            '<ctrl>+s': lambda: self.root.event_generate('<<ReactSave>>',  when='tail'),
            '<cmd>+s':  lambda: self.root.event_generate('<<ReactSave>>',  when='tail'),
            '<ctrl>+z': lambda: self.root.event_generate('<<ReactUndo>>',  when='tail'),
            '<cmd>+z':  lambda: self.root.event_generate('<<ReactUndo>>',  when='tail'),
            '<ctrl>+[': lambda: self.root.event_generate('<<ReactQuit>>',  when='tail'),
            '<cmd>+[':  lambda: self.root.event_generate('<<ReactQuit>>',  when='tail'),
        })
        self.listener.start()

    # ── RUN ─────────────────────────────────────────────────────────────────────
    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    KeystrokePet().run()
