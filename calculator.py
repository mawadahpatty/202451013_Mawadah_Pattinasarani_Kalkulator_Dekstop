"""
Kalkulator Desktop (Tkinter)
Fitur : + - x ÷ , akar (√), persen (%), sin, cos, tan, pangkat, kurung, π
Jendela: bisa diperkecil (minimize), diperbesar (maximize), ditutup (close)
Warna : biru
Jalankan: python kalkulator.py
"""

import ast
import math
import tkinter as tk
from tkinter import font as tkfont

# ---------- Warna (tema biru) ----------
BG = "#0D47A1"          # latar jendela
DISPLAY_BG = "#082F6B"  # layar
DISPLAY_FG = "#FFFFFF"
BTN_NUM = "#1976D2"     # tombol angka
BTN_FUNC = "#42A5F5"    # tombol fungsi
BTN_OP = "#0288D1"      # tombol operator
BTN_EQ = "#FFC107"      # tombol sama dengan
BTN_CLR = "#E53935"     # tombol hapus
FG = "#FFFFFF"


class Kalkulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kalkulator Biru")
        self.geometry("360x560")
        self.minsize(300, 450)          # tetap bisa diperkecil sampai ukuran ini
        self.configure(bg=BG)
        self.resizable(True, True)      # tombol minimize, maximize, close aktif

        self.ekspresi = ""
        self.mode_derajat = True        # True = DEG, False = RAD
        self.baru_selesai = False       # setelah "=" ditekan

        self._buat_layar()
        self._buat_tombol()
        self._bind_keyboard()
        self.bind("<Configure>", self._atur_font)

    # ---------- UI ----------
    def _buat_layar(self):
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="both", padx=10, pady=(10, 4))

        self.lbl_mode = tk.Label(frame, text="DEG", bg=BG, fg="#BBDEFB",
                                 anchor="w", font=("Segoe UI", 10, "bold"))
        self.lbl_mode.pack(fill="x")

        self.lbl_ekspresi = tk.Label(frame, text="", bg=DISPLAY_BG, fg="#90CAF9",
                                     anchor="e", padx=10, font=("Segoe UI", 12))
        self.lbl_ekspresi.pack(fill="x")

        self.lbl_hasil = tk.Label(frame, text="0", bg=DISPLAY_BG, fg=DISPLAY_FG,
                                  anchor="e", padx=10, pady=8,
                                  font=("Segoe UI", 28, "bold"))
        self.lbl_hasil.pack(fill="x")

    def _buat_tombol(self):
        self.frame_tombol = tk.Frame(self, bg=BG)
        self.frame_tombol.pack(fill="both", expand=True, padx=8, pady=8)

        # (teks, warna, aksi)
        baris = [
            [("DEG/RAD", BTN_FUNC, "mode"), ("C", BTN_CLR, "clear"),
             ("⌫", BTN_CLR, "back"), ("÷", BTN_OP, "/")],
            [("sin", BTN_FUNC, "sin("), ("cos", BTN_FUNC, "cos("),
             ("tan", BTN_FUNC, "tan("), ("√", BTN_FUNC, "sqrt(")],
            [("(", BTN_FUNC, "("), (")", BTN_FUNC, ")"),
             ("π", BTN_FUNC, "π"), ("^", BTN_OP, "^")],
            [("7", BTN_NUM, "7"), ("8", BTN_NUM, "8"),
             ("9", BTN_NUM, "9"), ("×", BTN_OP, "*")],
            [("4", BTN_NUM, "4"), ("5", BTN_NUM, "5"),
             ("6", BTN_NUM, "6"), ("−", BTN_OP, "-")],
            [("1", BTN_NUM, "1"), ("2", BTN_NUM, "2"),
             ("3", BTN_NUM, "3"), ("+", BTN_OP, "+")],
            [("0", BTN_NUM, "0"), (".", BTN_NUM, "."),
             ("%", BTN_FUNC, "%"), ("=", BTN_EQ, "=")],
        ]

        self.tombol = []
        for r, row in enumerate(baris):
            self.frame_tombol.rowconfigure(r, weight=1, uniform="baris")
            for c, (teks, warna, aksi) in enumerate(row):
                self.frame_tombol.columnconfigure(c, weight=1, uniform="kolom")
                fg = "#000000" if warna == BTN_EQ else FG
                b = tk.Button(
                    self.frame_tombol, text=teks, bg=warna, fg=fg,
                    activebackground="#64B5F6", activeforeground="#000000",
                    relief="flat", bd=0, cursor="hand2",
                    command=lambda a=aksi: self._tekan(a),
                )
                b.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)
                self.tombol.append(b)
                if aksi == "mode":
                    self.btn_mode = b

    def _atur_font(self, event=None):
        """Ukuran font menyesuaikan ukuran jendela (saat diperbesar/diperkecil)."""
        if event is not None and event.widget is not self:
            return
        tinggi, lebar = self.winfo_height(), self.winfo_width()
        skala = max(min(tinggi / 560, lebar / 360), 0.7)
        f_tombol = tkfont.Font(family="Segoe UI", size=int(14 * skala), weight="bold")
        for b in self.tombol:
            b.configure(font=f_tombol)
        self.lbl_hasil.configure(font=("Segoe UI", int(28 * skala), "bold"))
        self.lbl_ekspresi.configure(font=("Segoe UI", max(int(12 * skala), 9)))

    def _bind_keyboard(self):
        self.bind("<Key>", self._tombol_keyboard)
        self.bind("<Return>", lambda e: self._tekan("="))
        self.bind("<KP_Enter>", lambda e: self._tekan("="))
        self.bind("<BackSpace>", lambda e: self._tekan("back"))
        self.bind("<Escape>", lambda e: self._tekan("clear"))

    def _tombol_keyboard(self, e):
        if e.char and e.char in "0123456789.+-*/()%^":
            self._tekan(e.char)

    # ---------- Logika ----------
    def _tekan(self, aksi):
        if aksi == "clear":
            self.ekspresi = ""
            self.lbl_hasil.config(text="0")
        elif aksi == "back":
            self.ekspresi = self._hapus_terakhir(self.ekspresi)
        elif aksi == "mode":
            self.mode_derajat = not self.mode_derajat
            self.lbl_mode.config(text="DEG" if self.mode_derajat else "RAD")
        elif aksi == "=":
            self._hitung()
            return
        else:
            # Setelah "=", angka baru memulai ekspresi baru;
            # operator melanjutkan hasil sebelumnya.
            if self.baru_selesai and aksi not in ("+", "-", "*", "/", "^", "%"):
                self.ekspresi = ""
            self.ekspresi += aksi
        self.baru_selesai = False
        self._perbarui_layar()

    @staticmethod
    def _hapus_terakhir(teks):
        for fn in ("sin(", "cos(", "tan(", "sqrt("):
            if teks.endswith(fn):
                return teks[: -len(fn)]
        return teks[:-1]

    def _perbarui_layar(self):
        tampil = (self.ekspresi.replace("*", "×").replace("/", "÷")
                  .replace("sqrt(", "√("))
        self.lbl_ekspresi.config(text=tampil)
        if not self.ekspresi:
            self.lbl_hasil.config(text="0")

    def _hitung(self):
        if not self.ekspresi:
            return
        try:
            hasil = self._evaluasi(self.ekspresi)
            teks = self._format(hasil)
            self.lbl_ekspresi.config(
                text=self.lbl_ekspresi.cget("text") + " =")
            self.lbl_hasil.config(text=teks)
            self.ekspresi = teks
            self.baru_selesai = True
        except ZeroDivisionError:
            self._error("Tidak bisa dibagi 0")
        except Exception as ex:
            self._error(str(ex) if isinstance(ex, ValueError) else "Error")

    def _error(self, pesan):
        self.lbl_hasil.config(text=pesan)
        self.ekspresi = ""
        self.baru_selesai = False

    @staticmethod
    def _format(x):
        if isinstance(x, float):
            x = round(x, 10)              # sin(180) -> 0, bukan 1.2e-16
            if x == int(x) and abs(x) < 1e15:
                return str(int(x))
        return str(x)

    # ---------- Evaluator aman (tanpa eval mentah) ----------
    def _evaluasi(self, ekspresi):
        e = ekspresi.replace("π", "pi").replace("^", "**")
        e = e.replace("%", "/100")        # 50% = 0.5 ; 200+10% = 200+0.1
        pohon = ast.parse(e, mode="eval")
        return self._eval_node(pohon.body)

    def _sudut(self, x):
        return math.radians(x) if self.mode_derajat else x

    def _eval_node(self, n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.Name) and n.id == "pi":
            return math.pi
        if isinstance(n, ast.UnaryOp):
            v = self._eval_node(n.operand)
            if isinstance(n.op, ast.USub):
                return -v
            if isinstance(n.op, ast.UAdd):
                return v
        if isinstance(n, ast.BinOp):
            a, b = self._eval_node(n.left), self._eval_node(n.right)
            if isinstance(n.op, ast.Add):
                return a + b
            if isinstance(n.op, ast.Sub):
                return a - b
            if isinstance(n.op, ast.Mult):
                return a * b
            if isinstance(n.op, ast.Div):
                return a / b
            if isinstance(n.op, ast.Pow):
                return a ** b
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and len(n.args) == 1:
            x = self._eval_node(n.args[0])
            nama = n.func.id
            if nama == "sin":
                return math.sin(self._sudut(x))
            if nama == "cos":
                return math.cos(self._sudut(x))
            if nama == "tan":
                if abs(math.cos(self._sudut(x))) < 1e-12:
                    raise ValueError("tan tidak terdefinisi")
                return math.tan(self._sudut(x))
            if nama == "sqrt":
                if x < 0:
                    raise ValueError("Akar negatif tidak valid")
                return math.sqrt(x)
        raise ValueError("Ekspresi tidak valid")


if __name__ == "__main__":
    Kalkulator().mainloop()
