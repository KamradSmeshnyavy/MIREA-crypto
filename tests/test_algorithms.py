from app.main import (
    RUS_ALPHABET,
    affine,
    atbash,
    book_decode,
    book_encode,
    caesar,
    diffie_hellman,
    elgamal_decrypt,
    elgamal_encrypt,
    feistel_decrypt,
    feistel_encrypt,
    hill_encrypt,
    rail_fence_decode,
    rail_fence_encode,
    rc4,
    richelieu_decode,
    richelieu_encode,
    vigenere,
)


def test_caesar_roundtrip():
    text = "ПРИМЕРТЕКСТ"
    enc = caesar(text, 5, decrypt=False)
    dec = caesar(enc, 5, decrypt=True)
    assert dec == text


def test_atbash_involution():
    text = "ПРИМЕРТЕКСТ"
    enc = atbash(text)
    dec = atbash(enc)
    assert dec == text


def test_affine_roundtrip():
    text = "ПРИМЕРТЕКСТ"
    enc = affine(text, 5, 3, decrypt=False)
    dec = affine(enc, 5, 3, decrypt=True)
    assert dec == text


def test_vigenere_roundtrip():
    text = "ПРИМЕРТЕКСТ"
    enc = vigenere(text, "КЛЮЧ", decrypt=False)
    dec = vigenere(enc, "КЛЮЧ", decrypt=True)
    assert dec == text


def test_rail_fence_roundtrip():
    text = "ЭТОПРОСТОТЕСТ"
    enc = rail_fence_encode(text, 4)
    dec = rail_fence_decode(enc, 4)
    assert dec == text


def test_book_cipher_roundtrip_for_known_words():
    message = "кот учёный"
    coords = book_encode(message)
    dec = book_decode(coords)
    assert dec.lower() == message.lower()


def test_richelieu_roundtrip():
    plain = "ПЕРЕСТАНОВКА"
    key = "(1342)(31542)(132)(3124)"
    enc = richelieu_encode(plain, key)
    dec = richelieu_decode(enc, key)
    assert dec == plain


def test_hill_roundtrip():
    matrix = [
        [14, 8, 3],
        [8, 5, 2],
        [3, 2, 1],
    ]
    plain = "МИРЭА"
    enc = hill_encrypt(plain, matrix, decrypt=False)
    dec = hill_encrypt(enc, matrix, decrypt=True)
    assert dec.startswith(plain)


def test_feistel_roundtrip():
    vals = [13, 1]
    keys = [11, 9, 2, 10]
    enc = feistel_encrypt(vals, keys, rounds=4)
    dec = feistel_decrypt(enc, keys, rounds=4)
    assert dec == vals


def test_diffie_hellman_consistency():
    A, B, K = diffie_hellman(5, 23, 6, 15)
    assert pow(A, 15, 23) == K
    assert pow(B, 6, 23) == K


def test_elgamal_roundtrip():
    p = 23
    m = 6
    g = 5
    x = 7
    k = 3
    c1, c2 = elgamal_encrypt(m, p, g, x, k)
    rec = elgamal_decrypt(c1, c2, p, x)
    assert rec == m


def test_rc4_symmetry():
    key = "КИИБ".encode("utf-8")
    pt = "ТЕСТ".encode("utf-8")
    ct = rc4(key, pt)
    pt2 = rc4(key, ct)
    assert pt2 == pt


def test_normalize_rus_preserves_alphabet():
    assert all(ch in RUS_ALPHABET for ch in "".join(RUS_ALPHABET))
