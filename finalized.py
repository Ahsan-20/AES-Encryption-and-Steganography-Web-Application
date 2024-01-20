from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64
import os

def pad(s):
    padder = padding.PKCS7(128).padder()
    return padder.update(s) + padder.finalize()

def unpad(s):
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(s) + unpadder.finalize()

def aes_encrypt(plaintext, key):
    if len(key) < 16:
        raise ValueError("Key must be at least 16 characters long")
    key = key.ljust(16)[:16]
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key.encode()), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_message = encryptor.update(pad(plaintext.encode())) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_message).decode()

def aes_decrypt(ciphertext, key):
    if len(key) < 16:
        raise ValueError("Key must be at least 16 characters long")
    key = key.ljust(16)[:16]
    data = base64.b64decode(ciphertext)
    iv = data[:16]
    cipher = Cipher(algorithms.AES(key.encode()), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return unpad(decryptor.update(data[16:]) + decryptor.finalize()).decode()

from PIL import Image

def encode_image(img, msg):
    length = len(msg)
    if length > 255:
        raise ValueError("Text too long to hide!")
    encoded = img.copy()
    width, height = img.size
    index = 0
    for row in range(height):
        for col in range(width):
            r, g, b = img.getpixel((col, row))
            if row == 0 and col == 0:
                asc = length
            elif index <= length:
                c = msg[index - 1] if index > 0 else ''
                asc = ord(c) if c else r
            else:
                asc = r
            encoded.putpixel((col, row), (asc, g, b))
            index += 1
    return encoded

def decode_image(img):
    width, height = img.size
    msg = ""
    index = 0
    for row in range(height):
        for col in range(width):
            r, g, b = img.getpixel((col, row))
            if row == 0 and col == 0:
                length = r
            elif index <= length:
                msg += chr(r)
            index += 1
    return msg

# Encryption key
#2sqrt534rwqscvhr
