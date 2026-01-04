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

    # Kategoriler ve Ürünler
    print("Örnek ürünler ve kategoriler ekleniyor...")
    
    # Varsayılan Resim URL'si (Placeholder)
    DEFAULT_IMAGE_URL = "https://placehold.co/600x400?text=Urun+Resmi"
    
    kategoriler = [
        {
            "ad": "Gıda Takviyeleri",
            "aciklama": "Sağlıklı yaşam için doğal takviyeler",
            "resim_url": DEFAULT_IMAGE_URL
        },
        {
            "ad": "Kişisel Bakım",
            "aciklama": "Cilt ve vücut bakım ürünleri",
            "resim_url": DEFAULT_IMAGE_URL
        },
        {
            "ad": "İçecekler",
            "aciklama": "Enerji ve sağlık içecekleri",
            "resim_url": DEFAULT_IMAGE_URL
        }
    ]

    db_kategoriler = []
    for kat_data in kategoriler:
        kategori = models.Kategori(**kat_data)
        db.add(kategori)
        db.commit()
        db.refresh(kategori)
        db_kategoriler.append(kategori)
        print(f"Kategori eklendi: {kategori.ad}")

    # Ürünler
    urunler = [
        # Gıda Takviyeleri
        {
            "ad": "Omega 3 Balık Yağı",
            "aciklama": "Yüksek EPA ve DHA içeren balık yağı takviyesi.",
            "fiyat": 450.0,
            "indirimli_fiyat": 399.0,
            "stok": 100,
            "kategori_id": db_kategoriler[0].id,
            "resim_url": DEFAULT_IMAGE_URL,
            "pv_degeri": 25
        },
        {
            "ad": "Multivitamin Kompleks",
            "aciklama": "Günlük vitamin ve mineral ihtiyacınızı karşılar.",
            "fiyat": 350.0,
            "indirimli_fiyat": None,
            "stok": 150,
            "kategori_id": db_kategoriler[0].id,
            "resim_url": DEFAULT_IMAGE_URL,
            "pv_degeri": 20
        },
        # Kişisel Bakım
        {
            "ad": "Doğal Yüz Kremi",
            "aciklama": "Aloe vera özlü nemlendirici yüz kremi.",
            "fiyat": 250.0,
            "indirimli_fiyat": 199.0,
            "stok": 80,
            "kategori_id": db_kategoriler[1].id,
            "resim_url": DEFAULT_IMAGE_URL,
            "pv_degeri": 15
        },
        {
            "ad": "Bitkisel Şampuan",
            "aciklama": "Saç dökülmesine karşı etkili bitkisel şampuan.",
            "fiyat": 180.0,
            "indirimli_fiyat": None,
            "stok": 200,
            "kategori_id": db_kategoriler[1].id,
            "resim_url": DEFAULT_IMAGE_URL,
            "pv_degeri": 10
        },
        # İçecekler
        {
            "ad": "Detox Çayı",
            "aciklama": "Vücuttan toksin atmanıza yardımcı bitki çayı.",
            "fiyat": 120.0,
            "indirimli_fiyat": 99.0,
            "stok": 300,
            "kategori_id": db_kategoriler[2].id,
            "resim_url": DEFAULT_IMAGE_URL,
            "pv_degeri": 5
        },
        {
            "ad": "Enerji İçeceği",
            "aciklama": "Doğal kafein içeren enerji içeceği.",
            "fiyat": 45.0,
            "indirimli_fiyat": None,
            "stok": 500,
            "kategori_id": db_kategoriler[2].id,
            "resim_url": DEFAULT_IMAGE_URL,
            "pv_degeri": 2
        }
    ]

    for urun_data in urunler:
        urun = models.Urun(**urun_data)
        db.add(urun)
        print(f"Ürün eklendi: {urun.ad}")
    
    db.commit()
    
    db.close()
    print("İşlem tamamlandı.")

if __name__ == "__main__":
    reset_database()
