import os
from typing import List, Tuple

from PySide6.QtCore import QLibraryInfo
from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

RUS_ALPHABET = list("АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
ALPHABET_INDEX = {ch: i for i, ch in enumerate(RUS_ALPHABET)}


def normalize_rus(text: str) -> str:
    return "".join(ch.upper() for ch in text if ch.upper() in ALPHABET_INDEX)


def caesar(text: str, shift: int, decrypt: bool = True) -> str:
    text = normalize_rus(text)
    if decrypt:
        shift = -shift
    result = []
    n = len(RUS_ALPHABET)
    for ch in text:
        idx = (ALPHABET_INDEX[ch] + shift) % n
        result.append(RUS_ALPHABET[idx])
    return "".join(result)


def atbash(text: str) -> str:
    text = normalize_rus(text)
    n = len(RUS_ALPHABET)
    result = []
    for ch in text:
        idx = ALPHABET_INDEX[ch]
        result.append(RUS_ALPHABET[n - 1 - idx])
    return "".join(result)


def modinv(a: int, m: int) -> int:
    t, new_t = 0, 1
    r, new_r = m, a
    while new_r != 0:
        q = r // new_r
        t, new_t = new_t, t - q * new_t
        r, new_r = new_r, r - q * new_r
    if r != 1:
        raise ValueError("Нет обратимого элемента")
    if t < 0:
        t += m
    return t


def affine(text: str, a: int, b: int, decrypt: bool = True) -> str:
    text = normalize_rus(text)
    m = len(RUS_ALPHABET)
    res = []
    if decrypt:
        a_inv = modinv(a, m)
        for ch in text:
            y = ALPHABET_INDEX[ch]
            x = (a_inv * (y - b)) % m
            res.append(RUS_ALPHABET[x])
    else:
        for ch in text:
            x = ALPHABET_INDEX[ch]
            y = (a * x + b) % m
            res.append(RUS_ALPHABET[y])
    return "".join(res)


def vigenere(text: str, key: str, decrypt: bool = True) -> str:
    text = normalize_rus(text)
    key = normalize_rus(key)
    if not key:
        return ""
    res = []
    m = len(RUS_ALPHABET)
    for i, ch in enumerate(text):
        k = ALPHABET_INDEX[key[i % len(key)]]
        shift = -k if decrypt else k
        idx = (ALPHABET_INDEX[ch] + shift) % m
        res.append(RUS_ALPHABET[idx])
    return "".join(res)


def rail_fence_decode(cipher: str, rails: int) -> str:
    if rails < 2:
        return cipher
    pattern = list(range(rails)) + list(range(rails - 2, 0, -1))
    pattern_len = len(pattern)
    positions = [pattern[i % pattern_len] for i in range(len(cipher))]
    counts = [positions.count(r) for r in range(rails)]
    rail_chars = []
    idx = 0
    for c in counts:
        rail_chars.append(list(cipher[idx : idx + c]))
        idx += c
    pointers = [0] * rails
    result = []
    for pos in positions:
        result.append(rail_chars[pos][pointers[pos]])
        pointers[pos] += 1
    return "".join(result)


def rail_fence_encode(text: str, rails: int) -> str:
    if rails < 2:
        return text
    pattern = list(range(rails)) + list(range(rails - 2, 0, -1))
    pattern_len = len(pattern)
    rows = [[] for _ in range(rails)]
    for i, ch in enumerate(text):
        rows[pattern[i % pattern_len]].append(ch)
    return "".join("".join(r) for r in rows)


DEFAULT_BOOK_KEY = (
    "У лукоморья дуб зелёный;\n"
    "Златая цепь на дубе том:\n"
    "И днём и ночью кот учёный\n"
    "Всё ходит по цепи кругом;"
)


def book_decode(coords: List[Tuple[int, int]], key_text: str = DEFAULT_BOOK_KEY) -> str:
    lines = [ln.strip() for ln in key_text.split("\n") if ln.strip()]
    words_by_line = [ln.replace(";", "").replace(":", "").split() for ln in lines]
    result = []
    for line_idx, word_idx in coords:
        try:
            word = words_by_line[line_idx - 1][word_idx - 1]
            result.append(word)
        except Exception:
            result.append("?")
    return " ".join(result)


def book_find(
    word: str, key_text: str = DEFAULT_BOOK_KEY
) -> List[Tuple[int, int, str]]:
    word = word.strip()
    if not word:
        return []
    lines = [ln.strip() for ln in key_text.split("\n") if ln.strip()]
    words_by_line = [ln.replace(";", "").replace(":", "").split() for ln in lines]
    hits: List[Tuple[int, int, str]] = []
    for i, line_words in enumerate(words_by_line, start=1):
        for j, w in enumerate(line_words, start=1):
            if w.lower() == word.lower():
                hits.append((i, j, w))
    return hits


def book_encode(
    message: str, key_text: str = DEFAULT_BOOK_KEY
) -> List[Tuple[int, int]]:
    words = [w for w in message.replace(";", " ").replace(":", " ").split() if w]
    lines = [ln.strip() for ln in key_text.split("\n") if ln.strip()]
    words_by_line = [ln.replace(";", "").replace(":", "").split() for ln in lines]
    coords: List[Tuple[int, int]] = []
    for word in words:
        found = False

        for i, line_words in enumerate(words_by_line, start=1):
            for j, w in enumerate(line_words, start=1):
                if w.lower() == word.lower():
                    coords.append((i, j))
                    found = True
                    break
            if found:
                break
        if not found:
            coords.append((-1, -1))
    return coords


def parse_cycles(key: str) -> List[List[int]]:
    cycles = []
    buf = ""
    inside = False
    for ch in key:
        if ch == "(":
            inside = True
            buf = ""
        elif ch == ")":
            inside = False
            if buf:
                cycles.append([int(x) for x in buf if x.isdigit()])
        elif inside:
            buf += ch
    return cycles


def richelieu_decode(cipher: str, key: str) -> str:
    cycles = parse_cycles(key)
    idx = 0
    plain = []
    for cycle in cycles:
        block = list(cipher[idx : idx + len(cycle)])
        idx += len(cycle)
        inv = [0] * len(cycle)
        for i, cpos in enumerate(cycle):
            inv[cpos - 1] = i
        plain_block = [""] * len(cycle)
        for i, ch in enumerate(block):
            plain_block[inv[i]] = ch
        plain.extend(plain_block)
    return "".join(plain) + cipher[idx:]


def richelieu_encode(plain: str, key: str) -> str:
    cycles = parse_cycles(key)
    idx = 0
    cipher = []
    for cycle in cycles:
        block = list(plain[idx : idx + len(cycle)])
        idx += len(cycle)
        inv = [0] * len(cycle)
        for i, cpos in enumerate(cycle):
            inv[cpos - 1] = i
        cipher_block = [""] * len(cycle)
        for i, _ in enumerate(block):
            cipher_block[i] = block[inv[i]]
        cipher.extend(cipher_block)
    return "".join(cipher) + plain[idx:]


def hill_encrypt(text: str, matrix: List[List[int]], decrypt: bool = False) -> str:
    text = normalize_rus(text)
    n = len(RUS_ALPHABET)
    size = 3
    while len(text) % size != 0:
        text += "Я"
    blocks = [text[i : i + size] for i in range(0, len(text), size)]
    if decrypt:
        det = int(
            round(
                matrix[0][0]
                * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
                - matrix[0][1]
                * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
                + matrix[0][2]
                * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
            )
        )
        det_inv = modinv(det % n, n)
        adj = [
            [
                (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]),
                -(matrix[0][1] * matrix[2][2] - matrix[0][2] * matrix[2][1]),
                (matrix[0][1] * matrix[1][2] - matrix[0][2] * matrix[1][1]),
            ],
            [
                -(matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0]),
                (matrix[0][0] * matrix[2][2] - matrix[0][2] * matrix[2][0]),
                -(matrix[0][0] * matrix[1][2] - matrix[0][2] * matrix[1][0]),
            ],
            [
                (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0]),
                -(matrix[0][0] * matrix[2][1] - matrix[0][1] * matrix[2][0]),
                (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]),
            ],
        ]
        inv_m = []
        for r in range(size):
            row = []
            for c in range(size):
                row.append((adj[c][r] * det_inv) % n)
            inv_m.append(row)
        matrix = inv_m
    res = []
    for block in blocks:
        vec = [ALPHABET_INDEX[ch] for ch in block]
        out = [0] * size
        for r in range(size):
            out[r] = sum(matrix[r][c] * vec[c] for c in range(size)) % n
        res.extend(RUS_ALPHABET[x] for x in out)
    return "".join(res)


def feistel_round(left: int, right: int, subkey: int) -> Tuple[int, int]:
    f = right ^ subkey
    new_left = right
    new_right = left ^ f
    return new_left, new_right


def feistel_encrypt(values: List[int], keys: List[int], rounds: int = 2) -> List[int]:
    if len(values) != 2:
        raise ValueError("Требуются два числа")
    left, right = values
    for i in range(rounds):
        left, right = feistel_round(left, right, keys[i % len(keys)])
    return [left, right]


def feistel_decrypt(values: List[int], keys: List[int], rounds: int = 2) -> List[int]:
    if len(values) != 2:
        raise ValueError("Требуются два числа")
    left, right = values
    for i in reversed(range(rounds)):
        f = left ^ keys[i % len(keys)]
        new_right = right ^ f
        right, left = left, new_right
    return [left, right]


def diffie_hellman(g: int, p: int, a: int, b: int) -> Tuple[int, int, int]:
    A = pow(g, a, p)
    B = pow(g, b, p)
    K1 = pow(B, a, p)
    K2 = pow(A, b, p)
    if K1 != K2:
        raise ValueError("Ключи не совпали")
    return A, B, K1


def elgamal_encrypt(m: int, p: int, g: int, x: int, k: int) -> Tuple[int, int]:
    y = pow(g, x, p)
    c1 = pow(g, k, p)
    c2 = (m * pow(y, k, p)) % p
    return c1, c2


def elgamal_decrypt(c1: int, c2: int, p: int, x: int) -> int:
    s = pow(c1, x, p)
    s_inv = modinv(s, p)
    return (c2 * s_inv) % p


def rc4(key: bytes, data: bytes) -> bytes:
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    out = bytearray()
    for byte in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        k = S[(S[i] + S[j]) % 256]
        out.append(byte ^ k)
    return bytes(out)


def make_line(layout: QVBoxLayout, label: str, default: str = "") -> QLineEdit:
    row = QHBoxLayout()
    row.addWidget(QLabel(label))
    edit = QLineEdit()
    if default:
        edit.setText(default)
    row.addWidget(edit)
    layout.addLayout(row)
    return edit


def make_text(
    layout: QVBoxLayout, label: str, default: str = "", height: int = 80
) -> QTextEdit:
    layout.addWidget(QLabel(label))
    txt = QTextEdit()
    if default:
        txt.setPlainText(default)
    txt.setFixedHeight(height)
    layout.addWidget(txt)
    return txt


def make_group(title: str) -> Tuple[QGroupBox, QVBoxLayout]:
    box = QGroupBox(title)
    vbox = QVBoxLayout()
    box.setLayout(vbox)
    return box, vbox


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Крипто-практикум (вариант 3)")
        root = QVBoxLayout()
        tabs = QTabWidget()
        tabs.addTab(self.practice1_tab(), "Практика 1")
        tabs.addTab(self.practice2_tab(), "Практика 2")
        tabs.addTab(self.practice3_tab(), "Практика 3")
        tabs.addTab(self.practice4_tab(), "Практика 4")
        tabs.addTab(self.practice5_tab(), "Практика 5")
        tabs.addTab(self.practice6_tab(), "Практика 6")
        tabs.addTab(self.practice7_tab(), "Практика 7")
        tabs.addTab(self.practice13_tab(), "Практика 13")
        root.addWidget(tabs)
        self.setLayout(root)

    def practice1_tab(self):
        content = QWidget()
        layout = QVBoxLayout()

        book_box, book_layout = make_group("Книжный шифр (координаты line/word)")
        coords_entry = make_line(
            book_layout, "Координаты через запятую:", "2/8,1/4,2/1,2/3,3/5,3/8,3/3"
        )
        key_text = make_text(
            book_layout, "Текст-ключ", default=DEFAULT_BOOK_KEY, height=100
        )
        out_book = make_text(book_layout, "Результат", height=60)
        find_entry = make_line(book_layout, "Слово для поиска:", "кот")
        out_find = make_text(book_layout, "Координаты слова", height=50)
        out_letters = make_text(book_layout, "Координаты букв", height=80)
        encode_entry = make_line(book_layout, "Сообщение для шифрования:", "кот учёный")
        out_encode = make_text(book_layout, "Координаты сообщения", height=50)

        def run_book():
            coords = []
            for part in coords_entry.text().split(","):
                if "/" in part:
                    a, b = part.strip().split("/")
                    coords.append((int(a), int(b)))
            out_book.setPlainText(book_decode(coords, key_text.toPlainText()))

        def run_find():
            hits = book_find(find_entry.text(), key_text.toPlainText())
            if not hits:
                out_find.setPlainText("Не найдено")
                out_letters.setPlainText("")
            else:
                lines = [f"строка {i}, слово {j}: {w}" for i, j, w in hits]
                out_find.setPlainText("\n".join(lines))
                letters = []
                for i, j, w in hits:
                    for k, ch in enumerate(w, start=1):
                        letters.append(f"строка {i}, слово {j}, буква {k}: {ch}")
                out_letters.setPlainText("\n".join(letters))

        def run_book_encode():
            coords = book_encode(encode_entry.text(), key_text.toPlainText())
            rendered = []
            for a, b in coords:
                if a == -1:
                    rendered.append("?")
                else:
                    rendered.append(f"{a}/{b}")
            out_encode.setPlainText(", ".join(rendered))

        btn_book = QPushButton("Расшифровать")
        btn_book.clicked.connect(run_book)
        book_layout.addWidget(btn_book)

        btn_book_enc = QPushButton("Зашифровать")
        btn_book_enc.clicked.connect(run_book_encode)
        book_layout.addWidget(btn_book_enc)

        btn_find = QPushButton("Найти слово")
        btn_find.clicked.connect(run_find)
        book_layout.addWidget(btn_find)

        rail_box, rail_layout = make_group("Rail Fence (r=5)")
        rail_entry = make_line(rail_layout, "Текст:", "аемаЯн_аю_изш_деанде.деол")
        r_entry = make_line(rail_layout, "Рельсы:", "5")
        out_rail = make_text(rail_layout, "Результат", height=60)

        def run_rail():
            out_rail.setPlainText(
                rail_fence_decode(rail_entry.text(), int(r_entry.text() or 2))
            )

        btn_rail_dec = QPushButton("Расшифровать")
        btn_rail_dec.clicked.connect(run_rail)
        rail_layout.addWidget(btn_rail_dec)

        def run_rail_enc():
            out_rail.setPlainText(
                rail_fence_encode(rail_entry.text(), int(r_entry.text() or 2))
            )

        btn_rail_enc = QPushButton("Зашифровать")
        btn_rail_enc.clicked.connect(run_rail_enc)
        rail_layout.addWidget(btn_rail_enc)

        caesar_box, caesar_layout = make_group("Цезарь")
        caesar_entry = make_line(caesar_layout, "Текст:", "Мтксфретвцкб")
        caesar_key = make_line(caesar_layout, "Ключ k:", "2")
        out_caesar = make_text(caesar_layout, "Результат", height=60)

        def run_caesar():
            try:
                k = int(caesar_key.text())
            except ValueError:
                out_caesar.setPlainText("Ошибка: ключ k должен быть целым")
                return
            out_caesar.setPlainText(caesar(caesar_entry.text(), k, decrypt=True))

        btn_caesar = QPushButton("Расшифровать")
        btn_caesar.clicked.connect(run_caesar)
        caesar_layout.addWidget(btn_caesar)

        def run_caesar_enc():
            try:
                k = int(caesar_key.text())
            except ValueError:
                out_caesar.setPlainText("Ошибка: ключ k должен быть целым")
                return
            out_caesar.setPlainText(caesar(caesar_entry.text(), k, decrypt=False))

        btn_caesar_enc = QPushButton("Зашифровать")
        btn_caesar_enc.clicked.connect(run_caesar_enc)
        caesar_layout.addWidget(btn_caesar_enc)

        layout.addWidget(book_box)
        layout.addWidget(rail_box)
        layout.addWidget(caesar_box)
        layout.addStretch(1)
        content.setLayout(layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)
        return scroll

    def practice2_tab(self):
        frame = QWidget()
        layout = QVBoxLayout()

        atbash_box, atbash_layout = make_group("Атбаш")
        atbash_entry = make_line(atbash_layout, "Текст:", "Фоцпмрьоякца")
        out_atbash = make_text(atbash_layout, "Результат", height=60)

        def run_atbash():
            out_atbash.setPlainText(atbash(atbash_entry.text()))

        btn_atbash = QPushButton("Расшифровать")
        btn_atbash.clicked.connect(run_atbash)
        atbash_layout.addWidget(btn_atbash)

        btn_atbash_enc = QPushButton("Зашифровать")
        btn_atbash_enc.clicked.connect(run_atbash)
        atbash_layout.addWidget(btn_atbash_enc)

        aff_box, aff_layout = make_group("Аффинный шифр")
        aff_entry = make_line(aff_layout, "Текст:", "КЖЗЬЖ")
        a_entry = make_line(aff_layout, "a:", "5")
        b_entry = make_line(aff_layout, "b:", "3")
        out_aff = make_text(aff_layout, "Результат", height=60)

        def run_aff():
            try:
                res = affine(
                    aff_entry.text(),
                    int(a_entry.text()),
                    int(b_entry.text()),
                    decrypt=True,
                )
            except Exception as e:
                res = f"Ошибка: {e}"
            out_aff.setPlainText(res)

        btn_aff = QPushButton("Расшифровать")
        btn_aff.clicked.connect(run_aff)
        aff_layout.addWidget(btn_aff)

        def run_aff_enc():
            try:
                res = affine(
                    aff_entry.text(),
                    int(a_entry.text()),
                    int(b_entry.text()),
                    decrypt=False,
                )
            except Exception as e:
                res = f"Ошибка: {e}"
            out_aff.setPlainText(res)

        btn_aff_enc = QPushButton("Зашифровать")
        btn_aff_enc.clicked.connect(run_aff_enc)
        aff_layout.addWidget(btn_aff_enc)

        layout.addWidget(atbash_box)
        layout.addWidget(aff_box)
        layout.addStretch(1)
        frame.setLayout(layout)
        return frame

    def practice3_tab(self):
        frame = QWidget()
        layout = QVBoxLayout()

        vig_box, vig_layout = make_group("Виженер")
        vig_entry = make_line(vig_layout, "Текст:", "лудбйхще")
        vig_key = make_line(vig_layout, "Ключ:", "весна")
        out_vig = make_text(vig_layout, "Результат", height=60)

        def run_vig():
            out_vig.setPlainText(
                vigenere(vig_entry.text(), vig_key.text(), decrypt=True)
            )

        btn_vig = QPushButton("Расшифровать")
        btn_vig.clicked.connect(run_vig)
        vig_layout.addWidget(btn_vig)

        def run_vig_enc():
            out_vig.setPlainText(
                vigenere(vig_entry.text(), vig_key.text(), decrypt=False)
            )

        btn_vig_enc = QPushButton("Зашифровать")
        btn_vig_enc.clicked.connect(run_vig_enc)
        vig_layout.addWidget(btn_vig_enc)

        layout.addWidget(vig_box)
        layout.addStretch(1)
        frame.setLayout(layout)
        return frame

    def practice4_tab(self):
        frame = QWidget()
        layout = QVBoxLayout()

        ric_box, ric_layout = make_group("Ришелье (перестановка)")
        ric_entry = make_line(ric_layout, "Текст:", "_виг янк_е оан икр_")
        ric_key = make_line(ric_layout, "Ключ:", "(1342)(31542)(132)(3124)")
        out_ric = make_text(ric_layout, "Результат", height=60)

        def run_ric():
            out_ric.setPlainText(richelieu_decode(ric_entry.text(), ric_key.text()))

        btn_ric = QPushButton("Расшифровать")
        btn_ric.clicked.connect(run_ric)
        ric_layout.addWidget(btn_ric)

        def run_ric_enc():
            out_ric.setPlainText(richelieu_encode(ric_entry.text(), ric_key.text()))

        btn_ric_enc = QPushButton("Зашифровать")
        btn_ric_enc.clicked.connect(run_ric_enc)
        ric_layout.addWidget(btn_ric_enc)

        morse_box, morse_layout = make_group("Морзе")
        morse_entry = make_line(
            morse_layout,
            "Морзе:",
            ".--. .-. . -.. .-- .. ...- ..- / .-- ... . ---... / .-- .- ... / --- ... -.- --- .-. - ... .. - / .--. . ---. .- .-.. -..- -. --- .--- / - .- .--- -. -.-- / --- -... --.--",
        )
        out_morse = make_text(morse_layout, "Результат", height=60)
        MORSE_DICT = {
            ".-": "A",
            "-...": "B",
            "-.-.": "C",
            "-..": "D",
            ".": "E",
            "..-.": "F",
            "--.": "G",
            "....": "H",
            "..": "I",
            ".---": "J",
            "-.-": "K",
            ".-..": "L",
            "--": "M",
            "-.": "N",
            "---": "O",
            ".--.": "P",
            "--.-": "Q",
            ".-.": "R",
            "...": "S",
            "-": "T",
            "..-": "U",
            "...-": "V",
            ".--": "W",
            "-..-": "X",
            "-.--": "Y",
            "--..": "Z",
            "..--..": "?",
            "/": " ",
            "...---...": "SOS",
        }
        MORSE_REVERSE = {v: k for k, v in MORSE_DICT.items() if v != "/"}

        def run_morse():
            parts = morse_entry.text().split()
            res = "".join(MORSE_DICT.get(p, "?") for p in parts)
            out_morse.setPlainText(res)

        def run_morse_encode():
            text = morse_entry.text().upper()
            encoded = []
            for ch in text:
                if ch == " ":
                    encoded.append("/")
                else:
                    encoded.append(MORSE_REVERSE.get(ch, "?"))
            out_morse.setPlainText(" ".join(encoded))

        btn_morse = QPushButton("Декодировать")
        btn_morse.clicked.connect(run_morse)
        morse_layout.addWidget(btn_morse)

        btn_morse_enc = QPushButton("Кодировать")
        btn_morse_enc.clicked.connect(run_morse_encode)
        morse_layout.addWidget(btn_morse_enc)

        layout.addWidget(ric_box)
        layout.addWidget(morse_box)
        layout.addStretch(1)
        frame.setLayout(layout)
        return frame

    def practice5_tab(self):
        frame = QWidget()
        layout = QVBoxLayout()

        hill_box, hill_layout = make_group("Шифр Хилла 3x3")
        hill_entry = make_line(hill_layout, "Текст:", "МИРЭА")
        hill_mat_entry = make_line(
            hill_layout, "Матрица 3x3 (через пробелы):", "14 8 3 8 5 2 3 2 1"
        )
        out_hill = make_text(hill_layout, "Результат", height=60)

        def run_hill(enc: bool):
            nums = [int(x) for x in hill_mat_entry.text().split()]
            matrix = [nums[0:3], nums[3:6], nums[6:9]]
            res = hill_encrypt(hill_entry.text(), matrix, decrypt=not enc)
            out_hill.setPlainText(res)

        btns = QHBoxLayout()
        btn_enc = QPushButton("Зашифровать")
        btn_dec = QPushButton("Расшифровать")
        btn_enc.clicked.connect(lambda: run_hill(True))
        btn_dec.clicked.connect(lambda: run_hill(False))
        btns.addWidget(btn_enc)
        btns.addWidget(btn_dec)
        hill_layout.addLayout(btns)

        layout.addWidget(hill_box)
        layout.addStretch(1)
        frame.setLayout(layout)
        return frame

    def practice6_tab(self):
        frame = QWidget()
        layout = QVBoxLayout()

        dh_box, dh_layout = make_group("Диффи-Хеллман (вариант 3)")
        g_entry = make_line(dh_layout, "g:", "11")
        p_entry = make_line(dh_layout, "p:", "3")
        a_entry = make_line(dh_layout, "a:", "7")
        b_entry = make_line(dh_layout, "b:", "6")
        out_dh = make_text(dh_layout, "A, B, K", height=60)

        def run_dh():
            A, B, K = diffie_hellman(
                int(g_entry.text()),
                int(p_entry.text()),
                int(a_entry.text()),
                int(b_entry.text()),
            )
            out_dh.setPlainText(f"A={A}, B={B}, K={K}")

        btn_dh = QPushButton("Вычислить")
        btn_dh.clicked.connect(run_dh)
        dh_layout.addWidget(btn_dh)

        elg_box, elg_layout = make_group("ElGamal (вариант 3)")
        m_entry = make_line(elg_layout, "Сообщение m:", "6")
        p2_entry = make_line(elg_layout, "p:", "13")
        g2_entry = make_line(elg_layout, "g:", "2")
        x_entry = make_line(elg_layout, "x (секрет):", "7")
        k_entry = make_line(elg_layout, "k (сеанс):", "10")
        c1_entry = make_line(elg_layout, "c1:", "")
        c2_entry = make_line(elg_layout, "c2:", "")
        out_elg = make_text(elg_layout, "Результат", height=60)

        def run_elg_enc():
            c1, c2 = elgamal_encrypt(
                int(m_entry.text()),
                int(p2_entry.text()),
                int(g2_entry.text()),
                int(x_entry.text()),
                int(k_entry.text()),
            )
            out_elg.setPlainText(f"c1={c1}, c2={c2}")
            c1_entry.setText(str(c1))
            c2_entry.setText(str(c2))

        def run_elg_dec():
            try:
                c1 = int(c1_entry.text())
                c2 = int(c2_entry.text())
                m = elgamal_decrypt(c1, c2, int(p2_entry.text()), int(x_entry.text()))
                out_elg.setPlainText(f"m={m}")
            except Exception as e:
                out_elg.setPlainText(f"Ошибка: {e}")

        btn_elg_enc = QPushButton("Зашифровать")
        btn_elg_enc.clicked.connect(run_elg_enc)
        elg_layout.addWidget(btn_elg_enc)

        btn_elg_dec = QPushButton("Расшифровать")
        btn_elg_dec.clicked.connect(run_elg_dec)
        elg_layout.addWidget(btn_elg_dec)

        layout.addWidget(dh_box)
        layout.addWidget(elg_box)
        layout.addStretch(1)
        frame.setLayout(layout)
        return frame

    def practice7_tab(self):
        frame = QWidget()
        layout = QVBoxLayout()

        feis_box, feis_layout = make_group("Сеть Фейстеля (игровая)")
        l_entry = make_line(feis_layout, "L0:", "13")
        r_entry = make_line(feis_layout, "R0:", "1")
        key_entry = make_line(feis_layout, "Ключи через запятую:", "11,9,2,10")
        out_feis = make_text(feis_layout, "Результат", height=60)

        def run_feis(enc: bool):
            keys = [int(x) for x in key_entry.text().split(",") if x.strip()]
            vals = [int(l_entry.text()), int(r_entry.text())]
            if enc:
                res = feistel_encrypt(vals, keys, rounds=min(4, len(keys)))
            else:
                res = feistel_decrypt(vals, keys, rounds=min(4, len(keys)))
            out_feis.setPlainText(f"{res}")

        btns = QHBoxLayout()
        btn_enc = QPushButton("Шифровать")
        btn_dec = QPushButton("Дешифровать")
        btn_enc.clicked.connect(lambda: run_feis(True))
        btn_dec.clicked.connect(lambda: run_feis(False))
        btns.addWidget(btn_enc)
        btns.addWidget(btn_dec)
        feis_layout.addLayout(btns)

        layout.addWidget(feis_box)
        layout.addStretch(1)
        frame.setLayout(layout)
        return frame

    def practice13_tab(self):
        frame = QWidget()
        layout = QVBoxLayout()

        rc_box, rc_layout = make_group("RC4")
        key_entry = make_line(rc_layout, "Ключ:", "КИИБ")
        data_entry = make_line(rc_layout, "Текст:", "ЗЗНГ_ЧЫ _ЗЫГНЧЗ")
        out_rc = make_text(rc_layout, "Результат", height=60)

        def run_rc():
            key_bytes = key_entry.text().encode("utf-8")
            data_bytes = data_entry.text().encode("utf-8")
            res = rc4(key_bytes, data_bytes)
            try:
                out_rc.setPlainText(res.decode("utf-8"))
            except UnicodeDecodeError:
                out_rc.setPlainText(res.hex())

        btn_rc = QPushButton("RC4 XOR")
        btn_rc.clicked.connect(run_rc)
        rc_layout.addWidget(btn_rc)

        btn_rc_dec = QPushButton("RC4 XOR (дешифровать)")
        btn_rc_dec.clicked.connect(run_rc)
        rc_layout.addWidget(btn_rc_dec)

        layout.addWidget(rc_box)
        layout.addStretch(1)
        frame.setLayout(layout)
        return frame


def main():
    import sys

    plugins_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)
    if plugins_path and not os.environ.get("QT_QPA_PLATFORM_PLUGIN_PATH"):
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugins_path
    os.environ.setdefault("QT_QPA_PLATFORM", "cocoa")

    qt_app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(900, 700)
    window.show()
    sys.exit(qt_app.exec())


if __name__ == "__main__":
    main()
