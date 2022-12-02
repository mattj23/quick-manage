from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


def generate_pair():
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                        format=serialization.PrivateFormat.OpenSSH,
                                        encryption_algorithm=serialization.NoEncryption()).decode()

    public = public_key.public_bytes(encoding=serialization.Encoding.OpenSSH,
                                     format=serialization.PublicFormat.OpenSSH).decode()

    return public, private

