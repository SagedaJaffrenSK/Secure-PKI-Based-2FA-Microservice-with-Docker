import base64
import pyotp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def decrypt_seed_logic(encrypted_seed_b64, private_key_pem):
    """Decrypts the seed using the student private key (RSA-OAEP-SHA256)."""
    priv_key = serialization.load_pem_private_key(private_key_pem, password=None)
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)
    
    # We use OAEP padding with SHA-256 as required by the task
    decrypted = priv_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted.decode('utf-8').strip()

def get_totp_token(hex_seed):
    """Generates a TOTP object from the hex seed."""
    # Convert the 64-char hex seed to base32 for the pyotp library
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
    return pyotp.TOTP(base32_seed)