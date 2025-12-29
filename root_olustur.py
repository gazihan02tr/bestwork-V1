from app.database import SessionLocal
from app import models

def kok_kullaniciyi_ekle():
    db = SessionLocal()
    
    # Daha önce eklenmiş mi kontrol et
    mevcut = db.query(models.Kullanici).first()
    if mevcut:
        print(f"Zaten bir kök kullanıcı var: {mevcut.tam_ad} (ID: {mevcut.id})")
        db.close()
        return

    # İlk kullanıcıyı (ID: 1 olacak) tanımlıyoruz
    root = models.Kullanici(
        tam_ad="BestWork Kurucu",
        email="admin@bestwork.com",
        telefon="05550001122",
        sifre="123456",  # Güvenlik için ileride hashleyeceğiz
        referans_id=None, # Onu kimse getirmedi
        parent_id=None,   # Üstünde kimse yok
        kol=None,          # Herhangi bir kolda değil
        uye_no="900000001" # İlk üye numarası
    )
    
    db.add(root)
    db.commit()
    db.refresh(root)
    print(f"✅ Kök Kullanıcı Oluşturuldu: {root.tam_ad} (ID: {root.id})")
    db.close()

if __name__ == "__main__":
    kok_kullaniciyi_ekle()