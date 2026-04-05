"""
converter.py – Modern Unit Converter
Dark-themed desktop app built with tkinter/ttk.
"""

import tkinter as tk
from tkinter import ttk
import threading
import datetime

# ── optional requests import ───────────────────────────────────────────────
try:
    import requests as _requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ═══════════════════════════════════════════════════════════════════════════
#  THEME
# ═══════════════════════════════════════════════════════════════════════════
BG        = "#1a1a1a"
BG_CARD   = "#242424"
BG_INPUT  = "#2e2e2e"
BG_HOVER  = "#333333"
ACCENT    = "#6c8ef5"
ACCENT2   = "#a78bfa"
TEXT      = "#f0f0f0"
TEXT_DIM  = "#888888"
TEXT_RES  = "#6c8ef5"
BORDER    = "#383838"
GREEN     = "#4ade80"
YELLOW    = "#fbbf24"
RED       = "#f87171"

FONT_TITLE  = ("SF Pro Display", 22, "bold")
FONT_HEAD   = ("SF Pro Display", 15, "bold")
FONT_BODY   = ("SF Pro Text",    12)
FONT_SMALL  = ("SF Pro Text",    10)
FONT_RESULT = ("SF Pro Display", 28, "bold")
FONT_INPUT  = ("SF Pro Display", 18)

# Fallback fonts for systems without SF Pro
import tkinter.font as tkfont

def _best_font(families, size, weight="normal"):
    available = set(tkfont.families())
    for f in families:
        if f in available:
            return (f, size, weight)
    return ("Helvetica", size, weight)

def _fonts_init():
    global FONT_TITLE, FONT_HEAD, FONT_BODY, FONT_SMALL, FONT_RESULT, FONT_INPUT
    SF   = ["SF Pro Display", "SF Pro Text", "Helvetica Neue", "Segoe UI", "Ubuntu"]
    FONT_TITLE  = _best_font(SF, 22, "bold")
    FONT_HEAD   = _best_font(SF, 15, "bold")
    FONT_BODY   = _best_font(SF, 12)
    FONT_SMALL  = _best_font(SF, 10)
    FONT_RESULT = _best_font(SF, 28, "bold")
    FONT_INPUT  = _best_font(SF, 18)


# ═══════════════════════════════════════════════════════════════════════════
#  CONVERSION LOGIC
# ═══════════════════════════════════════════════════════════════════════════

class LengthConverter:
    units = ["mm", "cm", "m", "km", "inch", "foot", "mile"]
    to_m  = {"mm":1e-3,"cm":1e-2,"m":1,"km":1e3,
              "inch":0.0254,"foot":0.3048,"mile":1609.344}
    @staticmethod
    def convert(val, frm, to):
        return val * LengthConverter.to_m[frm] / LengthConverter.to_m[to]

class MassConverter:
    units = ["mg","g","kg","t","oz","lb"]
    to_kg = {"mg":1e-6,"g":1e-3,"kg":1,"t":1e3,
              "oz":0.0283495,"lb":0.453592}
    @staticmethod
    def convert(val, frm, to):
        return val * MassConverter.to_kg[frm] / MassConverter.to_kg[to]

class AreaConverter:
    units = ["mm²","cm²","m²","km²","hectare","acre"]
    to_m2 = {"mm²":1e-6,"cm²":1e-4,"m²":1,"km²":1e6,
              "hectare":1e4,"acre":4046.856}
    @staticmethod
    def convert(val, frm, to):
        return val * AreaConverter.to_m2[frm] / AreaConverter.to_m2[to]

class TimeConverter:
    units = ["ms","s","min","h","day","week","year"]
    to_s  = {"ms":1e-3,"s":1,"min":60,"h":3600,
              "day":86400,"week":604800,"year":31557600}
    @staticmethod
    def convert(val, frm, to):
        return val * TimeConverter.to_s[frm] / TimeConverter.to_s[to]

class DataConverter:
    units = ["bit","byte","KB","MB","GB","TB"]
    to_b  = {"bit":0.125,"byte":1,"KB":1024,"MB":1024**2,
              "GB":1024**3,"TB":1024**4}
    @staticmethod
    def convert(val, frm, to):
        return val * DataConverter.to_b[frm] / DataConverter.to_b[to]

class VolumeConverter:
    units = ["ml","l","m³","teaspoon","cup","gallon"]
    to_l  = {"ml":1e-3,"l":1,"m³":1000,
              "teaspoon":0.00492892,"cup":0.24,"gallon":3.78541}
    @staticmethod
    def convert(val, frm, to):
        return val * VolumeConverter.to_l[frm] / VolumeConverter.to_l[to]

class SpeedConverter:
    units = ["m/s","km/h","mph","knot"]
    to_ms = {"m/s":1,"km/h":1/3.6,"mph":0.44704,"knot":0.514444}
    @staticmethod
    def convert(val, frm, to):
        return val * SpeedConverter.to_ms[frm] / SpeedConverter.to_ms[to]

class TemperatureConverter:
    units = ["°C","°F","K"]
    @staticmethod
    def convert(val, frm, to):
        if frm == to: return val
        if frm == "°C":
            c = val
        elif frm == "°F":
            c = (val - 32) * 5/9
        else:  # K
            c = val - 273.15
        if to == "°C":   return c
        if to == "°F":   return c * 9/5 + 32
        return c + 273.15

class NumberConverter:
    units = ["binary","octal","decimal","hex"]
    @staticmethod
    def convert(val_str, frm, to):
        bases = {"binary":2,"octal":8,"decimal":10,"hex":16}
        try:
            n = int(str(val_str).strip(), bases[frm])
        except Exception:
            return None
        if to == "binary":  return bin(n)[2:]
        if to == "octal":   return oct(n)[2:]
        if to == "decimal": return str(n)
        return hex(n)[2:].upper()

class BMICalculator:
    @staticmethod
    def calculate(weight_kg, height_m):
        if height_m <= 0: return None, ""
        bmi = weight_kg / (height_m ** 2)
        if bmi < 18.5:   cat = "Underweight"
        elif bmi < 25:   cat = "Normal"
        elif bmi < 30:   cat = "Overweight"
        else:            cat = "Obese"
        return round(bmi, 2), cat

class CurrencyConverter:
    CURRENCIES = ["USD","EUR","GBP","JPY","CHF","CAD","AUD","CNY","SEK","NOK"]
    STATIC_RATES = {  # fallback EUR-based
        "USD":1.08,"EUR":1.0,"GBP":0.85,"JPY":162.0,
        "CHF":0.97,"CAD":1.46,"AUD":1.64,"CNY":7.82,
        "SEK":11.3,"NOK":11.5,
    }
    def __init__(self):
        self.rates = dict(self.STATIC_RATES)
        self.base  = "EUR"
        self.status = "loading"   # loading | live | offline
        self.updated = ""

    def fetch(self, callback):
        def _run():
            if not HAS_REQUESTS:
                self.status = "offline"
                callback()
                return
            try:
                r = _requests.get(
                    "https://api.frankfurter.app/latest",
                    params={"base":"EUR",
                            "symbols":",".join(self.CURRENCIES)},
                    timeout=5
                )
                r.raise_for_status()
                data = r.json()
                self.rates = data["rates"]
                self.rates["EUR"] = 1.0
                self.base = "EUR"
                self.status = "live"
                self.updated = datetime.datetime.now().strftime("%H:%M")
            except Exception:
                self.status = "offline"
            callback()
        threading.Thread(target=_run, daemon=True).start()

    def convert(self, val, frm, to):
        eur = val / self.rates.get(frm, 1)
        return eur * self.rates.get(to, 1)


# ═══════════════════════════════════════════════════════════════════════════
#  CATEGORIES META
# ═══════════════════════════════════════════════════════════════════════════
CATEGORIES = [
    {"key":"currency",    "label":"Currency",      "icon":"💱"},
    {"key":"length",      "label":"Length",         "icon":"📏"},
    {"key":"mass",        "label":"Mass",           "icon":"⚖️"},
    {"key":"area",        "label":"Area",           "icon":"⬜"},
    {"key":"time",        "label":"Time",           "icon":"⏱️"},
    {"key":"data",        "label":"Data",           "icon":"💾"},
    {"key":"volume",      "label":"Volume",         "icon":"🧪"},
    {"key":"speed",       "label":"Speed",          "icon":"🚀"},
    {"key":"temperature", "label":"Temp",           "icon":"🌡️"},
    {"key":"number",      "label":"Numbers",        "icon":"🔢"},
    {"key":"bmi",         "label":"BMI",            "icon":"🏃"},
]


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════════════════
class ConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        _fonts_init()
        self.title("Converter")
        self.geometry("400x700")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.currency = CurrencyConverter()
        self._current_frame = None

        self._setup_styles()
        self._show_home()

        # kick off currency fetch
        self.currency.fetch(self._on_currency_loaded)

    # ── currency callback ──────────────────────────────────────────────────
    def _on_currency_loaded(self):
        self.after(0, self._refresh_currency_status)

    def _refresh_currency_status(self):
        if hasattr(self, "_currency_status_label"):
            if self.currency.status == "live":
                self._currency_status_label.config(
                    text=f"Rates updated: {self.currency.updated}",
                    foreground=GREEN)
            else:
                self._currency_status_label.config(
                    text="Offline – static rates", foreground=YELLOW)

    # ── ttk styles ─────────────────────────────────────────────────────────
    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame",        background=BG)
        style.configure("Card.TFrame",   background=BG_CARD)
        style.configure("TLabel",        background=BG,      foreground=TEXT,
                        font=FONT_BODY)
        style.configure("Title.TLabel",  background=BG,      foreground=TEXT,
                        font=FONT_TITLE)
        style.configure("Head.TLabel",   background=BG,      foreground=TEXT,
                        font=FONT_HEAD)
        style.configure("Dim.TLabel",    background=BG,      foreground=TEXT_DIM,
                        font=FONT_SMALL)
        style.configure("Res.TLabel",    background=BG,      foreground=TEXT_RES,
                        font=FONT_RESULT)
        style.configure("CardDim.TLabel",background=BG_CARD, foreground=TEXT_DIM,
                        font=FONT_SMALL)
        style.configure("CardHead.TLabel",background=BG_CARD,foreground=TEXT,
                        font=FONT_HEAD)

        # Combobox
        style.configure("TCombobox",
            fieldbackground=BG_INPUT,
            background=BG_INPUT,
            foreground=TEXT,
            selectbackground=ACCENT,
            selectforeground=TEXT,
            arrowcolor=TEXT_DIM,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER,
            font=FONT_BODY,
            padding=6,
        )
        style.map("TCombobox",
            fieldbackground=[("readonly", BG_INPUT)],
            background=[("readonly", BG_INPUT)],
        )

        # Entry
        style.configure("TEntry",
            fieldbackground=BG_INPUT,
            foreground=TEXT,
            insertcolor=TEXT,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER,
            font=FONT_INPUT,
            padding=8,
        )

        # Scrollbar
        style.configure("Vertical.TScrollbar",
            background=BG_CARD, troughcolor=BG, bordercolor=BG,
            arrowcolor=TEXT_DIM, relief="flat")

    # ── frame switching ────────────────────────────────────────────────────
    def _switch(self, new_frame):
        if self._current_frame:
            self._current_frame.destroy()
        self._current_frame = new_frame
        new_frame.pack(fill="both", expand=True)

    # ═══════════════════════════════════════════════════════════════════════
    #  HOME SCREEN
    # ═══════════════════════════════════════════════════════════════════════
    def _show_home(self):
        frame = ttk.Frame(self)

        # header
        hdr = ttk.Frame(frame)
        hdr.pack(fill="x", padx=20, pady=(24,16))
        ttk.Label(hdr, text="Converter", style="Title.TLabel").pack(side="left")

        # grid of category cards
        grid_frame = ttk.Frame(frame)
        grid_frame.pack(fill="both", expand=True, padx=16)

        cols = 3
        for i, cat in enumerate(CATEGORIES):
            r, c = divmod(i, cols)
            btn_frame = tk.Frame(grid_frame, bg=BG_CARD, cursor="hand2",
                                 highlightthickness=1,
                                 highlightbackground=BORDER)
            btn_frame.grid(row=r, column=c, padx=6, pady=6,
                           sticky="nsew", ipadx=4, ipady=12)
            grid_frame.columnconfigure(c, weight=1)

            icon_lbl = tk.Label(btn_frame, text=cat["icon"],
                                bg=BG_CARD, fg=TEXT,
                                font=(_best_font(["Segoe UI Emoji","Apple Color Emoji",
                                                  "Noto Color Emoji","Helvetica"],22)[0], 22))
            icon_lbl.pack(pady=(10,4))
            name_lbl = tk.Label(btn_frame, text=cat["label"],
                                bg=BG_CARD, fg=TEXT_DIM,
                                font=FONT_SMALL)
            name_lbl.pack(pady=(0,8))

            key = cat["key"]
            for w in (btn_frame, icon_lbl, name_lbl):
                w.bind("<Button-1>", lambda e, k=key: self._open_category(k))
                w.bind("<Enter>",    lambda e, f=btn_frame: f.config(bg="#2c2c2c"))
                w.bind("<Leave>",    lambda e, f=btn_frame: f.config(bg=BG_CARD))

        self._switch(frame)

    # ═══════════════════════════════════════════════════════════════════════
    #  CATEGORY SCREENS
    # ═══════════════════════════════════════════════════════════════════════
    def _open_category(self, key):
        if key == "bmi":
            self._show_bmi()
        elif key == "currency":
            self._show_currency()
        elif key == "number":
            self._show_generic(key, NumberConverter.units,
                               lambda v, f, t: NumberConverter.convert(v, f, t),
                               is_number=True)
        else:
            converters = {
                "length":      (LengthConverter.units,      LengthConverter.convert),
                "mass":        (MassConverter.units,         MassConverter.convert),
                "area":        (AreaConverter.units,         AreaConverter.convert),
                "time":        (TimeConverter.units,         TimeConverter.convert),
                "data":        (DataConverter.units,         DataConverter.convert),
                "volume":      (VolumeConverter.units,       VolumeConverter.convert),
                "speed":       (SpeedConverter.units,        SpeedConverter.convert),
                "temperature": (TemperatureConverter.units,  TemperatureConverter.convert),
            }
            units, fn = converters[key]
            self._show_generic(key, units, fn)

    # ── shared converter UI ────────────────────────────────────────────────
    def _show_generic(self, key, units, convert_fn, is_number=False):
        meta = next(c for c in CATEGORIES if c["key"] == key)
        frame = ttk.Frame(self)

        self._make_back_header(frame, meta["icon"] + "  " + meta["label"])

        inner = ttk.Frame(frame)
        inner.pack(fill="both", expand=True, padx=24, pady=8)

        # from dropdown
        ttk.Label(inner, text="FROM", style="Dim.TLabel").pack(anchor="w", pady=(16,4))
        from_var = tk.StringVar(value=units[0])
        from_cb  = ttk.Combobox(inner, textvariable=from_var,
                                values=units, state="readonly")
        from_cb.pack(fill="x")

        # input
        ttk.Label(inner, text="VALUE", style="Dim.TLabel").pack(anchor="w", pady=(16,4))
        entry_var = tk.StringVar()
        entry = ttk.Entry(inner, textvariable=entry_var, font=FONT_INPUT)
        entry.pack(fill="x")
        entry.focus_set()

        # to dropdown
        ttk.Label(inner, text="TO", style="Dim.TLabel").pack(anchor="w", pady=(16,4))
        to_var = tk.StringVar(value=units[1] if len(units) > 1 else units[0])
        to_cb  = ttk.Combobox(inner, textvariable=to_var,
                              values=units, state="readonly")
        to_cb.pack(fill="x")

        # result card
        res_card = tk.Frame(frame, bg=BG_CARD,
                            highlightthickness=1, highlightbackground=BORDER)
        res_card.pack(fill="x", padx=24, pady=24)
        res_lbl = tk.Label(res_card, text="—", bg=BG_CARD,
                           fg=TEXT_RES, font=FONT_RESULT,
                           wraplength=340, justify="center")
        res_lbl.pack(pady=20, padx=16)

        def _update(*_):
            raw = entry_var.get().strip()
            if not raw:
                res_lbl.config(text="—", fg=TEXT_DIM)
                return
            frm = from_var.get(); to = to_var.get()
            if is_number:
                result = convert_fn(raw, frm, to)
                if result is None:
                    res_lbl.config(text="Invalid", fg=RED)
                else:
                    res_lbl.config(
                        text=f"{result}  {to}", fg=TEXT_RES)
            else:
                try:
                    val = float(raw)
                    result = convert_fn(val, frm, to)
                    formatted = self._fmt(result)
                    res_lbl.config(
                        text=f"{formatted}  {to}", fg=TEXT_RES)
                except Exception:
                    res_lbl.config(text="Invalid", fg=RED)

        entry_var.trace_add("write", _update)
        from_var.trace_add("write", _update)
        to_var.trace_add("write",   _update)

        self._switch(frame)

    # ── currency screen ────────────────────────────────────────────────────
    def _show_currency(self):
        frame = ttk.Frame(self)
        self._make_back_header(frame, "💱  Currency")

        inner = ttk.Frame(frame)
        inner.pack(fill="both", expand=True, padx=24, pady=8)

        # status label
        if self.currency.status == "loading":
            sl_text, sl_color = "Fetching rates…", TEXT_DIM
        elif self.currency.status == "live":
            sl_text, sl_color = f"Rates updated: {self.currency.updated}", GREEN
        else:
            sl_text, sl_color = "Offline – static rates", YELLOW

        status_lbl = tk.Label(inner, text=sl_text,
                              bg=BG, fg=sl_color, font=FONT_SMALL)
        status_lbl.pack(anchor="e", pady=(4,0))
        self._currency_status_label = status_lbl

        currencies = CurrencyConverter.CURRENCIES

        ttk.Label(inner, text="FROM", style="Dim.TLabel").pack(anchor="w", pady=(12,4))
        from_var = tk.StringVar(value="USD")
        from_cb  = ttk.Combobox(inner, textvariable=from_var,
                                values=currencies, state="readonly")
        from_cb.pack(fill="x")

        ttk.Label(inner, text="AMOUNT", style="Dim.TLabel").pack(anchor="w", pady=(16,4))
        entry_var = tk.StringVar()
        entry = ttk.Entry(inner, textvariable=entry_var, font=FONT_INPUT)
        entry.pack(fill="x")
        entry.focus_set()

        ttk.Label(inner, text="TO", style="Dim.TLabel").pack(anchor="w", pady=(16,4))
        to_var = tk.StringVar(value="EUR")
        to_cb  = ttk.Combobox(inner, textvariable=to_var,
                              values=currencies, state="readonly")
        to_cb.pack(fill="x")

        res_card = tk.Frame(frame, bg=BG_CARD,
                            highlightthickness=1, highlightbackground=BORDER)
        res_card.pack(fill="x", padx=24, pady=24)
        res_lbl = tk.Label(res_card, text="—", bg=BG_CARD,
                           fg=TEXT_RES, font=FONT_RESULT)
        res_lbl.pack(pady=20)

        def _update(*_):
            raw = entry_var.get().strip()
            if not raw:
                res_lbl.config(text="—", fg=TEXT_DIM); return
            frm = from_var.get(); to = to_var.get()
            try:
                val = float(raw)
                result = self.currency.convert(val, frm, to)
                res_lbl.config(text=f"{self._fmt(result)}  {to}", fg=TEXT_RES)
            except Exception:
                res_lbl.config(text="Invalid", fg=RED)

        entry_var.trace_add("write", _update)
        from_var.trace_add("write", _update)
        to_var.trace_add("write",   _update)

        self._switch(frame)

    # ── BMI screen ─────────────────────────────────────────────────────────
    def _show_bmi(self):
        frame = ttk.Frame(self)
        self._make_back_header(frame, "🏃  BMI Calculator")

        inner = ttk.Frame(frame)
        inner.pack(fill="both", expand=True, padx=24, pady=8)

        ttk.Label(inner, text="WEIGHT (kg)", style="Dim.TLabel").pack(anchor="w", pady=(16,4))
        weight_var = tk.StringVar()
        w_entry = ttk.Entry(inner, textvariable=weight_var, font=FONT_INPUT)
        w_entry.pack(fill="x")
        w_entry.focus_set()

        ttk.Label(inner, text="HEIGHT (cm)", style="Dim.TLabel").pack(anchor="w", pady=(16,4))
        height_var = tk.StringVar()
        h_entry = ttk.Entry(inner, textvariable=height_var, font=FONT_INPUT)
        h_entry.pack(fill="x")

        # result card
        res_card = tk.Frame(frame, bg=BG_CARD,
                            highlightthickness=1, highlightbackground=BORDER)
        res_card.pack(fill="x", padx=24, pady=24)
        bmi_lbl = tk.Label(res_card, text="—", bg=BG_CARD,
                           fg=TEXT_RES, font=FONT_RESULT)
        bmi_lbl.pack(pady=(20,4))
        cat_lbl = tk.Label(res_card, text="", bg=BG_CARD,
                           fg=TEXT_DIM, font=FONT_HEAD)
        cat_lbl.pack(pady=(0,20))

        # BMI scale
        scale_frame = tk.Frame(res_card, bg=BG_CARD)
        scale_frame.pack(fill="x", padx=20, pady=(0,16))
        scale_data = [
            ("< 18.5", "Underweight", "#60a5fa"),
            ("18.5–25", "Normal",     GREEN),
            ("25–30",  "Overweight",  YELLOW),
            ("> 30",   "Obese",       RED),
        ]
        for s_range, s_cat, s_color in scale_data:
            row = tk.Frame(scale_frame, bg=BG_CARD)
            row.pack(fill="x", pady=2)
            tk.Frame(row, bg=s_color, width=10, height=10).pack(side="left", padx=(0,6))
            tk.Label(row, text=f"{s_range}  {s_cat}",
                     bg=BG_CARD, fg=TEXT_DIM, font=FONT_SMALL).pack(side="left")

        cat_colors = {
            "Underweight": "#60a5fa",
            "Normal": GREEN,
            "Overweight": YELLOW,
            "Obese": RED,
        }

        def _update(*_):
            try:
                w = float(weight_var.get())
                h = float(height_var.get()) / 100.0
                bmi, cat = BMICalculator.calculate(w, h)
                if bmi is None: raise ValueError
                bmi_lbl.config(text=str(bmi), fg=cat_colors.get(cat, TEXT_RES))
                cat_lbl.config(text=cat, fg=cat_colors.get(cat, TEXT_DIM))
            except Exception:
                bmi_lbl.config(text="—", fg=TEXT_DIM)
                cat_lbl.config(text="")

        weight_var.trace_add("write", _update)
        height_var.trace_add("write", _update)

        self._switch(frame)

    # ── helpers ────────────────────────────────────────────────────────────
    def _make_back_header(self, parent, title_str):
        hdr = tk.Frame(parent, bg=BG)
        hdr.pack(fill="x", padx=16, pady=(16,4))

        back_btn = tk.Label(hdr, text="←  Back", bg=BG,
                            fg=ACCENT, font=FONT_BODY, cursor="hand2")
        back_btn.pack(side="left")
        back_btn.bind("<Button-1>", lambda e: self._show_home())
        back_btn.bind("<Enter>", lambda e: back_btn.config(fg=ACCENT2))
        back_btn.bind("<Leave>", lambda e: back_btn.config(fg=ACCENT))

        sep = tk.Frame(parent, bg=BORDER, height=1)
        sep.pack(fill="x", pady=(8,0))

        ttk.Label(parent, text=title_str, style="Head.TLabel").pack(
            anchor="w", padx=24, pady=(12,0))

    @staticmethod
    def _fmt(val):
        if val != val: return "—"
        if abs(val) < 1e-9 and val != 0:
            return f"{val:.4e}"
        if abs(val) >= 1e12:
            return f"{val:.4e}"
        if abs(val) >= 1 or val == 0:
            return f"{val:,.6g}"
        return f"{val:.8g}"


# ═══════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = ConverterApp()

    # style the combobox popdown after mainloop starts
    def _patch_combobox(*_):
        try:
            app.option_add("*TCombobox*Listbox.background",  BG_INPUT)
            app.option_add("*TCombobox*Listbox.foreground",  TEXT)
            app.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
            app.option_add("*TCombobox*Listbox.font",        FONT_BODY)
        except Exception:
            pass

    app.after(100, _patch_combobox)
    app.mainloop()
