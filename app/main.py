import os
from fastapi import FastAPI, HTTPException
from .crypto_utils import decrypt_seed_logic

app = FastAPI()

SEED_FILE = "/data/seed.txt"
PRIV_KEY_FILE = "/app/student_private.pem"

class SeedInput(BaseModel):
    encrypted_seed: str

class VerifyInput(BaseModel):
    code: str

@app.post("/decrypt-seed")
async def decrypt_seed(data: dict):
    # Use the absolute path inside the container
    key_path = "/app/student_private.pem"
    
    if not os.path.exists(key_path):
        raise HTTPException(status_code=500, detail="Private key file missing inside container")
    
    try:
        with open(key_path, "rb") as f:
            private_key_pem = f.read()
        
        # This is where we call your utility function
        decrypted_seed = decrypt_seed_logic(data["encrypted_seed"], private_key_pem)
        
        if decrypted_seed is None:
            raise HTTPException(status_code=400, detail="Decryption failed - Check padding/key match")
            
        # Store in a global or state variable for the TOTP generator
        app.state.seed = decrypted_seed
        return {"status": "Seed decrypted and stored"}
        
    except Exception as e:
        # This will print the EXACT error to your docker logs
        print(f"CRITICAL ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/generate-2fa")
async def generate_2fa():
    if not os.path.exists(SEED_FILE):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    with open(SEED_FILE, "r") as f:
        seed = f.read().strip()
    totp = get_totp_token(seed)
    return {"code": totp.now(), "valid_for": 30 - (int(time.time()) % 30)}

@app.post("/verify-2fa")
async def verify_2fa(data: VerifyInput):
    if not os.path.exists(SEED_FILE):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    with open(SEED_FILE, "r") as f:
        seed = f.read().strip()
    totp = get_totp_token(seed)
    # valid_window=1 allows ±30s tolerance
    if totp.verify(data.code, valid_window=1):
        return {"valid": True}
    return {"valid": False}