# decrypt_file.py
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding

def decrypt_with_tls_key(key_path: str, enc_dict: dict) -> bytes:
    """
    Decrypts a message encrypted with encrypt_with_tls_cert().
    key_path: path to PEM private key.
    enc_dict: dict with 'enc_key', 'iv', 'ciphertext' (base64-encoded).
    Returns the decrypted bytes.
    """
    with open(key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )
    # Decode parts
    enc_key = base64.b64decode(enc_dict['enc_key'])
    iv = base64.b64decode(enc_dict['iv'])
    ciphertext = base64.b64decode(enc_dict['ciphertext'])
    # Decrypt AES key
    aes_key = private_key.decrypt(
        enc_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # Decrypt message
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_msg = decryptor.update(ciphertext) + decryptor.finalize()
    # Remove padding
    unpadder = sym_padding.PKCS7(128).unpadder()
    message = unpadder.update(padded_msg) + unpadder.finalize()
    return message

