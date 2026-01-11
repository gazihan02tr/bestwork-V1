from app.database import engine, SessionLocal
from app import models, utils
from app.utils import get_password_hash
from datetime import datetime
from zoneinfo import ZoneInfo
import random

# 1. Veritabanını Sıfırla
print("Veritabanı tabloları siliniyor...")
models.Base.metadata.drop_all(bind=engine)
print("Tablolar yeniden oluşturuluyor...")
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

# 2. BestSoft Panel Adminini Oluştur
print("BestSoft Admin kullanıcısı oluşturuluyor...")
bestsoft_admin = models.Admin(
    kullanici_adi="bestsoft",
    sifre="123456" # Gerçek hayatta hashlenmeli ama mevcut sistemde plain text
)
db.add(bestsoft_admin)

# 3. Normal Sistem Adminini Oluştur (Ağaç Tepesi)
def generate_random_id():
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return "90" + suffix

admin_user = models.Kullanici(
    uye_no=generate_random_id(), # Rastgele ID
    tam_ad="Sistem Yöneticisi",
    email="admin@bestwork.com",
    telefon="5555555555",
    sifre=get_password_hash("123"),
    rutbe="President",
    uyelik_turu="Kurumsal",
    sol_pv=0,
    sag_pv=0,
    toplam_sol_pv=0,
    toplam_sag_pv=0,
    referans_id=None,
    parent_id=None,
    kol=None,
    kayit_tarihi=datetime.now(ZoneInfo("Europe/Istanbul"))
)
db.add(admin_user)
db.commit()

# 4. Ayarları Yükle
print("Varsayılan ayarlar yükleniyor...")
ayarlar = [
    models.Ayarlar(anahtar="kayit_pv", deger=100.0),
    models.Ayarlar(anahtar="kayit_cv", deger=50.0),
    models.Ayarlar(anahtar="referans_orani", deger=0.40),
    models.Ayarlar(anahtar="kisa_kol_oran", deger=0.13),
]
db.add_all(ayarlar)

# 5. Nesil Ayarları
nesil_ayarlari = [
    models.NesilAyari(nesil_no=1, oran=0.10),
    models.NesilAyari(nesil_no=2, oran=0.08),
    models.NesilAyari(nesil_no=3, oran=0.05),
    models.NesilAyari(nesil_no=4, oran=0.03),
    models.NesilAyari(nesil_no=5, oran=0.02),
]
db.add_all(nesil_ayarlari)

# 6. Rütbe Gereksinimleri
print("-> Varsayılan rütbe gereksinimleri oluşturuluyor...")
rutbe_gereksinimleri = [
    models.Rutbe(ad="Distribütör", sol_pv_gereksinimi=0, sag_pv_gereksinimi=0),
    models.Rutbe(ad="Platinum", sol_pv_gereksinimi=5000, sag_pv_gereksinimi=5000),
    models.Rutbe(ad="Pearl", sol_pv_gereksinimi=15000, sag_pv_gereksinimi=15000),
    models.Rutbe(ad="Sapphire", sol_pv_gereksinimi=50000, sag_pv_gereksinimi=50000),
    models.Rutbe(ad="Ruby", sol_pv_gereksinimi=100000, sag_pv_gereksinimi=100000),
    models.Rutbe(ad="Emerald", sol_pv_gereksinimi=250000, sag_pv_gereksinimi=250000),
    models.Rutbe(ad="Diamond", sol_pv_gereksinimi=500000, sag_pv_gereksinimi=500000),
    models.Rutbe(ad="Double Diamond", sol_pv_gereksinimi=1000000, sag_pv_gereksinimi=1000000),
    models.Rutbe(ad="Triple Diamond", sol_pv_gereksinimi=2500000, sag_pv_gereksinimi=2500000),
    models.Rutbe(ad="President", sol_pv_gereksinimi=5000000, sag_pv_gereksinimi=5000000),
    models.Rutbe(ad="Double President", sol_pv_gereksinimi=10000000, sag_pv_gereksinimi=10000000),
]
db.add_all(rutbe_gereksinimleri)

db.commit()
db.close()

print("✅ Kurulum Tamamlandı!")
print("---------------")
print("BestSoft Panel: bestsoft / 123456")
print("Normal Giriş: admin@bestwork.com / 123")
print("---------------")
