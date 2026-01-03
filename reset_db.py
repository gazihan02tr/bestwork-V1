from app.database import engine, SessionLocal
from app import models
from datetime import datetime
from zoneinfo import ZoneInfo
import random

def generate_random_id():
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return "90" + suffix

def reset_database():
    print("Veritabanı sıfırlanıyor...")
    
    # Tabloları sil ve yeniden oluştur
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    
    print("Tablolar oluşturuldu.")
    
    db = SessionLocal()
    
    # Yönetici Hesabı Oluştur
    admin = models.Kullanici(
        uye_no=generate_random_id(),
        tam_ad="BestWork",
        email="admin@bestwork.com",
        sifre="123",
        rutbe="Triple President",
        telefon="5555555555",
        kayit_tarihi=datetime.now(ZoneInfo("Europe/Istanbul")),
        yerlestirme_tarihi=datetime.now(ZoneInfo("Europe/Istanbul")), # Yönetici en tepede, yerleşmiş sayılır
        sol_pv=0, # Anlık Eşleşme 0
        sag_pv=0, # Anlık Eşleşme 0
        toplam_sol_pv=100000000,
        toplam_sag_pv=100000000,
        toplam_cv=0.0
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print(f"Yönetici oluşturuldu: {admin.email} / 123 (ID: {admin.uye_no})")
    
    # Örnek Bekleyen Üyeler (Ağaca yerleşmemiş)
    bekleyen1 = models.Kullanici(
        uye_no=generate_random_id(),
        tam_ad="Ahmet Yılmaz",
        email="ahmet@test.com",
        sifre="123",
        telefon="5551112233",
        referans_id=admin.id, # Yönetici referans oldu
        parent_id=None, # Henüz yerleşmedi
        kol=None,
        kayit_tarihi=datetime.now(ZoneInfo("Europe/Istanbul"))
    )
    
    bekleyen2 = models.Kullanici(
        uye_no=generate_random_id(),
        tam_ad="Ayşe Demir",
        email="ayse@test.com",
        sifre="123",
        telefon="5554445566",
        referans_id=admin.id,
        parent_id=None,
        kol=None,
        kayit_tarihi=datetime.now(ZoneInfo("Europe/Istanbul"))
    )
    
    db.add(bekleyen1)
    db.add(bekleyen2)
    db.commit()
    
    print("Örnek bekleyen üyeler eklendi.")
    
    # Ayarları Yükle
    varsayilan_ayarlar = {
        "kayit_pv": 100.0,
        "kayit_cv": 50.0,
        "referans_orani": 0.20,
        "eslesme_kazanc": 10.0,
        "matching_orani": 0.10,
        "kisa_kol_oran": 0.13
    }

    for anahtar, deger in varsayilan_ayarlar.items():
        db.add(models.Ayarlar(anahtar=anahtar, deger=deger))
    
    db.commit()
    print("Varsayılan ayarlar yüklendi.")
    
    db.close()
    print("İşlem tamamlandı.")

if __name__ == "__main__":
    reset_database()
