"""
Kalkulator Desktop (Tkinter)
Fitur : + - × ÷ , akar (√), persen (%), pangkat, kurung, π
Jalankan: python kalkulator_ringkas.py
"""

import ast
import math
import operator as op
import tkinter as tk

# ---------- Warna (tema biru) ----------
BG, DISPLAY_BG, FG = "#0D47A1", "#082F6B", "#FFFFFF"
NUM, FUNC, OP, EQ, CLR = "#1976D2", "#42A5F5", "#0288D1", "#FFC107", "#E53935"
W0, H0 = 360, 480                      # ukuran dasar (juga untuk skala font)

# Tombol: (teks, warna, aksi). Untuk angka, aksi = teks.
n = lambda x: (x, NUM, x)
ROWS = [
    [("C", CLR, "clear"), ("⌫", CLR, "back"), ("√", FUNC, "sqrt("), ("÷", OP, "/")],
    [("(", FUNC, "("), (")", FUNC, ")"), ("π", FUNC, "π"), ("^", OP, "^")],
    [n("7"), n("8"), n("9"), ("×", OP, "*")],
    [n("4"), n("5"), n("6"), ("−", OP, "-")],
    [n("1"), n("2"), n("3"), ("+", OP, "+")],
    [n("0"), n("."), ("%", FUNC, "%"), ("=", EQ, "=")],
]

# ---------- Evaluator aman (tanpa eval mentah) ----------
BINOP = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
         ast.Div: op.truediv, ast.Pow: op.pow}
UNOP = {ast.USub: op.neg, ast.UAdd: op.pos}


def evaluasi(ekspresi):
    e = ekspresi.replace("π", "pi").replace("^", "**").replace("%", "/100")
    return _eval(ast.parse(e, mode="eval").body)


def _eval(n):
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
        return n.value
    if isinstance(n, ast.Name) and n.id == "pi":
        return math.pi
    if isinstance(n, ast.UnaryOp) and type(n.op) in UNOP:
        return UNOP[type(n.op)](_eval(n.operand))
    if isinstance(n, ast.BinOp) and type(n.op) in BINOP:
        return BINOP[type(n.op)](_eval(n.left), _eval(n.right))
    if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id == "sqrt" and len(n.args) == 1):
        x = _eval(n.args[0])
        if x < 0:
            raise ValueError("Akar negatif tidak valid")
        return math.sqrt(x)
    raise ValueError("Ekspresi tidak valid")


def format_angka(x):
    if isinstance(x, float):
        x = round(x, 10)                   # buang sisa floating point
        if x == int(x) and abs(x) < 1e15:
            return str(int(x))
    return str(x)


class Kalkulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kalkulator Biru")
        self.geometry(f"{W0}x{H0}")
        self.minsize(300, 400)
        self.configure(bg=BG)

        self.ekspresi = ""
        self.baru_selesai = False          # True setelah "=" ditekan

        self._buat_layar()
        self._buat_tombol()
        self._bind_keyboard()
        self.bind("<Configure>", self._atur_font)

    # ---------- UI ----------
    def _buat_layar(self):
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="both", padx=10, pady=(10, 4))
        self.lbl_ekspresi = tk.Label(frame, bg=DISPLAY_BG, fg="#90CAF9",
                                     anchor="e", padx=10)
        self.lbl_hasil = tk.Label(frame, text="0", bg=DISPLAY_BG, fg=FG,
                                  anchor="e", padx=10, pady=8)
        for lbl in (self.lbl_ekspresi, self.lbl_hasil):
            lbl.pack(fill="x")

    def _buat_tombol(self):
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="both", expand=True, padx=8, pady=8)
        self.tombol = []
        for r, row in enumerate(ROWS):
            frame.rowconfigure(r, weight=1, uniform="baris")
            for c, (teks, warna, aksi) in enumerate(row):
                frame.columnconfigure(c, weight=1, uniform="kolom")
                b = tk.Button(frame, text=teks, bg=warna,
                              fg="#000000" if warna == EQ else FG,
                              activebackground="#64B5F6", activeforeground="#000000",
                              relief="flat", bd=0, cursor="hand2",
                              command=lambda a=aksi: self._tekan(a))
                b.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)
                self.tombol.append(b)

    def _atur_font(self, event=None):
        """Font menyesuaikan ukuran jendela (sekaligus mengatur font awal)."""
        if event is not None and event.widget is not self:
            return
        s = max(min(self.winfo_height() / H0, self.winfo_width() / W0), 0.7)
        for b in self.tombol:
            b.configure(font=("Segoe UI", int(14 * s), "bold"))
        self.lbl_hasil.configure(font=("Segoe UI", int(28 * s), "bold"))
        self.lbl_ekspresi.configure(font=("Segoe UI", max(int(12 * s), 9)))

    def _bind_keyboard(self):
        self.bind("<Key>", lambda e: e.char and e.char in "0123456789.+-*/()%^"
                  and self._tekan(e.char))
        for key, aksi in (("<Return>", "="), ("<KP_Enter>", "="),
                          ("<BackSpace>", "back"), ("<Escape>", "clear")):
            self.bind(key, lambda e, a=aksi: self._tekan(a))

    # ---------- Logika ----------
    def _tekan(self, aksi):
        if aksi == "=":
            return self._hitung()
        if aksi == "clear":
            self.ekspresi = ""
        elif aksi == "back":
            self.ekspresi = self.ekspresi[:-5 if self.ekspresi.endswith("sqrt(") else -1]
        else:
            # Setelah "=", angka baru memulai ekspresi baru;
            # operator melanjutkan hasil sebelumnya.
            if self.baru_selesai and aksi not in tuple("+-*/^%"):
                self.ekspresi = ""
            self.ekspresi += aksi
        self.baru_selesai = False
        self._perbarui_layar()

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
            teks = format_angka(evaluasi(self.ekspresi))
        except ZeroDivisionError:
            return self._error("Tidak bisa dibagi 0")
        except ValueError as ex:
            return self._error(str(ex))
        except Exception:
            return self._error("Error")
        self.lbl_ekspresi.config(text=self.lbl_ekspresi.cget("text") + " =")
        self.lbl_hasil.config(text=teks)
        self.ekspresi, self.baru_selesai = teks, True

    def _error(self, pesan):
        self.lbl_hasil.config(text=pesan)
        self.ekspresi, self.baru_selesai = "", False


if __name__ == "__main__":
    Kalkulator().mainloop()
