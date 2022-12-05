from io import StringIO

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from paramiko import PKey, RSAKey, DSSKey, ECDSAKey, Ed25519Key
from paramiko.ssh_exception import SSHException


def generate_key_pair():
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                        format=serialization.PrivateFormat.OpenSSH,
                                        encryption_algorithm=serialization.NoEncryption()).decode()

    public = public_key.public_bytes(encoding=serialization.Encoding.OpenSSH,
                                     format=serialization.PublicFormat.OpenSSH).decode()

    return public, private


def private_key_from_string(data: str):
    for pkey_class in (RSAKey, DSSKey, ECDSAKey, Ed25519Key):
        try:
            file_like = StringIO(data)
            pkey = pkey_class.from_private_key(file_like)
            return pkey, pkey_class
        except SSHException:
            continue

    return None, None
