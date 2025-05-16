from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509

import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding

def encrypt_with_tls_cert(cert_path: str, message: bytes) -> dict:
    """
    Hybrid encryption: encrypts message with AES, then AES key with RSA from cert.
    Returns a dict with base64-encoded 'enc_key', 'iv', and 'ciphertext'.
    """
    # Load the public key from the TLS certificate
    with open(cert_path, "rb") as cert_file:
        cert = x509.load_pem_x509_certificate(cert_file.read())
        public_key = cert.public_key()

    # Generate AES key and IV
    aes_key = os.urandom(32)  # AES-256
    iv = os.urandom(16)

    # Pad message for AES
    padder = sym_padding.PKCS7(128).padder()
    padded_msg = padder.update(message) + padder.finalize()

    # Encrypt message with AES
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_msg) + encryptor.finalize()

    # Encrypt AES key with RSA
    enc_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Return all parts base64 encoded for easy JSON transport
    return {
        'enc_key': base64.b64encode(enc_key).decode('utf-8'),
        'iv': base64.b64encode(iv).decode('utf-8'),
        'ciphertext': base64.b64encode(ciphertext).decode('utf-8')
    }

def decrypt_with_tls_key(key_path: str, enc_dict: dict) -> bytes:
    """
    Decrypts a message encrypted with encrypt_with_tls_cert().
    key_path: path to PEM private key.
    enc_dict: dict with 'enc_key', 'iv', 'ciphertext' (base64-encoded).
    Returns the decrypted bytes.
    """
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    # Load private key
    with open(key_path, 'rb') as key_file:
        private_key = load_pem_private_key(key_file.read(), password=None)
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

