# --- SİSTEM PARAMETRELERİ ---

import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "gizli_anahtar_degistirin_lutfen_cok_gizli_olmali_bestwork_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

AYARLAR = {
    # Bir üye kayıt olduğunda yukarı giden puanlar
    "KAYIT_PV": 100,
    "KAYIT_CV": 50.0,
    
    # Referans (Sponsor) Bonusu (Yüzdelik veya Sabit)
    # Örn: Kayıt olan kişinin CV değerinin % kaçı sponsora gitsin?
    "REFERANS_BONUS_ORANI": 0.40,  # %40 (50 CV'nin 20'si demek)
    
    # Binary Eşleşme Bonusu
    # Örn: Her 100 PV eşleştiğinde kaç CV nakit verilsin?
    "ESLESME_BONUS_MIKTARI": 10.0,
    
    # Kariyer için gereken puanlar (Geliştireceğiz)
    "KARIYER_BRONZ_PUAN": 500,
}