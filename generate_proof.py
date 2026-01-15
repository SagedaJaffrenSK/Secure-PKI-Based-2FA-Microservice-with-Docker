import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import subprocess

# 1. Get Commit Hash
commit_hash = subprocess.check_output(['git', 'log', '-1', '--format=%H']).decode('ascii').strip()

# 2. Load Keys
with open("student_private.pem", "rb") as f:
    student_priv = serialization.load_pem_private_key(f.read(), password=None)
with open("instructor_public.pem", "rb") as f:
    inst_pub = serialization.load_pem_public_key(f.read())

# 3. Sign Hash (RSA-PSS)
signature = student_priv.sign(
    commit_hash.encode('ascii'),
    padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
    hashes.SHA256()
)

# 4. Encrypt Signature (RSA-OAEP)
encrypted_sig = inst_pub.encrypt(
    signature,
    padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
)

print(f"\n--- SUBMISSION DATA ---")
print(f"Commit Hash: {commit_hash}")
print(f"Encrypted Signature: {base64.b64encode(encrypted_sig).decode('utf-8')}")