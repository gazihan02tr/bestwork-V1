from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    # Legacy support for plain text passwords (from reset_db.py)
    if plain_password == hashed_password:
        return True
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except:
        return False

def get_password_hash(password):
    return pwd_context.hash(password)

# Rütbe Gereksinimleri
RUTBE_GEREKSINIMLERI = [
    {"ad": "Distribütör", "sol_pv": 0, "sag_pv": 0},
    {"ad": "Platinum", "sol_pv": 5000, "sag_pv": 5000},
    {"ad": "Pearl", "sol_pv": 15000, "sag_pv": 15000},
    {"ad": "Sapphire", "sol_pv": 50000, "sag_pv": 50000},
    {"ad": "Ruby", "sol_pv": 100000, "sag_pv": 100000},
    {"ad": "Emerald", "sol_pv": 250000, "sag_pv": 250000},
    {"ad": "Diamond", "sol_pv": 500000, "sag_pv": 500000},
    {"ad": "Double Diamond", "sol_pv": 1000000, "sag_pv": 1000000},
    {"ad": "Triple Diamond", "sol_pv": 2500000, "sag_pv": 2500000},
    {"ad": "President", "sol_pv": 5000000, "sag_pv": 5000000},
    {"ad": "Double President", "sol_pv": 10000000, "sag_pv": 10000000},
]
