import sys
import subprocess
import os
import time

def check_installation():
    """Veritabanının kurulu olup olmadığını kontrol eder."""
    try:
        # Paketler yüklü değilse hata verebilir, bu durumda kurulu değil sayarız
        from app.database import engine
        from sqlalchemy import inspect
        inspector = inspect(engine)
        return inspector.has_table("kullanicilar")
    except ImportError:
        return False
    except Exception:
        return False

def clean_database():
    """Tüm tabloları siler."""
    print("🧹 Veritabanı temizleniyor...")
    try:
        from app.database import engine, Base
        from app import models
        Base.metadata.drop_all(bind=engine)
        print("✅ Veritabanı sıfırlandı.")
    except Exception as e:
        print(f"❌ Temizleme hatası: {e}")
        raise e

def install_dependencies():
    print("📦 Paketler yükleniyor...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Paketler başarıyla yüklendi.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Paket yükleme hatası: {e}")
        raise e

def initialize_database():
    print("🗄️ Veritabanı tabloları oluşturuluyor...")
    try:
        from app.database import engine, Base
        from app import models
        Base.metadata.create_all(bind=engine)
        print("✅ Tablolar başarıyla oluşturuldu.")
    except Exception as e:
        print(f"❌ Veritabanı hatası: {e}")
        raise e

def seed_data():
    print("🌱 Varsayılan veriler ekleniyor...")
    try:
        from app.database import SessionLocal
        from app import models
        
        db = SessionLocal()

        # 1. Kök Kullanıcı (Admin)
        admin = db.query(models.Kullanici).filter(models.Kullanici.id == 1).first()
        if not admin:
            print("   👤 Admin kullanıcısı oluşturuluyor...")
            root = models.Kullanici(
                tam_ad="BestWork Kurucu",
                email="admin@bestwork.com",
                telefon="05550001122",
                sifre="123456",
                referans_id=None,
                parent_id=None,
                kol=None,
                rutbe="Yönetici",
                uye_no="900000000",
                tc_no="11111111111",
                uyelik_turu="Kurumsal",
                ulke="Türkiye"
            )
            db.add(root)
            db.commit()
            print("   ✅ Admin oluşturuldu: admin@bestwork.com / 123456")
        else:
            print("   ℹ️ Admin kullanıcısı zaten mevcut.")

        # 2. Kategoriler
        kategoriler = [
            {"ad": "Cilt Bakımı", "aciklama": "Doğal ve etkili cilt bakım ürünleri", "resim_url": "🧴"},
            {"ad": "Vitaminler", "aciklama": "Sağlıklı yaşam destekçileri", "resim_url": "💊"},
            {"ad": "Doğal Yağlar", "aciklama": "Saf ve organik yağlar", "resim_url": "🌿"},
            {"ad": "Kozmetik", "aciklama": "Güzellik ve bakım", "resim_url": "✨"},
        ]

        for kat_data in kategoriler:
            exists = db.query(models.Kategori).filter(models.Kategori.ad == kat_data["ad"]).first()
            if not exists:
                kat = models.Kategori(**kat_data)
                db.add(kat)
                print(f"   📂 Kategori eklendi: {kat_data['ad']}")
        db.commit()

        # 3. Ürünler
        urunler = [
            {
                "ad": "Anti-Aging Krem",
                "aciklama": "Yaşlanma karşıtı, kolajen destekli özel formül.",
                "fiyat": 1250.00,
                "indirimli_fiyat": 999.00,
                "stok": 100,
                "kategori_id": 1,
                "resim_url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?q=80&w=600",
                "pv_degeri": 50
            },
            {
                "ad": "Multivitamin Complex",
                "aciklama": "Günlük enerji ihtiyacınız için 30 farklı vitamin ve mineral.",
                "fiyat": 450.00,
                "stok": 200,
                "kategori_id": 2,
                "resim_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?q=80&w=600",
                "pv_degeri": 20
            },
            {
                "ad": "Organik Argan Yağı",
                "aciklama": "Saç ve cilt için %100 saf soğuk sıkım argan yağı.",
                "fiyat": 320.00,
                "stok": 150,
                "kategori_id": 3,
                "resim_url": "https://images.unsplash.com/photo-1608248597279-f99d160bfbc8?q=80&w=600",
                "pv_degeri": 15
            },
            {
                "ad": "Nemlendirici Serum",
                "aciklama": "Hyaluronik asit içeren yoğun nemlendirici serum.",
                "fiyat": 850.00,
                "indirimli_fiyat": 699.00,
                "stok": 80,
                "kategori_id": 1,
                "resim_url": "https://images.unsplash.com/photo-1629198688000-71f23e745b6e?q=80&w=600",
                "pv_degeri": 35
            }
        ]

        # Kategori ID'lerini dinamik bulmak daha sağlıklı olur ama şimdilik varsayılan ID'ler üzerinden gidiyoruz
        # Eğer veritabanı boşsa ID'ler 1,2,3,4 diye gidecektir.
        
        for urun_data in urunler:
            exists = db.query(models.Urun).filter(models.Urun.ad == urun_data["ad"]).first()
            if not exists:
                urun = models.Urun(**urun_data)
                db.add(urun)
                print(f"   🛍️ Ürün eklendi: {urun_data['ad']}")
        
        db.commit()
        print("✅ Veriler başarıyla eklendi.")
        db.close()

    except Exception as e:
        print(f"❌ Veri ekleme hatası: {e}")
        # Hata olsa bile devam etmeyebiliriz, ama setup scripti olduğu için durması daha iyi
        raise e

def main():
    print("="*50)
    print("🚀 BestWork Kurulum Sihirbazı Başlatılıyor...")
    print("="*50)
    
    # 1. Adım: Paketler
    install_dependencies()
    print("-" * 30)
    
    # 2. Adım: Veritabanı
    initialize_database()
    print("-" * 30)
    
    # 3. Adım: Veriler
    seed_data()
    print("-" * 30)
    
    print("\n🎉 KURULUM TAMAMLANDI!")
    print("="*50)
    print("Sistemi başlatmak için şu komutu kullanın:")
    print("👉 uvicorn main:app --reload")
    print("="*50)

if __name__ == "__main__":
    main()
