# --- SİSTEM PARAMETRELERİ ---

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